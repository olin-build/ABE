#!/usr/bin/env python3
"""Main flask app"""
from flask import Flask, render_template, jsonify
from flask_restplus import Api
from flask_cors import CORS
from flask_sslify import SSLify  # redirect to https
from flask.json import JSONEncoder

from datetime import datetime

import os

import logging
FORMAT = "%(levelname)s:ABE: _||_ %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

app = Flask(__name__)
CORS(app)
#SSLify(app)

@app.route('/') #For the splash to work, needs to be declared before API
def splash():
    return render_template('splash.html')

api = Api(app, doc="/swagger/")

from .resource_models.event_resources import EventApi
from .resource_models.label_resources import LabelApi
from .resource_models.ics_resources import ICSApi


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
api.add_resource(EventApi, '/events/<string:event_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'], endpoint='event_id')  # TODO: add route for string/gphycat links
api.add_resource(EventApi, '/events/<string:event_id>/<string:rec_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'], endpoint='rec_id')  # TODO: add route for string/gphycat links

api.add_resource(LabelApi, '/labels/', methods=['GET', 'POST'], endpoint='label')
api.add_resource(LabelApi, '/labels/<string:label_name>', methods=['GET', 'PUT', 'PATCH', 'DELETE'], endpoint='label_name')

api.add_resource(ICSApi, '/ics/', methods=['GET', 'POST'], endpoint='ics')


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
