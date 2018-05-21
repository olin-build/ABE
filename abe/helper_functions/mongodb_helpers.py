from functools import wraps

import mongoengine
from mongoengine import EmbeddedDocument

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


def Document__repr__(doc, nested=False, skip_empty_values=True):
    """Return a string containing a printable representation of a MongoDB
    Document.

    This function makes a string that would return an object of the same
    value when passed to `eval()`, if the suitable constructors are in scope.

    For example, DocumentSubclass(a=1, b="str").
    """
    def value_repr(v):
        if isinstance(v, EmbeddedDocument):
            return Document__repr__(v, nested=True, skip_empty_values=skip_empty_values)
        else:
            return repr(v)
    data_iter = ((k, v) for
                 k, v in doc._data.items()
                 if k != '_cls')
    if skip_empty_values:
        data_iter = ((k, v) for k, v in data_iter if v)
    sep = ': ' if nested else '='
    data_repr = ', '.join("{}{}{}".format(k, sep, value_repr(v))
                          for k, v in data_iter)
    return '{' + data_repr + '}' if nested else f"{doc.__class__.__name__}({data_repr})"


def Document__str__(doc, skip_empty_values=True):
    """Return a nicely-printable string representation of a MongoDB Document.

    For example, <DocumentSubclass a=1 b="str">.
    """
    def value_str(v):
        if isinstance(v, EmbeddedDocument):
            return Document__str__(v, skip_empty_values=skip_empty_values)
        elif isinstance(v, str):
            return repr(v)
        else:
            return str(v)
    data_iter = ((k, v) for
                 k, v in doc._data.items()
                 if k != '_cls')
    if skip_empty_values:
        data_iter = ((k, v) for k, v in data_iter if v)
    data_repr = ' '.join("{}={}".format(k, value_str(v))
                         for k, v in data_iter)
    return f"<{doc.__class__.__name__} {data_repr}>"
