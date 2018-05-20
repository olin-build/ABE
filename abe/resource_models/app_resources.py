from uuid import uuid4
from flask import request
from flask_restplus import Namespace, Resource, fields

from abe import database as db
from abe.auth import require_scope
from abe.helper_functions.converting_helpers import mongo_to_dict, request_to_dict
from abe.helper_functions.mongodb_helpers import mongo_resource_errors

api = Namespace('apps',
                description='Create and update apps that are registered to OAuth against ABE.')

# This should be kept in sync with the document model, which drives the format
app_model = api.model("App", {
    "name": fields.String(required=True),
    "short_description": fields.String,
    "long_description": fields.String,
    "url": fields.String,
    # "client_id": fields.String(required=True),
    "redirect_uris": fields.List(fields.String),
    "scopes": fields.List(fields.String),
})


class AppApi(Resource):

    @mongo_resource_errors
    @require_scope('admin:apps')
    def get(self, id=None):
        """Retrieve a single application by id, or a list of apps"""
        if id:
            result = db.App.objects(client_id=id).first()
            if not result:
                return "App not found with identifier '{}'".format(id), 404
            return mongo_to_dict(result)
        else:
            return [mongo_to_dict(result) for result in db.App.objects()]

    @require_scope('admin:apps')
    @mongo_resource_errors
    @api.expect(app_model)
    def post(self):
        """Create an app"""
        data = request_to_dict(request)
        data['client_id'] = uuid4().hex
        app = db.App(**data)
        app.save()
        return mongo_to_dict(app), 201

    @require_scope('admin:apps')
    @mongo_resource_errors
    @api.expect(app_model)
    def put(self, id):
        """Update an app"""
        data = request_to_dict(request)
        result = db.App.objects(client_id=id).first()
        if not result:
            return "App not found with identifier '{}'".format(id), 404
        result.update(**data)
        return mongo_to_dict(result)

    @require_scope('admin:apps')
    @mongo_resource_errors
    def delete(self, id):
        """Delete an app"""
        result = db.App.objects(client_id=id).first()
        if not result:
            return "App not found with identifier '{}'".format(id), 404
        result.delete()
        return mongo_to_dict(result)


api.add_resource(AppApi, '/', methods=['GET', 'POST'], endpoint='app')
api.add_resource(AppApi, '/<string:id>',
                 methods=['GET', 'PUT', 'PATCH', 'DELETE'],
                 endpoint='app_id')
