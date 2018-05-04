"""This module defines a decorator to control access to routing methods."""

import os
from functools import wraps

from flask import request, abort, g
from netaddr import IPNetwork, IPSet

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

shared_secret = os.environ.get("SHARED_SECRET", None)


def after_this_request(f):  # For setting cookie
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


def edit_auth_required(f):
    "Decorates f to raise an HTTP UNAUTHORIZED exception if the client IP is not in the list of authorized IPs."
    @wraps(f)
    def wrapped(*args, **kwargs):
        client_ip = request.headers.get(
            'X-Forwarded-For', request.remote_addr).split(',')[-1]
        if client_ip in INTRANET_IPS:
            @after_this_request
            def remember_computer(response):
                response.set_cookie('app_secret', shared_secret)
        else:
            if (not shared_secret) or (request.cookies.get('app_secret') != shared_secret):
                abort(401)
        return f(*args, **kwargs)
    return wrapped
