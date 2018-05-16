"""This module defines a decorator to control access to routing methods."""

import os
from functools import wraps
import re
from flask import request, abort, g
from netaddr import IPNetwork, IPSet
from uuid import uuid4
import time
import jwt

ACCESS_TOKEN_COOKIE_NAME = 'access_token'

# A set of IP addresses with edit permission.
#
# If the INTRANET_CDIRS environment variable is set, it should be a
# comma-separated list of CDIR blocks, e.g. `192.168.100.14/24` (IPv4) or
# `2001:db8::/48` (IPv6).
#
# If the INTRANET_CDIRS environment variable is not set, this defaults to the
# entire range of IP addresses.
INTRANET_CDIRS = (IPSet([IPNetwork(s) for s in os.environ.get('INTRANET_CDIRS', '').split(',')])
                  if 'INTRANET_CDIRS' in os.environ else IPSet(['0.0.0.0/0', '0000:000::/0']))

# For development and testing, default to an instance-specific secret.
AUTH_TOKEN_SECRET = os.environ.get("AUTH_TOKEN_SECRET", str(uuid4()))


def create_access_token():
    return jwt.encode({'iat': int(time.time())}, AUTH_TOKEN_SECRET, algorithm='HS256').decode()


def is_valid_access_token(token):
    if not token:
        return False
    enc = token.encode()
    try:
        jwt.decode(enc, AUTH_TOKEN_SECRET, algorithms='HS256')  # for effect
    except Exception:
        return False
    return True


def after_this_request(f):  # For setting cookie
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


def request_is_from_inside_intranet(req):
    """Return a bool indicating whether a request is from inside the intranet."""
    client_ip = req.headers.get('X-Forwarded-For', req.remote_addr).split(',')[-1]
    return client_ip in INTRANET_CDIRS


def check_auth(req):
    """Checks if a request is from an IP whitelist, or if it has a secret cookie,
    or a valid bearer token.

    If the request is in the IP whitelist, sets the secret cookie.

    Returns a bool that indicates whether the request is authorized.
    """
    if request_is_from_inside_intranet(req):
        access_token = create_access_token()

        @after_this_request
        def remember_computer(response):
            response.set_cookie(ACCESS_TOKEN_COOKIE_NAME, access_token, max_age=180 * 24 * 3600)
        return True
    if is_valid_access_token(req.cookies.get(ACCESS_TOKEN_COOKIE_NAME)):
        return True
    if 'Authorization' in req.headers:
        match = re.match(r'Bearer (.+)', req.headers['Authorization'])
        return match and is_valid_access_token(match[1])
    return False


def clear_auth_cookie():
    @after_this_request
    def remove_cookie(response):
        response.set_cookie(ACCESS_TOKEN_COOKIE_NAME, '', expires=0)


def edit_auth_required(f):
    "Decorates f to raise an HTTP UNAUTHORIZED exception if the auth check fails."
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not check_auth(request):
            abort(401)
        return f(*args, **kwargs)
    return wrapped
