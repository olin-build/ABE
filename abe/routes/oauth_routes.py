import logging
import os
import time
from email.message import EmailMessage
from urllib.parse import quote_plus as url_quote_plus
from uuid import uuid4

import flask
import jwt
from flask import Blueprint, flash, redirect, render_template, request

# This is a *different* secret from the auth token, so that email tokens can't
# be used to sign in. This could also be accomplished by using the *same*
# secret, with different properties in the payload.
#
# In order to simplify credential management, this secret is derived from the
# auth token secret. The auth token and secret and the email token secret are
# never used to encrypt the same plaintext, so this shouldn't enable any
# differential cryptoanalysis.
from abe.auth import AUTH_TOKEN_SECRET, clear_auth_cookie, create_auth_token
from abe.helper_functions.email_helpers import smtp_connect
from abe.helper_functions.url_helpers import url_add_query_params
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, validators
from wtforms.validators import DataRequired, Email

SLACK_OAUTH_CLIENT_ID = os.environ.get('SLACK_OAUTH_CLIENT_ID')
SLACK_OAUTH_VALIDATION_CODE = os.environ.get('SLACK_OAUTH_VALIDATION_CODE', str(uuid4()))

profile = Blueprint('oauth', __name__)


@profile.route('/oauth/authorize')
def authorize():
    downstream_redirect_uri = request.args['redirect_uri']
    upstream_redirect_uri = request.url_root + 'oauth/slack'
    state = {
        'state': request.args.get('state'),
        'validation_code': SLACK_OAUTH_VALIDATION_CODE,
    }
    # Some OAuth servesr require exact callback URL. For these, the downstram
    # redirect_uri should be in the state. For Slack, this prevents the state
    # from being present in the callback (maybe because it is too large?), so
    # place it in the redirect instead.
    if False:
        state['redirect_uri'] = downstream_redirect_uri
    else:
        upstream_redirect_uri += '?redirect_uri=' + url_quote_plus(downstream_redirect_uri)
    email_oauth_url = url_add_query_params(
        '/oauth/send_email',
        redirect_uri=upstream_redirect_uri,
        state=flask.json.dumps(state),
    ) if request.args.get('allow_email') else None
    slack_oauth_url = url_add_query_params(
        "https://slack.com/oauth/authorize",
        client_id=SLACK_OAUTH_CLIENT_ID,
        redirect_uri=upstream_redirect_uri,
        scope='identity.basic',
        state=flask.json.dumps(state),
    )
    if not SLACK_OAUTH_CLIENT_ID:
        logging.warning("SLACK_OAUTH_CLIENT_ID isn't set")
        slack_oauth_url = "javascript:alert('Set SLACK_OAUTH_CLIENT_ID to enable this feature')"
    return render_template('login.html', slack_oauth_url=slack_oauth_url, email_oauth_url=email_oauth_url)


@profile.route('/oauth/deauthorize')
def deauthorize():
    redirect_uri = request.args.get('redirect_uri', '/oauth/authorize')
    clear_auth_cookie()
    return redirect(redirect_uri)


@profile.route('/oauth/slack')
def slack_auth():
    state = flask.json.loads(request.args['state'])
    redirect_uri = state.get('redirect_uri') or request.args['redirect_uri']
    if state['validation_code'] != SLACK_OAUTH_VALIDATION_CODE:
        redirect_uri = url_add_query_params(redirect_uri,
                                            error='access_denied',
                                            error_description='Upstream oauth service called back with invalid state'
                                            )
    elif 'error' in request.args:
        return redirect(url_add_query_params(redirect_uri, error=request.args['error']))
    else:
        redirect_uri = url_add_query_params(redirect_uri,
                                            access_token=create_auth_token(),
                                            expires_in=str(6 * 30 * 24 * 3600),  # ignored by server
                                            state=state['state'],
                                            token_type='bearer',
                                            )
    return redirect(redirect_uri)


EMAIL_TOKEN_SECRET = 'email:' + AUTH_TOKEN_SECRET


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
        logging.warning('did  validate')
        email = request.args.get('email')
        email = form.email.data
        payload = {
            'iat': int(time.time()),
            'redirect_uri': request.args.get('redirect_uri'),
            'state': request.args.get('state'),
        }
        token = jwt.encode(payload, EMAIL_TOKEN_SECRET, algorithm='HS256').decode()
        server, sent_from = smtp_connect()
        msg = EmailMessage()
        msg['Subject'] = 'Sign into ABE'
        msg['From'] = sent_from
        msg['To'] = email
        email_auth_link = url_add_query_params(request.url_root + 'oauth/email', token=token)
        msg.set_content(f"Click on {token} but really {email_auth_link}")
        server.send_message(msg)
        server.close()
        return render_template('email_sign_in.html',
                               email_sent=True, email=email, token=token, email_auth_link=email_auth_link)
    for field, errors in form.errors.items():
        for error in errors:
            flash("Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))
    return render_template('email_sign_in.html', form=form)


@profile.route('/oauth/email')
def email_auth():
    return "ok"
