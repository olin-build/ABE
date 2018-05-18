import os
import time
from uuid import uuid4

import jwt

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
