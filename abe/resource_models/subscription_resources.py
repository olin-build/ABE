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
from abe.helper_functions.query_helpers import multi_search


def subscription_to_dict(s: Subscription):
    return {'id': s.sid,
            'labels': s.labels,
            'ics_url': '/subscriptions/{}/ics'.format(s.sid)}


class SubscriptionAPI(Resource):
    """API for managing subscription feeds"""

    def get(self, subscription_id: str):
        """
        Returns information about the subscription feed with the provided ID
        """

        logging.debug("Subscription information requested: " + subscription_id)

        subscription = db.Subscription.objects(sid=subscription_id).first()

        if not subscription:
            return "Subscription not found with identifier '{}'".format(subscription_id), 404

        return subscription_to_dict(subscription)

    def post(self, subscription_id: str = ''):
        """
        Creates a subscription object with a list of labels, returning it with an ID
        """
        try:
            d = request_to_dict(request)

            subscription = Subscription.new()  # Creates a subscription with a random ID
            if subscription_id:
                subscription.sid = subscription_id

            if isinstance(d['labels'], list):
                subscription.labels = d['labels']
            elif isinstance(d['labels'], str):
                subscription.labels = d['labels'].split(',')
            else:
                raise ValueError('labels must be a list or comma-separated string')

            subscription.save()
            logging.debug("Subscription {} saved to the database".format(subscription.sid))

            return subscription_to_dict(subscription)

        except ValidationError as error:
            return {'error_type': 'validation',
                    'validation_errors': [str(err) for err in error.errors],
                    'error_message': error.message}, 400

    def put(self, subscription_id: str):
        """Modify an existing subscription"""

        data = request_to_dict(request)
        logging.debug("Received Subscription PUT data: {}".format(data))

        try:
            subscription = db.Subscription.objects(sid=subscription_id).first()

            if not subscription:
                return "Subscription not found with identifier '{}'".format(subscription_id), 404

            if isinstance(data['labels'], list):
                subscription.labels = data['labels']
            elif isinstance(data['labels'], str):
                subscription.labels = data['labels'].split(',')

            subscription.save()

        except ValidationError as error:
            return {'error_type': 'validation',
                    'validation_errors': [str(err) for err in error.errors],
                    'error_message': error.message}, 400

        else:  # return success
            return subscription_to_dict(subscription)


class SubscriptionICS(Resource):
    """Retrieves data from the given subscription as an ICS feed"""

    def get(self, subscription_id: str):
        """
        Returns an ICS feed when requested.
        Takes all search parameters that are accepted
        """
        req_dict = request_to_dict(request)

        sub = db.Subscription.objects(sid=subscription_id).first()

        if not sub:
            return "Subscription not found with identifier '{}'".format(subscription_id), 404

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
