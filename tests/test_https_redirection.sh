#!/usr/bin/env bash -eu

# Usage:
#    env FLASK_DEBUG=False python run.py
# In another terminal:
#    ./tests/test_https_redirection.sh
#
# Test HTTPS redirection.
#
# TODO: Move this test to Python so that it can be run as part of the test
# suite. This requires modifying app instantiation to use an app factory
# <http://flask.pocoo.org/docs/0.12/patterns/appfactories/#app-factories>.

function summary {
    if [[ $? == 0 ]]; then
        echo 'all tests passed' 1>&2
    else
        echo 'some tests failed' 1>&2
    fi
}
trap summary EXIT

curl -sv http://0.0.0.0:3000/ -o /dev/null 2>&1 | egrep '< HTTP/1.0 301 MOVED PERMANENTLY'
curl -sv http://0.0.0.0:3000/ -o /dev/null 2>&1 | egrep '< Location: https://0.0.0.0:3000/'

curl -sv http://0.0.0.0:3000/.well-known/invalid-acme-challenge/LoqX -o /dev/null 2>&1 | egrep '< HTTP/1.0 301 MOVED PERMANENTLY'
curl -sv http://0.0.0.0:3000/.well-known/invalid-acme-challenge/LoqX -o /dev/null 2>&1 | egrep '< Location: https://0.0.0.0:3000/'

curl -sv http://0.0.0.0:3000/.well-known/acme-challenge/LoqX -o /dev/null 2>&1 | egrep '< HTTP/1.0 301 MOVED PERMANENTLY' && exit 1 || true
curl -sv http://0.0.0.0:3000/.well-known/acme-challenge/LoqX -o /dev/null 2>&1 | egrep '< Location: https://0.0.0.0:3000/' && exit 1 || true
