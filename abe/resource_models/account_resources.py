from flask import request
from flask_restplus import Namespace, Resource, fields

from abe.auth import (get_access_token_provider, get_access_token_role, get_access_token_scope, request_access_token,
                      request_is_from_inside_intranet)

api = Namespace('account', description='Account info')

resource_model = api.model("Account", {
    "authenticated": fields.Boolean(
        required=True,
        description="The client has been authenticated or is inside the intranet."),
    "inside_intranet": fields.Boolean(
        required=True,
        description="The client is inside the intranet."),
    "permissions": fields.List(
        fields.String, required=True,
        description="A list of strings that name granted permissions."),
    "provider": fields.String(enum=['intranet', 'email', 'slack']),
    "role": fields.String(enum=['user', 'admin']),
    "scope": fields.List(
        fields.String, required=True,
        description="The OAuth scope."),
})


class AccountApi(Resource):
    """Account information for the authenticated user"""

    @api.marshal_with(resource_model)
    def get(self):
        access_token = request_access_token(request)
        permissions = []
        if access_token:
            permissions += ['view_all_events', 'add_events', 'edit_events']
        return {
            'authenticated': bool(access_token),
            'inside_intranet': request_is_from_inside_intranet(request),
            'permissions': permissions,
            'provider': get_access_token_provider(access_token) if access_token else None,
            'role': get_access_token_role(access_token) if access_token else None,
            'scope': get_access_token_scope(access_token),
        }


api.add_resource(AccountApi, '/', methods=['GET'], endpoint='account')
