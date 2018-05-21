"""Label Resource models for flask"""

import logging

from flask import request
from flask_restplus import Namespace, Resource, fields

from abe import database as db
from abe.auth import require_scope
from abe.helper_functions.converting_helpers import request_to_dict
from abe.helper_functions.mongodb_helpers import mongo_resource_errors
from abe.helper_functions.query_helpers import multi_search

api = Namespace('labels', description='Event labels')

# This should be kept in sync with the document model, which drives the format
model = api.model("Label", {
    "id": fields.String(readonly=True),
    "name": fields.String(example="library"),
    "description": fields.String(
        description="Description of the label",
        example="Any event that has to do with the library",
    ),
    "url": fields.String(description="Not currently used."),
    # "parent_labels": fields.List(fields.String),
    "color": fields.String(
        description="Color for calendar display.",
        example="#aaccff",
    ),
    "default":  fields.Boolean(
        default=False,
        description="If true, appears in the default calendar view.",
    ),
    "protected": fields.Boolean(
        default=False,
        description="If true, requires the admin role to create and edit labeled events."
    ),
    "visibility": fields.String(
        enum=['public', 'olin', 'students'],
        description="Who can see events with this label.",
    ),
})


class LabelApi(Resource):
    """API for interacting with all labels (searching, creating)"""

    @mongo_resource_errors
    @api.doc(security=[])
    @api.marshal_with(model)
    def get(self, id=None):
        """Retrieve a list of labels"""
        if id:  # use label name/object id if present
            logging.debug('Label requested: %s', id)
            search_fields = ['name', 'id']
            result = multi_search(db.Label, id, search_fields)
            if not result:
                return "Label not found with identifier '{}'".format(id), 404
            return result
        return list(db.Label.objects())

    @require_scope('create:labels')
    @mongo_resource_errors
    @api.expect(model)
    @api.marshal_with(model)
    def post(self):
        """Create a new label"""
        received_data = request_to_dict(request)
        logging.debug("Received POST data: %s", received_data)
        new_label = db.Label(**received_data)
        new_label.save()
        return new_label, 201

    @require_scope('edit:labels')
    @mongo_resource_errors
    @api.expect(model)
    @api.marshal_with(model)
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

        return result

    @require_scope('delete:labels')
    @mongo_resource_errors
    @api.marshal_with(model)
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
        return result


api.add_resource(LabelApi, '/', methods=['GET', 'POST'], endpoint='label')
api.add_resource(LabelApi, '/<string:id>',
                 methods=['GET', 'PUT', 'PATCH', 'DELETE'],
                 endpoint='label_id')
