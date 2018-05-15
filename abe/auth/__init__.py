"""This module defines a decorator to control access to routing methods."""

import os
from functools import wraps

from flask import request, abort, g
from netaddr import IPNetwork, IPSet
import logging

ACCESS_TOKEN_COOKIE_NAME = 'access_token'

# A set of IP addresses with edit permission.
#
# If the INTRANET_IPS environment variable is set, it should be a
# comma-separated list of CDIR blocks, e.g. `192.168.100.14/24` (IPv4) or
# `2001:db8::/48` (IPv6).
#
# If the INTRANET_IPS environment variable is not set, this defaults to the
# entire range of IP addresses.
INTRANET_IPS = (IPSet([IPNetwork(s) for s in os.environ.get('INTRANET_IPS', '').split(',')])
                if 'INTRANET_IPS' in os.environ else IPSet(['0.0.0.0/0', '0000:000::/0']))

SHARED_SECRET = os.environ.get("SHARED_SECRET", "")
if not SHARED_SECRET:
    logging.critical("SHARED_SECRET isn't set")


def after_this_request(f):  # For setting cookie
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


def check_auth(req):
    """
    Checks if a request is from an IP whitelist, or if it has a secret cookie.
    If the request is in the IP whitelist, sets the secret cookie.
    Returns a Bool of passing.
    """
    access_token = f"secret:{SHARED_SECRET or '---'}"
    client_ip = req.headers.get('X-Forwarded-For', req.remote_addr).split(',')[-1]
    if client_ip in INTRANET_IPS:
        @after_this_request
        def remember_computer(response):
            response.headers['Access-Control-Expose-Headers'] = 'Access-Token'
            response.headers['Access-Token'] = access_token
            response.set_cookie(ACCESS_TOKEN_COOKIE_NAME, access_token, max_age=180 * 24 * 3600)
        return True
    if req.cookies.get(ACCESS_TOKEN_COOKIE_NAME) == access_token:
        return True
    if req.headers.get('Authorization') == f"Bearer {access_token}":
        return True
    return False


def edit_auth_required(f):
    "Decorates f to raise an HTTP UNAUTHORIZED exception if the auth check fails."
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not check_auth(request):
            abort(401)
        return f(*args, **kwargs)
    return wrapped
