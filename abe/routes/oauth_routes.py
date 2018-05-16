import os
from urllib.parse import quote_plus as url_quote_plus
from urllib.parse import urlencode
from uuid import uuid4

import flask
from flask import Blueprint, redirect, render_template, request

import logging
from abe.auth import clear_auth_cookie, create_access_token
from abe.helper_functions.url_helpers import url_add_query_params

SLACK_OAUTH_CLIENT_ID = os.environ.get('SLACK_OAUTH_CLIENT_ID')
SLACK_OAUTH_VALIDATION_CODE = os.environ.get('SLACK_OAUTH_VALIDATION_CODE', str(uuid4()))

profile = Blueprint('oauth', __name__)


@profile.route('/oauth/authorize')
def authorize():
    downstream_redirect_uri = request.args['redirect_uri']
    upstream_redirect_uri = request.url_root + 'oauth/slack'
    state = {
        'state': request.args.get('state', None),
        'validation_code': SLACK_OAUTH_VALIDATION_CODE,
    }
    # Some OAuth servesr require exact callback URL. For these, the downstram
    # redirect_uri should be in the state. For Slack, this prevents the state
    # from being present in the callback (maybe because it is too large?), so
    # place it in the redirect instead.
    if False:
        state['redirect_uri'] = downstream_redirect_uri
    else:
        upstream_redirect_uri += '?redirect_uri=' + url_quote_plus(downstream_redirect_uri)
    oauth_url = "https://slack.com/oauth/authorize?" + urlencode({
        'client_id': SLACK_OAUTH_CLIENT_ID,
        'redirect_uri': upstream_redirect_uri,
        'scope': 'identity.basic',
        'state': flask.json.dumps(state),
    })
    if not SLACK_OAUTH_CLIENT_ID:
        logging.warning("SLACK_OAUTH_CLIENT_ID isn't set")
        oauth_url = "javascript:alert('Set SLACK_OAUTH_CLIENT_ID to enable this feature')"
    return render_template('login.html', oauth_url=oauth_url)


@profile.route('/oauth/deauthorize')
def deauthorize():
    redirect_uri = request.args.get('redirect_uri', '/oauth/authorize')
    clear_auth_cookie()
    return redirect(redirect_uri)


@profile.route('/oauth/slack')
def slack_auth():
    logging.warning('decode %s', request.args['state'])
    state = flask.json.loads(request.args['state'])
    logging.warning('decoded %s', state)
    redirect_uri = state.get('redirect_uri', None) or request.args['redirect_uri']
    if state['validation_code'] != SLACK_OAUTH_VALIDATION_CODE:
        redirect_uri = url_add_query_params(redirect_uri,
                                            error='access_denied',
                                            error_description='Upstream oauth service called back with invalid state'
                                            )
    elif 'error' in request.args:
        return redirect(url_add_query_params(redirect_uri, error=request.args['error']))
    else:
        redirect_uri = url_add_query_params(redirect_uri,
                                            access_token=create_access_token(),
                                            expires_in=str(6 * 30 * 24 * 3600),  # ignored by server
                                            state=state['state'],
                                            token_type='bearer',
                                            )
    return redirect(redirect_uri)
