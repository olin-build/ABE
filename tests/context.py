"""Provide context for imports of ABE.
Referenced from The Hitchhiker's Guide to Python.
http://docs.python-guide.org/en/latest/writing/structure/#test-suite
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

MONGODB_TEST_DB_NAME = "abe-unittest"
os.environ["DB_NAME"] = MONGODB_TEST_DB_NAME
os.environ["INTRANET_CDIRS"] = "127.0.0.1/24"
os.environ["MONGODB_URI"] = ""
os.environ['SLACK_OAUTH_CLIENT_ID'] = 'slack-oauth-client-id'

os.environ['ABE_EMAIL_USERNAME'] = 'email-test-user'
os.environ['ABE_EMAIL_PASSWORD'] = 'email-test-password'
os.environ['ABE_EMAIL_HOST'] = 'pop.test.com'
