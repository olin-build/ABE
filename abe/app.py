"""Main flask app"""
import os
import time
from datetime import datetime
from urllib.parse import quote_plus as url_quote_plus

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from flask.json import JSONEncoder
from flask_cors import CORS
from flask_restplus import Api
from flask_sslify import SSLify  # redirect to https
from itsdangerous import Signer

from .resource_models.account_resources import api as account_api
from .resource_models.event_resources import api as event_api
from .resource_models.ics_resources import api as ics_api
from .resource_models.label_resources import api as label_api
from .resource_models.subscription_resources import api as subscription_api
from .routes.oauth_routes import profile as oauth_blueprint

app = Flask(__name__)
CORS(app, allow_headers=['Authorization', 'Content-Type'], supports_credentials=True)
if 'APP_SECRET_KEY' in os.environ:
    app.secret_key = os.environ['APP_SECRET_KEY'].encode()

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
if os.environ.get('ENABLE_HSTS'):
    SSLify(app, age=10, skips=['.well-known/acme-challenge/'])


@app.route('/')  # For the splash to work, needs to be declared before API
def splash():
    return render_template('splash.html')


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return JSONEncoder.default(self, obj)


app.json_encoder = CustomJSONEncoder

# add return representations

api = Api(app, doc="/docs/", version="0.1", title="ABE API",
          description="View and modify calendar events, event labels, and subscriptions. "
          "Use /login and /logout to log into ABE, in order to try out methods "
          "that view public events or modify entities."
          )


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

# Routes
app.register_blueprint(oauth_blueprint)


@app.route('/add_event')
def add_event():
    return render_template('add_event.html')


@app.route('/add_label')
def add_label():
    return render_template('add_label.html')


# For debugging, and signing in to try out the interactive /docs:


signer = Signer(app.secret_key)


@app.route('/login')
def login():
    # This is a roundabout way of logging in, but it exercises the same OAuth
    # flow that client apps use, so it doubles as testing that flow.
    redirect_uri = url_for('login_auth')
    iat = int(time.time())
    sig = signer.sign(str(iat).encode())
    return redirect('/oauth/authorize' +
                    '?redirect_uri=' + url_quote_plus(redirect_uri) +
                    '&state=' + url_quote_plus(sig.decode()))


@app.route('/logout')
def logout():
    session.pop('access_token', None)
    redirect_uri = 'login'
    return redirect('/oauth/deauthorize?redirect_uri=' + url_quote_plus(redirect_uri))


@app.route('/account/info')
def login_auth():
    iat = signer.unsign(request.args['state'])
    age = int(time.time()) - int(iat)
    # Allow this many minutes to use a link. This is unlikely for sign in with
    # slack, but reasonable for email if the user comes back to it later.
    if age > 30 * 60:
        flash('This link has expired. Please try again.')
        return redirect(url_for('login'))
    session['access_token'] = request.args['access_token']
    return render_template('account.html', args=request.args, age=age)
