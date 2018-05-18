import os
import re

from flask import g, session
from netaddr import IPNetwork, IPSet

from .auth_tokens import create_access_token, get_access_token_scope, is_valid_token

ACCESS_TOKEN_COOKIE_NAME = 'access_token'


def parse_intranet_cdirs():
    return (IPSet([IPNetwork(s) for s in os.environ.get('INTRANET_CDIRS', '').split(',')])
            if 'INTRANET_CDIRS' in os.environ else IPSet(['0.0.0.0/0', '0000:000::/0']))


# A set of IP addresses with edit permission.
#
# If the INTRANET_CDIRS environment variable is set, it should be a
# comma-separated list of CDIR blocks, e.g. `192.168.100.14/24` (IPv4) or
# `2001:db8::/48` (IPv6).
#
# If the INTRANET_CDIRS environment variable is not set, this defaults to the
# entire range of IP addresses.
INTRANET_CDIRS = parse_intranet_cdirs()


def reload_env_vars():
    """Used in testing."""
    global INTRANET_CDIRS
    INTRANET_CDIRS = parse_intranet_cdirs()


def after_this_request(f):  # For setting cookie
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


def ip_inside_intranet(ip_address):
    return ip_address in INTRANET_CDIRS


def request_is_from_inside_intranet(req):
    """Return a bool indicating whether a request is from inside the intranet."""
    client_ip = req.headers.get('X-Forwarded-For', req.remote_addr).split(',')[-1]
    return ip_inside_intranet(client_ip)


def request_access_token(req):
    """Returns the first valid access token from the variety of token storage
    mechanisms: Bearer token, cookie, Flask session. If the user is not signed
    in but is inside the intranet, this function creates a token and store it as
    a cookie, and returns this.
    """
    def iter_token_candidates():
        if 'Authorization' in req.headers:
            match = re.match(r'Bearer (.+)', req.headers['Authorization'])
            if match:
                yield match[1]
        yield req.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
        yield session.get('access_token', None)

    for token in iter_token_candidates():
        if is_valid_token(token):
            return token

    if request_is_from_inside_intranet(req):
        token = create_access_token(provider='intranet')

        @after_this_request
        def remember_computer(response):
            response.set_cookie(ACCESS_TOKEN_COOKIE_NAME, token, max_age=180 * 24 * 3600)

        return token


def get_request_scope(req):
    token = request_access_token(req)
    if token:
        return get_access_token_scope(token)
    return []


def request_has_scope(req, scope):
    return scope in get_request_scope(req)


def clear_auth_cookies():
    @after_this_request
    def remove_cookie(response):
        response.set_cookie(ACCESS_TOKEN_COOKIE_NAME, '', expires=0)
        session.pop('access_token', None)
