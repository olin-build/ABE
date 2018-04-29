#!/usr/bin/env python3
"""ICS Resource models for flask"""

import logging

import requests
from flask import Response,  request
from icalendar import Calendar
from mongoengine import ValidationError

from abe import database as db
from abe.auth import edit_auth_required
from abe.helper_functions.converting_helpers import request_to_dict
from abe.helper_functions.ics_helpers import extract_ics, mongo_to_ics
from abe.helper_functions.query_helpers import event_query, get_to_event_search
from flask_restplus import Namespace, Resource, fields

api = Namespace('ics', description='ICS feeds')

# This should be kept in sync with the document model, which drives the format
ics_model = api.model("ICS_Model", {
    "url": fields.Url(required=True),
    "labels": fields.List(fields.String, required=True)
})


class ICSApi(Resource):
    """API for interacting with ics feeds"""

    @api.deprecated
    def get(self):
        """
        Deprecated, use SubscriptionICSFeed get instead.
        Returns an ICS feed when requested
        """
        # configure ics specs from fullcalendar to be mongoengine searchable
        query = event_query(get_to_event_search(request))
        results = db.Event.objects(__raw__=query)
        # converts mongoDB objects to an ICS format
        response = mongo_to_ics(results)
        logging.debug("ics feed created")
        cd = "attachment;filename=abe.ics"
        return Response(response,
                        mimetype="text/calendar",
                        headers={"Content-Disposition": cd})


    @edit_auth_required
    @api.expect(ics_model)
    def post(self):
        """
        Converts an ICS feed input to mongoDB objects
        """
        try:
            # reads outside ics feed
            url = request_to_dict(request)
            data = requests.get(url['url'].strip()).content.decode('utf-8')
            cal = Calendar.from_ical(data)
            if 'labels' in url:
                labels = url['labels']
            else:
                labels = ['unlabeled']

            extract_ics(cal, url['url'], labels)
        except ValidationError as error:
            return {'error_type': 'validation',
                    'validation_errors': [str(err) for err in error.errors],
                    'error_message': error.message}, 400


api.add_resource(ICSApi, '/', methods=['GET', 'POST'], endpoint='ics')
