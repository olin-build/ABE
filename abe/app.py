"""Main flask app"""
import os
from datetime import datetime

from flask import Flask, g, jsonify, render_template, json
from flask.json import JSONEncoder
from flask_cors import CORS
from flask_restplus import Api
from flask_sslify import SSLify  # redirect to https

from .resource_models.app_resources import api as app_api
from .resource_models.event_resources import api as event_api
from .resource_models.ics_resources import api as ics_api
from .resource_models.label_resources import api as label_api
from .resource_models.subscription_resources import api as subscription_api
from .resource_models.user_resources import api as user_api
from .routes.admin_routes import profile as admin_blueprint
from .routes.oauth_routes import profile as oauth_blueprint

app = Flask(__name__)
CORS(app, allow_headers=['Authorization', 'Content-Type'], supports_credentials=True)
app.secret_key = os.environ['APP_SECRET_KEY'].encode() if 'APP_SECRET_KEY' in os.environ else os.urandom(32)

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

authorizationUrl = '/oauth/authorize?redirect_uri=/login/token%3Fredirect_uri%3D%2Fdocs&response_mode=query'

api = Api(app, doc="/docs/", title="ABE API", version="0.1",
          description="""View and modify calendar events, event labels, and subscriptions.
          Click on a resource row ("events", "labels", etc.) to see its methods. \
          Click on a method to see its description. \
          Click on “Models” to see documentation for each of the models.
          See the [wiki page](https://github.com/olin-build/ABE/wiki/ABE-API) for information about working \
          with the ABE API. \
          Use [this link](/docs/postman.json) to download a collection file for use with \
          [Postman](https://www.getpostman.com).""",
          security=[{'oauth2': 'read'}],
          authorizations={
              'oauth2': {
                  'type': 'oauth2',
                  'authorizationUrl': authorizationUrl,
                  'scopes': {
                      'admin': 'Administrative access',
                      'read': 'Read access to non-public events',
                      'write': 'Write access to non-locked events',
                  }
              }
          }
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
api.add_namespace(app_api)
api.add_namespace(event_api)
api.add_namespace(ics_api)
api.add_namespace(label_api)
api.add_namespace(subscription_api)
api.add_namespace(user_api)

# Routes
app.register_blueprint(admin_blueprint)
app.register_blueprint(oauth_blueprint)


@app.route('/docs/postman.json')
def postman_docs():
    urlvars = False  # Build query strings in URLs
    swagger = True  # Export Swagger specifications
    data = api.as_postman(urlvars=urlvars, swagger=swagger)
    return (json.dumps(data, indent=2)), 200, {'Content-Type': 'application/json; charset=utf-8'}
