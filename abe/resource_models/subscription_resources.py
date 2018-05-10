#!/usr/bin/env python3
"""Subscription Resource models for flask"""

import logging

from flask import Response, request

from abe import database as db
from abe.document_models.subscription_documents import Subscription
from abe.helper_functions.converting_helpers import request_to_dict
from abe.helper_functions.mongodb_helpers import mongo_resource_errors
from abe.helper_functions.ics_helpers import mongo_to_ics
from abe.helper_functions.query_helpers import event_query, get_to_event_search
from flask_restplus import Namespace, Resource, fields

api = Namespace('subscriptions', description='Subscription related operations')

# This should be kept in sync with the document model, which drives the format
sub_model = api.model('Sub_Model', {
    "labels": fields.List(fields.String)
})


def subscription_to_dict(s: Subscription):
    return {'id': s.sid,
            'labels': s.labels,
            'ics_url': '/subscriptions/{}/ics'.format(s.sid)}


class SubscriptionAPI(Resource):
    """API for managing subscription feeds"""

    @mongo_resource_errors
    def get(self, subscription_id: str):
        """
        Returns information about the subscription feed with the provided ID
        """

        logging.debug("Subscription information requested: " + subscription_id)

        subscription = db.Subscription.objects(sid=subscription_id).first()

        if not subscription:
            return "Subscription not found with identifier '{}'".format(subscription_id), 404

        return subscription_to_dict(subscription)

    @mongo_resource_errors
    @api.expect(sub_model)
    def post(self, subscription_id: str = ''):
        """
        Creates a subscription object with a list of labels, returning it with an ID
        """
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

    @mongo_resource_errors
    @api.expect(sub_model)
    def put(self, subscription_id: str):
        """Modify an existing subscription"""

        data = request_to_dict(request)
        logging.debug("Received Subscription PUT data: {}".format(data))

        subscription = db.Subscription.objects(sid=subscription_id).first()

        if not subscription:
            return "Subscription not found with identifier '{}'".format(subscription_id), 404

        if isinstance(data['labels'], list):
            subscription.labels = data['labels']
        elif isinstance(data['labels'], str):
            subscription.labels = data['labels'].split(',')

        subscription.save()

        return subscription_to_dict(subscription)


class SubscriptionICS(Resource):
    """Retrieves data from the given subscription as an ICS feed"""

    @mongo_resource_errors
    def get(self, subscription_id: str):
        """
        Returns an ICS feed when requested.
        Takes all search parameters that are accepted
        """
        req_dict = request_to_dict(request)

        sub = db.Subscription.objects(sid=subscription_id).first()  # type: Subscription

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
        response = mongo_to_ics(results, sub=sub)
        logging.debug("ics feed created for Subscription {}".format(sub.id))
        cd = "attachment;filename=abe.ics"
        return Response(response,
                        mimetype="text/calendar",
                        headers={"Content-Disposition": cd})


api.add_resource(SubscriptionAPI, '/', methods=['POST'],
                 endpoint='subscription')
api.add_resource(SubscriptionAPI, '/<string:subscription_id>',
                 methods=['GET', 'PUT', 'POST'], endpoint='subscription_id')

api.add_resource(SubscriptionICS, '/<string:subscription_id>/ics',
                 methods=['GET'], endpoint='subscription_ics')
