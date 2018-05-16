from flask import request
from flask_restplus import Namespace, Resource, fields

from abe.auth import check_auth, request_is_from_inside_intranet

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
        description="A list of strings that name granted permissions.")
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
            'inside_intranet': request_is_from_inside_intranet(request),
            'permissions': permissions,
        }


api.add_resource(AccountApi, '/', methods=['GET'], endpoint='account')
