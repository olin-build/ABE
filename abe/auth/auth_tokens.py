import os
import time
from uuid import uuid4

import jwt

# For development and testing, default to an instance-specific secret.
AUTH_TOKEN_SECRET = os.environ.get("AUTH_TOKEN_SECRET", uuid4().hex)

AUTHENTICATED_USER_SCOPE = [
    'create:events', 'edit:events', 'delete:events',
    'create:labels', 'edit:labels', 'delete:labels',
    'create:ics',
    'read:all_events',
    # deprecated:
    'events:create', 'events:edit', 'community_events:read',
]

ADMIN_USER_SCOPE = AUTHENTICATED_USER_SCOPE + [
    'create:protected_events', 'edit:protected_events', 'delete:protected_events',
]


def create_auth_token():
    return jwt.encode({'iat': int(time.time())}, AUTH_TOKEN_SECRET, algorithm='HS256').decode()


def get_auth_token_scope(token):
    # The scope is computed based on the token's role, so that tokens stay
    # valid if the role -> scope map changes.
    if is_valid_token(token):
        # TODO: use ADMIN_USER_SCOPE for authenticated admin users
        return AUTHENTICATED_USER_SCOPE
    return []


def is_valid_token(token):
    if not token:
        return False
    enc = token.encode()
    try:
        jwt.decode(enc, AUTH_TOKEN_SECRET, algorithms='HS256')  # for effect
    except Exception:
        return False
    return True
