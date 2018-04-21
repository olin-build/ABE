#!/usr/bin/env python3
"""Main flask app"""
from flask import Flask, render_template, jsonify
from flask_restful import Api
from flask_cors import CORS
from flask_sslify import SSLify  # redirect to https
from flask.json import JSONEncoder

from datetime import datetime

import os

import logging

FORMAT = "%(levelname)s:ABE: _||_ %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)

from .resource_models.event_resources import EventApi
from .resource_models.label_resources import LabelApi
from .resource_models.ics_resources import ICSApi
from .resource_models.subscription_resources import SubscriptionAPI, SubscriptionICS

app = Flask(__name__)
CORS(app)

# Redirect HTTP to HTTPS.
#
# For operational flexibility, set the HSTS max-age to a few seconds, instead of
# the on-year default. The threats mitigated by HSTS policy caching are in any
# case mostly not relevant to API services.
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

api = Api(app)


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

# Route resources
api.add_resource(EventApi, '/events/', methods=['GET', 'POST'], endpoint='event')
# TODO: add route for string/gphycat links
api.add_resource(EventApi, '/events/<string:event_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'], endpoint='event_id')
api.add_resource(EventApi, '/events/<string:event_id>/<string:rec_id>',
                 methods=['GET', 'PUT', 'PATCH', 'DELETE'], endpoint='rec_id')  # TODO: add route for string/gphycat links

api.add_resource(LabelApi, '/labels/', methods=['GET', 'POST'], endpoint='label')
api.add_resource(LabelApi, '/labels/<string:label_name>',
                 methods=['GET', 'PUT', 'PATCH', 'DELETE'], endpoint='label_name')

api.add_resource(ICSApi, '/ics/', methods=['GET', 'POST'], endpoint='ics')

api.add_resource(SubscriptionAPI, '/subscriptions/', methods=['POST'], endpoint='subscription')
api.add_resource(SubscriptionAPI, '/subscriptions/<string:subscription_id>',
                 methods=['GET', 'PUT', 'POST'], endpoint='subscription_id')

api.add_resource(SubscriptionICS, '/subscriptions/<string:subscription_id>/ics',
                 methods=['GET'], endpoint='subscription_ics')


@app.route('/')
def splash():
    return render_template('splash.html')


@app.route('/add_event')
def add_event():
    return render_template('add_event.html')


@app.route('/add_label')
def add_label():
    return render_template('add_label.html')


if __name__ == '__main__':
    app.debug = os.getenv('FLASK_DEBUG') != 'False'  # updates the page as the code is saved
    HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT)
