from functools import wraps

from flask import abort, request

from .auth_requests import check_auth


def edit_auth_required(f):
    "Decorates f to raise an HTTP UNAUTHORIZED exception if the auth check fails."
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not check_auth(request):
            abort(401)
        return f(*args, **kwargs)
    return wrapped
