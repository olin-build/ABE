#!/usr/bin/env python3
"""ICS Resource models for flask"""

from flask import jsonify, request, abort, Response, make_response
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


def subscription_to_dict(s: Subscription):
    return {'subscription_id': s.id,
            'labels': s.labels,
            'ics_url': 'example.com/ics/{}'.format(s.id)}


class SubscriptionAPI(Resource):
    """API for managing subscription feeds"""

    def get(self, subscription_id: str):
        """
        Returns information about the subscription feed with the provided ID
        """

        logging.debug("Subscription information requested: " + subscription_id)

        subscription = Subscription()  # TODO: get from database instead of making something up
        subscription.id = subscription_id
        subscription.labels = 'hello world carpe'.split()

        return subscription_to_dict(subscription)

    def post(self):
        """
        Creates a subscription object with a list of labels, returning it with an ID
        """
        try:
            d = request_to_dict(request)

            subscription = Subscription()  # Creates a subscription with a random ID
            if isinstance(d['labels'], list):
                subscription.labels = d['labels']
            elif isinstance(d['labels'], str):
                subscription.labels = d['labels'].split(',')
            else:
                raise ValueError('labels must be a list or comma-separated string')

            return subscription_to_dict(subscription)

        except ValidationError as error:
            return {'error_type': 'validation',
                    'validation_errors': [str(err) for err in error.errors],
                    'error_message': error.message}, 400
