"""This module defines a decorator to control access to routing methods."""

import os
from functools import wraps

from flask import request, abort
from netaddr import IPNetwork, IPSet

INTRANET_IPS = (IPSet([IPNetwork(s) for s in os.environ.get('INTRANET_IPS', '').split(',')])
    if 'INTRANET_IPS' in os.environ else IPSet(['0.0.0.0/0', '0000:000::/0']))
"""A set of IP addresses with edit permission.

If the INTRANET_IPS environment variable is set it is be a comma-separated list of CDIR blocks e.g.
`192.168.100.14/24` (IPv4) or `2001:db8::/48` (IPv6).

If the INTRANET_IPS environment variable is not set, this defaults to the entire range of IP addresses.
"""

def edit_auth_required(f):
    "Decorates f to raise an HTTP UNAUTHORIZED exception if the client IP is not in the list of authorized IPs."
    @wraps(f)
    def wrapped(*args, **kwargs):
        client_ip = request.headers.get(
            'X-Forwarded-For', request.remote_addr).split(',')[-1]
        if client_ip not in INTRANET_IPS:
            abort(401)
        return f(*args, **kwargs)
    return wrapped
