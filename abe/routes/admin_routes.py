import time
from urllib.parse import quote_plus as url_quote_plus

from flask import Blueprint, flash, redirect, request, render_template, current_app, session, url_for
from itsdangerous import Signer

profile = Blueprint('admin', __name__)


def signer():
    return Signer(current_app.secret_key)


@profile.route('/login')
def login():
    # This is a roundabout way of logging in, but it exercises the same OAuth
    # flow that client apps use, so it doubles as testing that flow.
    redirect_uri = url_for('admin.login_auth')
    iat = int(time.time())
    sig = signer().sign(str(iat).encode())
    return redirect('/oauth/authorize' +
                    '?redirect_uri=' + url_quote_plus(redirect_uri) +
                    '&state=' + url_quote_plus(sig.decode()))


@profile.route('/logout')
def logout():
    session.pop('access_token', None)
    redirect_uri = 'login'
    return redirect('/oauth/deauthorize?redirect_uri=' + url_quote_plus(redirect_uri))


@profile.route('/account/info')
def login_auth():
    iat = signer().unsign(request.args['state'])
    age = int(time.time()) - int(iat)
    # Allow this many minutes to use a link. This is unlikely for sign in with
    # slack, but reasonable for email if the user comes back to it later.
    if age > 30 * 60:
        flash('This link has expired. Please try again.')
        return redirect(url_for('login'))
    session['access_token'] = request.args['access_token']
    return render_template('account.html', args=request.args, age=age)


@profile.route('/add_event')
def add_event():
    return render_template('add_event.html')


@profile.route('/add_label')
def add_label():
    return render_template('add_label.html')
