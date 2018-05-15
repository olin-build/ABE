#!/usr/bin/env python3
"""Main flask app"""
import logging
import os
import urllib
from datetime import datetime
from uuid import uuid4

import flask
from flask import Flask, g, jsonify, redirect, render_template, request
from flask.json import JSONEncoder
from flask_cors import CORS
from flask_restplus import Api
from flask_sslify import SSLify  # redirect to https

from abe.helper_functions.url_helpers import url_add_query_params

from .auth import create_access_token, clear_auth_cookie
from .resource_models.account_resources import api as account_api
from .resource_models.event_resources import api as event_api
from .resource_models.ics_resources import api as ics_api
from .resource_models.label_resources import api as label_api
from .resource_models.subscription_resources import api as subscription_api

FORMAT = "%(levelname)s:ABE: 🎩 %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)

app = Flask(__name__)
CORS(app, allow_headers='Authorization', supports_credentials=True)

# Access-Control-Allow-Headers

# Redirect HTTP to HTTPS.
#
# For operational flexibility, set the HSTS max-age to a few seconds, instead
# of the on-year default. The threats mitigated by HSTS policy caching are in
# any case mostly not relevant to API services.
#
# TODO: Maybe the app should 404 non-HTTPS requests, rather than redirect them.
#
# The value of `skips` is the fixed prefix from the ACME HTTP Challenge spec
# https://ietf-wg-acme.github.io/acme/draft-ietf-acme-acme.html#rfc.section.8.3,
# used by LetsEncrypt.
#
# Use tests/tests_https_redirection.sh to test changes to this code.
#
# Disabled by default for local development. See issue #158.
if os.environ.get('HSTS_ENABLED'):
    SSLify(app, age=10, skips=['.well-known/acme-challenge/'])


@app.route('/')  # For the splash to work, needs to be declared before API
def splash():
    return render_template('splash.html')


api = Api(app, doc="/docs/", version="0.1", title="ABE API")


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return JSONEncoder.default(self, obj)


app.json_encoder = CustomJSONEncoder

# add return representations


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = jsonify(data)
    resp.status_code = code
    resp.headers.extend(headers or {})
    return resp


@app.after_request
def call_after_request_callbacks(response):  # For deferred callbacks
    for callback in getattr(g, 'after_request_callbacks', ()):
        callback(response)
    return response


# Route resources
api.add_namespace(account_api)
api.add_namespace(event_api)
api.add_namespace(label_api)
api.add_namespace(ics_api)
api.add_namespace(subscription_api)


@app.route('/add_event')
def add_event():
    return render_template('add_event.html')


@app.route('/add_label')
def add_label():
    return render_template('add_label.html')


SLACK_OAUTH_VALIDATION_CODE = os.environ.get('SLACK_OAUTH_VALIDATION_CODE', str(uuid4()))


@app.route('/oauth/authorize')
def oauth_login():
    default_redirect_uri = request.url_root + 'oauth/account'  # default for debugging
    downstream_redirect_uri = request.args.get('redirect_uri', default_redirect_uri)
    # Some OAuth servesr require exact callback URL. For these, the downstram
    # redirect_uri should be in the state. For Slack, this prevents the state
    # from being present in the callback (maybe because it is too large?), so
    # place it in the redirect instead.
    upstream_redirect_uri = request.url_root + 'oauth/slack?redirect_uri=' + \
        urllib.parse.quote_plus(downstream_redirect_uri)
    state = {
        # 'redirect_uri': downstream_redirect_uri,
        'state': request.args.get('state', None),
        'validation_code': SLACK_OAUTH_VALIDATION_CODE,
    }
    return render_template('login.html',
                           client_id=os.environ['SLACK_OAUTH_CLIENT_ID'],
                           state=flask.json.dumps(state),
                           redirect_uri=urllib.parse.quote_plus(upstream_redirect_uri)
                           )


@app.route('/auth/logout')
def logout():
    redirect_uri = request.args.get('redirect_uri', '/login')
    clear_auth_cookie()
    return redirect(redirect_uri)


@app.route('/oauth/account')
def account_info():
    return render_template('account.html', args=request.args)


@app.route('/oauth/slack')
def slack_auth():
    state = flask.json.loads(request.args['state'])
    # redirect_uri = state['redirect_uri']
    redirect_uri = request.args['redirect_uri']
    if state['validation_code'] != SLACK_OAUTH_VALIDATION_CODE:
        redirect_uri = url_add_query_params(redirect_uri,
                                            error='access_denied',
                                            error_description='Upstream oauth service called back with invalid state'
                                            )
    elif 'error' in request.args:
        return redirect(url_add_query_params(redirect_uri, error=request.args['error']))
    else:
        redirect_uri = url_add_query_params(redirect_uri,
                                            access_token=create_access_token(),
                                            expires_in=str(6 * 30 * 24 * 3600),  # ignored by server
                                            state=state['state'],
                                            token_type='bearer',
                                            )
    return redirect(redirect_uri)
