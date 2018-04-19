#!/usr/bin/env python3
"""Subscription Resource models for flask"""

from flask import jsonify, request, abort, Response, make_response, Request
from flask_restful import Resource
from mongoengine import ValidationError
from bson.objectid import ObjectId
from pprint import pprint, pformat
from bson import json_util, objectid
from datetime import datetime, timedelta
from dateutil.rrule import rrule, MONTHLY, WEEKLY, DAILY, YEARLY
from icalendar import Calendar
import isodate

import pdb
import requests

import logging

from abe import database as db
from abe.document_models.subscription_documents import Subscription
from abe.helper_functions.converting_helpers import request_to_dict
from abe.helper_functions.query_helpers import get_to_event_search, event_query
from abe.helper_functions.ics_helpers import mongo_to_ics, extract_ics


def subscription_to_dict(s: Subscription, api_root='https://abe.olin.build'):
    return {'subscription_id': s.id,
            'labels': s.labels,
            'ics_url': '{}/ics/{}'.format(api_root, s.id)}


class SubscriptionAPI(Resource):
    """API for managing subscription feeds"""

    def get(self, subscription_id: str):
        """
        Returns information about the subscription feed with the provided ID
        """

        logging.debug("Subscription information requested: " + subscription_id)

        subscription = Subscription.get_sample()  # TODO: get from database instead of making something up
        subscription.id = subscription_id

        return subscription_to_dict(subscription)

    def post(self, subscription_id: str = ''):
        """
        Creates a subscription object with a list of labels, returning it with an ID
        """
        try:
            d = request_to_dict(request)

            subscription = Subscription()  # Creates a subscription with a random ID
            if subscription_id:
                subscription.id = subscription_id

            if isinstance(d['labels'], list):
                subscription.labels = d['labels']
            elif isinstance(d['labels'], str):
                subscription.labels = d['labels'].split(',')
            else:
                raise ValueError('labels must be a list or comma-separated string')

            # TODO: save to database
            logging.debug("Imagine that we saved the Subscription {} to the database".format(subscription))

            return subscription_to_dict(subscription)

        except ValidationError as error:
            return {'error_type': 'validation',
                    'validation_errors': [str(err) for err in error.errors],
                    'error_message': error.message}, 400

    def put(self, subscription_id: str):
        """Modify an existing subscription"""

        received_data = request_to_dict(request)
        logging.debug("Received Subscription PUT data: {}".format(received_data))

        try:
            # sub = db.Event.objects(id=subscription_id).first()
            sub = Subscription.get_sample()  # TODO: get from database instead of making data up
            if not sub:  # if no subscription was found
                abort(404)
            else:  # if subscription was found
                sub.update(**received_data)
                # sub.reload() # TODO: Put it back in the database

        except ValidationError as error:
            return {'error_type': 'validation',
                    'validation_errors': [str(err) for err in error.errors],
                    'error_message': error.message}, 400

        else:  # return success
            return subscription_to_dict(sub)


class SubscriptionICS(Resource):
    """Retrieves data from the given subscription as an ICS feed"""

    def get(self, subscription_id: str):
        """
        Returns an ICS feed when requested.
        Takes all search parameters that are accepted
        """
        req_dict = request_to_dict(request)

        sub = Subscription.get_sample()
        if not sub:
            abort(404)

        if 'labels' in req_dict:
            logging.warning('ICS feed requested with manually-specified labels {}. '
                            'They have been ignored in favor of the stored labels {}'.format(req_dict['labels'],
                                                                                             sub.labels))

        req_dict['labels'] = sub.labels

        query = event_query(get_to_event_search(req_dict))
        results = db.Event.objects(__raw__=query)

        # converts mongoDB objects to an ICS format
        response = mongo_to_ics(results)
        logging.debug("ics feed created for Subscription {}".format(sub.id))
        cd = "attachment;filename=abe.ics"
        return Response(response,
                        mimetype="text/calendar",
                        headers={"Content-Disposition": cd})
