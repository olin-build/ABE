import logging
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import quote_plus as url_quote_plus

import flask
import jwt
import requests
from flask import current_app as app
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from itsdangerous import BadSignature, Signer

from abe import database as db
from abe.auth import access_token_scopes, clear_auth_cookies, create_access_token, is_valid_token
from abe.helper_functions.email_helpers import send_message
from abe.helper_functions.url_helpers import url_add_fragment_params, url_add_query_params
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, validators
from wtforms.validators import DataRequired, Email

OAUTH_REQUIRES_CLIENT_ID = os.environ.get('OAUTH_REQUIRES_CLIENT_ID', False)

# These are optional so that this module can load during development and
# testing.
SLACK_CLIENT_ID = os.environ.get('SLACK_CLIENT_ID')
SLACK_CLIENT_SECRET = os.environ.get('SLACK_CLIENT_SECRET')
SLACK_TEAM_ID = os.environ.get('SLACK_TEAM_ID')

profile = Blueprint('oauth', __name__)


def sign_json(params):
    signer = Signer(app.secret_key)
    return signer.sign(flask.json.dumps(params).encode())


def unsign_json(param):
    signer = Signer(app.secret_key)
    return flask.json.loads(signer.unsign(param))


@profile.route('/oauth/authorize')
def authorize():
    # TODO: document and validate with swagger
    #
    # Validate response type now, so we can add more types later without
    # requiring bwcompat for non-compliant clients
    response_type = request.args.get('response_type', 'token')
    if response_type != 'token':
        abort(400, 'invalid response_type')
    if 'redirect_uri' not in request.args:
        abort(400, 'missing redirect_uri')

    redirect_uri = request.args['redirect_uri']
    response_mode = request.args.get('response_mode', 'fragment')

    client_id = request.args.get('client_id')
    if not client_id or client_id == '0':
        if OAUTH_REQUIRES_CLIENT_ID:
            abort(400, 'missing client_id')
        client_id = db.App.force_client(role='fallback').client_id
    app = db.App.objects(client_id=client_id).first()
    if not app:
        return abort(400, f'invalid client_id {client_id}')
    if not app.validate_redirect_uri(redirect_uri):
        return abort(400, f'invalid redirect_uri {redirect_uri}')

    callback_params = {
        'client_id': client_id,
        'response_mode': response_mode,
        'state': request.args.get('state'),
    }
    if 'nonce' in request.args:
        callback_params['nonce'] = request.args['nonce']
    # Some OAuth servers require exact callback URL. For these, the downstream
    # redirect_uri should be in the callback params. For Slack, this prevents
    # the state from being present in the callback (maybe because it is too
    # large?), so place it in the redirect instead.
    slack_client_redirect_uri = request.url_root.rstrip('/') + url_for('.slack_oauth')
    serverRequiresExactCallback = False
    if serverRequiresExactCallback:
        callback_params['redirect_uri'] = redirect_uri
    else:
        slack_client_redirect_uri += '?redirect_uri=' + url_quote_plus(redirect_uri)
    state = sign_json(callback_params)
    email_oauth_url = url_add_query_params(
        '/oauth/send_email',
        redirect_uri=redirect_uri,
        state=state,
    )
    slack_oauth_url = url_add_query_params(
        "https://slack.com/oauth/authorize",
        client_id=SLACK_CLIENT_ID,
        redirect_uri=slack_client_redirect_uri,
        scope='identity.basic,identity.email',
        state=state,
        team=SLACK_TEAM_ID,
    ) if SLACK_CLIENT_ID else None
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
    client_redirect_uri = request.args.get('redirect_uri')
    try:
        callback_params = unsign_json(request.args['state'])
    except (BadSignature, KeyError):
        msg = 'Upstream oauth service called back with invalid state'
        logging.warning(msg)
        if not client_redirect_uri:
            abort(500, msg)
        redirect_uri = url_add_query_params(client_redirect_uri,
                                            error='access_denied',
                                            error_description=msg,
                                            )
        return redirect(redirect_uri)
    client_redirect_uri = client_redirect_uri or callback_params['redirect_uri']

    if 'error' in request.args:
        redirect_uri = url_add_query_params(client_redirect_uri, error=request.args['error'])
        return redirect(redirect_uri)

    email = None
    # TODO: beef up the unit case, and make this unconditional
    if 'code' in request.args:
        code = request.args['code']
        slack_client_redirect_uri = request.url_root.rstrip('/') + url_for('.slack_oauth')
        slack_client_redirect_uri += '?redirect_uri=' + url_quote_plus(client_redirect_uri)
        response = requests.get('https://slack.com/api/oauth.access',
                                params=dict(
                                    client_id=SLACK_CLIENT_ID,
                                    client_secret=SLACK_CLIENT_SECRET,
                                    code=code,
                                    redirect_uri=slack_client_redirect_uri,
                                ))
        # TODO: turn these into calls to client_redirect_uri
        if response.status_code != 200 or not response.json().get('ok'):
            abort(500)
        slack_access_token = response.json()['access_token']
        response = requests.get('https://slack.com/api/users.identity',
                                {'token': slack_access_token})
        if response.status_code != 200 or not response.json().get('ok'):
            abort(500)
        email = response.json()['user']['email']

    token = create_access_token(
        client_id=callback_params.pop('client_id'),
        email=email,
        provider='slack',
    )
    redirect_uri = implicit_grant_uri(client_redirect_uri,
                                      access_token=token,
                                      **callback_params)
    return redirect(redirect_uri)


def implicit_grant_uri(redirect_uri, *, access_token, response_mode, state):
    add_params = url_add_fragment_params if response_mode == 'fragment' else url_add_query_params
    return add_params(redirect_uri,
                      access_token=access_token,
                      # TODO: get from token:
                      expires_in=str(6 * 30 * 24 * 3600),
                      # required because the server may have overridden the scope request:
                      scope=' '.join(access_token_scopes(access_token)),
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
            return render_template('email_login.html',
                                   email_sent=True,
                                   email=email,
                                   link_prefix=request.url_root,
                                   )
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
        email=payload['email'],
        provider='email',
    )
    redirect_uri = implicit_grant_uri(payload['redirect_uri'],
                                      access_token=access_token,
                                      **callback_params)
    return redirect(redirect_uri)


@profile.route('/oauth/introspect')
def introspect():
    """OpenID token introspection <https://tools.ietf.org/html/rfc7662>"""
    if 'token' not in request.args:
        abort(400, 'missing token')
    token = request.args['token']
    return jsonify({
        'active': is_valid_token(token),
        'scope': ' '.join(access_token_scopes(token)),
    })
