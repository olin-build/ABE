from flask import request
from flask_restplus import Namespace, Resource, fields

from abe.auth import check_auth

api = Namespace('account', description='Account info')

resource_model = api.model("Account", {
    "authenticated": fields.Boolean(required=True),
    "permissions": fields.List(fields.String, required=True)
})


class AccountApi(Resource):
    """Account information for the authenticated user"""

    @api.marshal_with(resource_model)
    def get(self):
        auth = check_auth(request)
        permissions = []
        if auth:
            permissions += ['view_all_events', 'add_events', 'edit_events']
        return {
            'authenticated': auth,
            'permissions': permissions,
        }


api.add_resource(AccountApi, '/', methods=['GET'], endpoint='account')
