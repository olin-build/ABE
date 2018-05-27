from uuid import uuid4
from flask import abort, request
from flask_restplus import Namespace, Resource, fields

from abe import database as db
from abe.auth import require_scope
from abe.helper_functions.converting_helpers import request_to_dict
from abe.helper_functions.mongodb_helpers import mongo_resource_errors

api = Namespace('apps',
                description="Applications that can sign in users, and use their credentials to access ABE data. "
                "Also see the wiki pages on "
                "[user authentication](https://github.com/olin-build/ABE/wiki/User-Authentication) "
                "and [sign in with ABE](https://github.com/olin-build/ABE/wiki/Sign-in-with-ABE)."
                )

# This should be kept in sync with the document model, which drives the format
model = api.model('App', {
    'client_id': fields.String(
        readonly=True,
        description="The API server creates this. Use it in the "
        "[OAuth flow](https://github.com/olin-build/ABE/wiki/User-Authentication)."
    ),
    'name': fields.String(example="Awesome App"),
    'short_description': fields.String(
        description="A short description. Not currently used."),
    'long_description': fields.String(
        description="A few lines that are displayed in the sign in form."),
    'url': fields.String(
        description="Your app's home page. Not currently used.",
        example="https://awesome.olin.build"),
    'redirect_uris': fields.List(
        fields.String,
        description="The OAuth 2.0 `redirect_uri` must begin with one of these.",
        example=["http://127.0.0.1:3000/"]),
    'scopes': fields.List(
        fields.String,
        description="Ignore this, for now",
        example=["read"]),
})


class AppApi(Resource):

    @mongo_resource_errors
    @require_scope('admin:apps')
    @api.doc(security=[{'oauth2': ['admin']}])
    @api.marshal_with(model)
    def get(self, client_id=None):
        """Retrieve a single application by id, or a list of apps"""
        if client_id:
            result = db.App.objects(client_id=client_id).first()
            if not result:
                return "App not found with identifier '{}'".format(client_id), 404
            return result
        return list(db.App.objects())

    @require_scope('admin:apps')
    @mongo_resource_errors
    @api.expect(model)
    @api.marshal_with(model)
    def post(self):
        """Create an app.

        The API server creates the `client_id`.
        Use it in the [authentication flow](https://github.com/olin-build/ABE/wiki/User-Authentication).
        """
        data = request_to_dict(request)
        if 'client_id' in data:
            abort(400)
        data['client_id'] = uuid4().hex
        app = db.App(**data)
        app.save()
        return app, 201

    @require_scope('admin:apps')
    @mongo_resource_errors
    @api.expect(model)
    @api.marshal_with(model)
    def put(self, client_id):
        """Update an app"""
        data = request_to_dict(request)
        if 'client_id' in data:
            abort(400)
        result = db.App.objects(client_id=client_id).first()
        if not result:
            return "App not found with identifier '{}'".format(client_id), 404
        result.modify(**data)
        return result

    @require_scope('admin:apps')
    @mongo_resource_errors
    @api.marshal_with(model)
    def delete(self, client_id):
        """Delete an app"""
        result = db.App.objects(client_id=client_id).first()
        if not result:
            abort(404, "App not found with identifier '{}'".format(client_id))
        result.delete()
        return result


api.add_resource(AppApi, '/', methods=['GET', 'POST'], endpoint='app')
api.add_resource(AppApi, '/<string:client_id>',
                 methods=['GET', 'PUT', 'PATCH', 'DELETE'],
                 endpoint='app_id')
