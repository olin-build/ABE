import os
import time
from uuid import uuid4

import jwt

ADMIN_EMAILS = os.environ.get('ADMIN_EMAILS', '').split(',')

# Default to an instance-specific secret for development and testing.
AUTH_TOKEN_SECRET = os.environ.get("AUTH_TOKEN_SECRET", uuid4().hex)

AUTHENTICATED_USER_CLAIMS = [
    'create:events', 'edit:events', 'delete:events',
    'create:ics',
    'read:all_events',
    'read:labels',
]

ADMIN_USER_CLAIMS = AUTHENTICATED_USER_CLAIMS + [
    'create:protected_events', 'edit:protected_events', 'delete:protected_events',
    'create:labels', 'edit:labels', 'delete:labels',
    'admin:apps',
]


def create_access_token(**params):
    payload = {}
    payload.update(params)
    payload.update({'iat': int(time.time())})
    token = jwt.encode(payload, AUTH_TOKEN_SECRET, algorithm='HS256').decode()
    return token


def get_access_token_provider(token):
    if is_valid_token(token):
        payload = jwt.decode(token.encode(), AUTH_TOKEN_SECRET, algorithms='HS256')
        return payload.get('provider')
    return None


def get_access_token_role(token):
    if is_valid_token(token):
        payload = jwt.decode(token.encode(), AUTH_TOKEN_SECRET, algorithms='HS256')
        return 'admin' if payload.get('email') in ADMIN_EMAILS else 'user'
    return None


def get_access_token_scope(token):
    # The scope is computed based on the token's role, so that tokens stay
    # valid if the role -> scope map changes.
    scope = []
    if is_valid_token(token):
        role = get_access_token_role(token)
        # TODO: limit claims by app scope
        scope = ADMIN_USER_CLAIMS if role == 'admin' else AUTHENTICATED_USER_CLAIMS
    return scope


def is_valid_token(token):
    if not token:
        return False
    enc = token.encode()
    try:
        jwt.decode(enc, AUTH_TOKEN_SECRET, algorithms='HS256')  # for effect
    except Exception:
        return False
    return True
