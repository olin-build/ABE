import os
import time
from urllib.parse import quote_plus as url_quote_plus

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from itsdangerous import Signer

from abe import database as db

from ..resource_models.user_resources import UserApi

OAUTH_BASE_URL = os.environ.get('OAUTH_BASE_URL', '')
OAUTH_CLIENT_ID = os.environ.get('OAUTH_CLIENT_ID')

profile = Blueprint('admin', __name__)


def signer():
    return Signer(current_app.secret_key)


@profile.route('/login')
def login():
    # This is a roundabout way of logging in, but it exercises the same OAuth
    # flow that client apps use, so it doubles as testing that flow.
    iat = int(time.time())
    sig = signer().sign(str(iat).encode())
    # create an absolute path, in case the OAuth server is a different host
    redirect_uri = request.url_root.rstrip('/') + url_for('admin.login_token')
    return redirect(OAUTH_BASE_URL.rstrip('/') +
                    url_for('oauth.authorize',
                            client_id=OAUTH_CLIENT_ID or db.App.admin_app().client_id,
                            redirect_uri=redirect_uri,
                            response_mode='query',
                            response_type='token',
                            scope='admin:apps admin:current-app',
                            state=sig.decode(),
                            ))


@profile.route('/logout')
def logout():
    "Remove the auth token from the session, and redirect to redirect_uri or to the login page."
    session.pop('access_token', None)
    redirect_uri = request.args.get('redirect_uri', url_for('admin.login'))
    return redirect('/oauth/deauthorize?redirect_uri=' + url_quote_plus(redirect_uri))


@profile.route('/login/token')
def login_token():
    "Store the auth token in the session, and redirect to redirect_uri or to the account info page."
    if 'state' in request.args and '.' in request.args['state']:
        iat = signer().unsign(request.args['state'])
        age = int(time.time()) - int(iat)
        # Allow this many minutes to use a link. This is unlikely for sign in with
        # slack, but reasonable for email if the user comes back to it later.
        if age > 30 * 60:
            flash('This link has expired. Please try again.')
            return redirect(url_for('admin.login'))
    session['access_token'] = request.args['access_token']
    return redirect(request.args.get('redirect_uri', url_for('admin.account_info')))


@profile.route('/account/info')
def account_info():
    "Display account info, for debugging."
    info = UserApi().get()
    info['access_token'] = session.get('access_token')
    info = dict(sorted(info.items()))
    return render_template('account.html', info=info)


# TODO:The following routes haven't been used in a while, to my knowledge. is it
#  okay to remove them? [ows 2018-05]

@profile.route('/add_event')
def add_event():
    return render_template('add_event.html')


@profile.route('/add_label')
def add_label():
    return render_template('add_label.html')
