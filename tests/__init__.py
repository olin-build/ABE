import sys

# flake8: noqa: F401 F403
from .context import *
from . import mock_requests

import abe
from abe import database as db
from abe import sample_data
from abe.app import app
from abe.auth import create_access_token

app.config['TESTING'] = True


admin_access_token = create_access_token(provider='test', email='abe-admin@olin.edu', role='admin')
user_access_token = create_access_token(provider='test', email='user@olin.edu')
