from functools import wraps

import mongoengine

# This is sketchy, but mongoengine doesn't export a helpful base class that
# could be used to catch all and only input-related errors (as opposed to server
# and implementation errors.)
#
# If this breaks with a future release, could be released by an extensive list
# of the relevant errors.
mongo_errors = tuple(mongoengine.errors.__dict__[k] for k in mongoengine.errors.__all__)


def mongo_resource_errors(f):
    "Decorates f to response with a 400 if a MongoDB error is raised."
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except mongoengine.ValidationError as error:
            return {'error_type': 'validation',
                    'validation_errors': [str(err) for err in error.errors or [error]],
                    'error_message': error.message,
                    }, 400
        except mongoengine.DoesNotExist as error:
            return {'error_type': 'validation',
                    'error_message': str(error)}, 404
        except mongo_errors as error:  # noqa: E0712
            return {'error_type': 'validation',
                    'error_message': str(error)}, 400
    return wrapper
