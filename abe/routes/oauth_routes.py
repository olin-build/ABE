import logging
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import quote_plus as url_quote_plus

import flask
import jwt
from flask import current_app as app
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from itsdangerous import Signer

from abe import database as db
from abe.auth import clear_auth_cookies, create_access_token
from abe.helper_functions.email_helpers import send_message
from abe.helper_functions.url_helpers import url_add_fragment_params, url_add_query_params
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, validators
from wtforms.validators import DataRequired, Email

OAUTH_REQUIRES_CLIENT_ID = os.environ.get('OAUTH_REQUIRES_CLIENT_ID')
SLACK_OAUTH_CLIENT_ID = os.environ.get('SLACK_OAUTH_CLIENT_ID')

profile = Blueprint('oauth', __name__)


def sign_json(params):
    signer = Signer(app.secret_key)
    return signer.sign(flask.json.dumps(params).encode())


def unsign_json(param):
    signer = Signer(app.secret_key)
    return flask.json.loads(signer.unsign(param))


@profile.route('/oauth/authorize')
def authorize():
    if 'response_type' not in request.args:
        abort(400, 'missing response_type')
    if request.args['response_type'] != 'token':
        abort(400, 'invalid response_type')
    if 'redirect_uri' not in request.args:
        abort(400, 'missing redirect_uri')
    if 'client_id' not in request.args and OAUTH_REQUIRES_CLIENT_ID:
        abort(400, 'missing client_id')

    redirect_uri = request.args['redirect_uri']
    response_mode = request.args.get('response_mode', 'fragment')

    app = None
    if 'client_id' in request.args:
        app = db.App.objects(client_id=request.args['client_id']).first()
        if app:
            redirect_uris = app.redirect_uris
            if app.admin:
                redirect_uris += [request.url_root, '/']
            print('check', redirect_uri, 'against', redirect_uris, 'in', app.name)
            if not any(redirect_uri.startswith(uri) for uri in redirect_uris):
                return abort(400, 'invalid redirect_uri')
        else:
            return abort(400, 'invalid client_id')

    upstream_redirect_uri = request.url_root.rstrip('/') + url_for('.slack_oauth')
    callback_params = {
        'client_id': request.args['client_id'],
        'response_mode': response_mode,
        'state': request.args.get('state'),
    }
    # Some OAuth servesr require exact callback URL. For these, the downstram
    # redirect_uri should be in the state. For Slack, this prevents the state
    # from being present in the callback (maybe because it is too large?), so
    # place it in the redirect instead.
    if False:
        callback_params['redirect_uri'] = redirect_uri
    else:
        upstream_redirect_uri += '?redirect_uri=' + url_quote_plus(redirect_uri)
    state = sign_json(callback_params)
    email_oauth_url = url_add_query_params(
        '/oauth/send_email',
        redirect_uri=redirect_uri,
        state=state,
    )
    slack_oauth_url = url_add_query_params(
        "https://slack.com/oauth/authorize",
        client_id=SLACK_OAUTH_CLIENT_ID,
        redirect_uri=upstream_redirect_uri,
        scope='identity.basic',
        state=state,
    )
    if not SLACK_OAUTH_CLIENT_ID:
        logging.warning("SLACK_OAUTH_CLIENT_ID isn't set")
        slack_oauth_url = "javascript:alert('Set SLACK_OAUTH_CLIENT_ID to enable this feature')"
    return render_template('login.html',
                           app=app,
                           email_oauth_url=email_oauth_url,
                           slack_oauth_url=slack_oauth_url,
                           )


@profile.route('/oauth/deauthorize')
def deauthorize():
    redirect_uri = request.args.get('redirect_uri', '/oauth/authorize')
    clear_auth_cookies()
    return redirect(redirect_uri)


@profile.route('/oauth/slack')
def slack_oauth():
    callback_params = unsign_json(request.args['state'])
    redirect_uri = callback_params.get('redirect_uri') or request.args['redirect_uri']
    if False:  # TODO: if unsign_json fails
        redirect_uri = url_add_query_params(redirect_uri,
                                            error='access_denied',
                                            error_description='Upstream oauth service called back with invalid state'
                                            )
    elif 'error' in request.args:
        redirect_uri = url_add_query_params(redirect_uri, error=request.args['error'])
    else:
        token = create_access_token(provider='slack', client_id=callback_params.pop('client_id'))
        redirect_uri = implicit_grant_uri(redirect_uri,
                                          access_token=token,
                                          **callback_params)
    return redirect(redirect_uri)


def implicit_grant_uri(redirect_uri, *, access_token, response_mode, state):
    add_params = url_add_fragment_params if response_mode == 'fragment' else url_add_query_params
    return add_params(redirect_uri,
                      access_token=access_token,
                      expires_in=str(6 * 30 * 24 * 3600),
                      state=state,
                      token_type='bearer',
                      )


class EmailForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        validators.Regexp(r'.+@(students\.)?olin\.edu', message="An Olin address is required")])
    submit = SubmitField('Submit')
    redirect_uri = HiddenField()
    state = HiddenField()


@profile.route('/oauth/send_email', methods=["GET", "POST"])
def auth_send_email():
    form = EmailForm(
        redirect_uri=request.args.get('redirect_uri'),
        state=request.args.get('state'),
    )
    if form.validate_on_submit():
        email = request.args.get('email')
        email = form.email.data
        payload = {
            'iat': int(time.time()),
            'email': email,
            'redirect_uri': request.args.get('redirect_uri'),
            'state': request.args.get('state'),
        }
        token = jwt.encode(payload, app.secret_key, algorithm='HS256').decode()
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Sign into ABE'
        msg['To'] = email
        email_auth_link = request.url_root.rstrip('/') + url_for('.email_auth', token=token)
        body = render_template('oauth_email_body.html', email_auth_link=email_auth_link)
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        if send_message(msg):
            return render_template('email_login.html', email_sent=True, email=email)
        else:
            flash("Failed to send email. Check the server log.")
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in the {getattr(form, field).label.text} field - {error}")
    return render_template('email_login.html', form=form)


@profile.route('/oauth/email')
def email_auth():
    payload = jwt.decode(request.args['token'].encode(), app.secret_key, algorithm='HS256')
    callback_params = unsign_json(payload['state'])
    access_token = create_access_token(
        client_id=callback_params.pop('client_id'),
        provider='email',
        email=payload['email'])
    redirect_uri = implicit_grant_uri(payload['redirect_uri'],
                                      access_token=access_token,
                                      **callback_params)
    return redirect(redirect_uri)
