"""This module defines a decorator to control access to routing methods."""

import os
from functools import wraps
import re
from flask import request, abort, g, session
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
AUTH_TOKEN_SECRET = os.environ.get("AUTH_TOKEN_SECRET", uuid4().hex)

AUTHENTICATED_USER_SCOPE = ['events:create', 'events:edit', 'community_events:read']


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
    return bool(get_valid_request_auth_token(req))


def get_valid_request_auth_token(req):
    """Returns the first valid access token from the variety of tokeen storage
    mechanisms: Bearer token, cookie, Flask session. If the user is not signed
    but is inside the intranet, create a token and store it as a cookie, and
    return this.
    """
    def iter_token_candidates():
        if 'Authorization' in req.headers:
            match = re.match(r'Bearer (.+)', req.headers['Authorization'])
            if match:
                yield match[1]
        yield req.cookies.get(ACCESS_TOKEN_COOKIE_NAME, None)
        yield session.get('access_token', None)
    for token in iter_token_candidates():
        if is_valid_access_token(token):
            return token

    access_token = create_access_token()

    @after_this_request
    def remember_computer(response):
        response.set_cookie(ACCESS_TOKEN_COOKIE_NAME, access_token, max_age=180 * 24 * 3600)

    if request_is_from_inside_intranet(req):
        return access_token


def get_request_scope(req):
    if get_valid_request_auth_token(req):
        return AUTHENTICATED_USER_SCOPE
    return []


def clear_auth_cookie():
    @after_this_request
    def remove_cookie(response):
        response.set_cookie(ACCESS_TOKEN_COOKIE_NAME, '', expires=0)
        session.pop('access_token', None)


def edit_auth_required(f):
    "Decorates f to raise an HTTP UNAUTHORIZED exception if the auth check fails."
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not check_auth(request):
            abort(401)
        return f(*args, **kwargs)
    return wrapped
