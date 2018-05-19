#!/usr/bin/env python3
"""Label Resource models for flask"""

import logging

from flask import request
from flask_restplus import Namespace, Resource, fields
from mongoengine import ValidationError

from abe import database as db
from abe.auth import require_scope
from abe.helper_functions.converting_helpers import mongo_to_dict, request_to_dict
from abe.helper_functions.mongodb_helpers import mongo_resource_errors
from abe.helper_functions.query_helpers import multi_search

api = Namespace('labels', description='Label related operations')

# This should be kept in sync with the document model, which drives the format
label_model = api.model("Label_Model", {
    "name": fields.String(required=True),
    "description": fields.String,
    "url": fields.Url,
    "default":  fields.Boolean,
    "parent_labels": fields.List(fields.String),
    "color": fields.String,
    "visibility": fields.String(enum=['public', 'olin', 'students']),
    "protected": fields.Boolean
})


class LabelApi(Resource):
    """API for interacting with all labels (searching, creating)"""

    @mongo_resource_errors
    def get(self, id=None):
        """Retrieve a list of labels"""
        if id:  # use label name/object id if present
            logging.debug('Label requested: %s', id)
            search_fields = ['name', 'id']
            result = multi_search(db.Label, id, search_fields)
            if not result:
                return "Label not found with identifier '{}'".format(id), 404
            else:
                return mongo_to_dict(result)
        else:  # search database based on parameters
            # TODO: search based on terms
            results = db.Label.objects()
            if not results:
                return []
            else:
                return [mongo_to_dict(result) for result in results]

    @require_scope('edit:labels')
    @mongo_resource_errors
    @api.expect(label_model)
    def post(self):
        """Create a new label"""
        received_data = request_to_dict(request)
        logging.debug("Received POST data: %s", received_data)
        # TODO: replace this try:except: by just the try: block, after PR #229 is merged
        try:
            new_label = db.Label(**received_data)
            new_label.save()
        except ValidationError as error:
            return {'error_type': 'validation',
                    'validation_errors': str(error),  # [str(err) for err in error.errors or [error]],
                    'error_message': error.message,
                    }, 400
        return mongo_to_dict(new_label), 201

    @require_scope('edit:labels')
    @mongo_resource_errors
    @api.expect(label_model)
    def put(self, id):
        """Modify a label's properties"""
        received_data = request_to_dict(request)
        logging.debug("Received PUT data: %s", received_data)
        search_fields = ['name', 'id']
        result = multi_search(db.Label, id, search_fields)
        if not result:
            return "Label not found with identifier '{}'".format(id), 404

        previous_name = result['name']
        new_name = received_data.get('name', previous_name)

        result.update(**received_data)

        # TODO: do this inside the same transaction as the update above, on update to mnogo 4.0
        if previous_name != new_name:
            db.Event.objects(labels=previous_name).update(labels__S=new_name)
            db.ICS.objects(labels=previous_name).update(labels__S=new_name)
            db.Subscription.objects(labels=previous_name).update(labels__S=new_name)

        return mongo_to_dict(result)

    @require_scope('edit:labels')
    @mongo_resource_errors
    def delete(self, id):
        """Delete a label"""
        logging.debug('Label requested: %s', id)
        search_fields = ['name', 'id']
        result = multi_search(db.Label, id, search_fields)
        if not result:
            return "Label not found with identifier '{}'".format(id), 404

        received_data = request_to_dict(request)
        logging.debug("Received DELETE data: %s", received_data)
        result.delete()

        # TODO: this should also remove the label from tagged events
        # TODO: should this operation fail if it would leave events untagged?
        return mongo_to_dict(result)


api.add_resource(LabelApi, '/', methods=['GET', 'POST'], endpoint='label')
api.add_resource(LabelApi, '/<string:id>',
                 methods=['GET', 'PUT', 'PATCH', 'DELETE'],
                 endpoint='id')
