#!/usr/bin/env python3
"""Resource models for flask"""
from flask import Flask, jsonify, render_template, request, abort
from flask_restful import Resource, Api, reqparse
from pprint import pprint, pformat
import json
import os

import logging

import database as db


class EventApi(Resource):
    """API for interacting with events"""

    def get(self, event_id=None):
        """Retrieve events"""
        if event_id:  # use event id if present
            print('eventid: ' + event_id)
            result = db.Event.objects(id=event_id).first()
            if not result:
                abort(404)

            return jsonify(json.loads(result.to_json()))
        else:  # search database based on parameters
            # TODO: search based on parameters
            results = db.Event.objects()
            if not results:
                abort(404)

            # TODO: expand recurrences
            return jsonify(result=[json.loads(result.to_json()) for result in results])

    def post(self):
        """Create new event with parameters passed in through args or form"""
        print('***REQUEST DATA***\n' + request.data)
        received_data = dict(request.data)  # combines args and form
        try:
            new_event = db.Event(**received_data)
            new_event.save()
        except Exception as error:
            abort(400)

        return "", 201

    def put(self, event_id):
        """Replace individual event"""
        pass

    def patch(self, event_id):
        """Modify individual event"""
        pass

    def delete(self, event_id):
        """Delete individual event"""
        pass


class LabelApi(Resource):
    """API for interacting with all labels (searching, creating)"""

    def get(self, label_name=None):
        """Retrieve labels"""
        if label_name:  # use event id if present
            result = db.Label.objects(name=label_name).first()
            if not result:
                abort(404)
            else:
                return jsonify(json.loads(result.to_json()))
        else:  # search database based on parameters
            # TODO: search based on terms
            results = db.Label.objects()
            if not results:
                abort(404)
            else:
                return jsonify([json.loads(result.to_json()) for result in results])

    def post(self):
        """Create new label with parameters passed in through args or form"""
        print('***REQUEST DATA***\n' + request.data)
        received_data = dict(request.data)  # combines args and form
        try:
            new_label = db.Label(**received_data)
            new_label.save()
        except ValidationError as error:
            abort(400)

        return 201

    def put(self, label_name):
        """Replace individual event"""
        pass

    def patch(self, label_name):
        """Modify individual event"""
        pass

    def delete(self, label_name):
        """Delete individual event"""
        pass
