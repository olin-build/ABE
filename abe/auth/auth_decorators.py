from functools import wraps

from flask import abort, request

from .auth_requests import request_has_scope


def require_scope(scope):
    "Decorates f to raise an HTTP Unauthorized exception if the auth check fails."
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not request_has_scope(request, scope):
                abort(401)
            return f(*args, **kwargs)
        return wrapped
    return wrapper
