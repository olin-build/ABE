"""This module defines a decorator to control access to routing methods."""

import os
from functools import wraps

from flask import request, abort, g
from netaddr import IPNetwork, IPSet
import logging

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

shared_secret = os.environ.get("SHARED_SECRET", "")
if not shared_secret:
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
    client_ip = req.headers.get(
        'X-Forwarded-For', req.remote_addr).split(',')[-1]
    if client_ip in INTRANET_IPS:
        @after_this_request
        def remember_computer(response):
            response.set_cookie('app_secret', shared_secret)
        return True
    else:
        return bool(shared_secret) and (req.cookies.get('app_secret') == shared_secret)


def edit_auth_required(f):
    "Decorates f to raise an HTTP UNAUTHORIZED exception if the auth check fails."
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not check_auth(request):
            abort(401)
        return f(*args, **kwargs)
    return wrapped

# TODO: add function for viewing auth
