from flask import request
from flask_restplus import Namespace, Resource, fields

from abe.auth import (get_access_token_provider, get_access_token_role, get_access_token_scope, request_access_token,
                      request_is_from_inside_intranet)

api = Namespace('user', description="User information and authorization.")

resource_model = api.model('User', {
    'authenticated': fields.Boolean(
        default=False,
        description="""The user has been authenticated. This includes **implicit "authentication**, which is granted \
        to anyone visiting from inside the intranet (and may remain when the same user agent visits again from \
        outside).""",
    ),
    'inside_intranet': fields.Boolean(
        description="""The user agent is [inside the \
        intranet](http://tvtropes.org/pmwiki/pmwiki.php/Main/TheCallsAreComingFromInsideTheHouse).""",
    ),
    'provider': fields.String(
        enum=['intranet', 'email', 'slack'],
        description="""How did the user sign in?\n\n`"intranet"` means they were *implicitly* authenticated, by \
        visiting from inside the intranet.""",
    ),
    'role': fields.String(
        description="The user's role. You probably want to check the scope instead.",
        enum=['user', 'admin']
    ),
    'scope': fields.List(
        fields.String, required=True, default=[],
        description="A list of authorization scopes that have been granted to the user.",
    ),
})


class UserApi(Resource):

    @api.marshal_with(resource_model)
    @api.doc(security=[])
    def get(self):
        """Get information about the currently-authenticated user.
        Also, whether the client is inside the intranet."""
        access_token = request_access_token(request)
        if not access_token:
            return None
        return {
            'authenticated': bool(access_token),
            'inside_intranet': request_is_from_inside_intranet(request),
            'provider': get_access_token_provider(access_token),
            'role': get_access_token_role(access_token),
            'scope': get_access_token_scope(access_token),
        }


api.add_resource(UserApi, '/', methods=['GET'], endpoint='user')
