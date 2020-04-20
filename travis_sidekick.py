""" Removes any old stale comments and posts the latest plan stdout as a comment """


import time
import os
import sys
import json
import requests
from cryptography.hazmat.backends import default_backend
import jwt

REPO_NAME = os.environ['TRAVIS_REPO_SLUG']
PR = os.environ['TRAVIS_PULL_REQUEST']
APP_ID = os.environ['APP_ID']
INSTALL_ID = os.environ['INSTALL_ID']

PEM_FILE = 'travis-sidekick.2020-04-19.private-key.pem'
CERT = open(PEM_FILE, 'r').read()
CERT_BYTES = CERT.encode()
PRIVATE_KEY = default_backend().load_pem_private_key(CERT_BYTES, None)

def status_check(req):
    """ stdout error code and fail build. """
    print('Code: ', req.status_code)
    print('Content: ', req.json())
    sys.exit(1)

if os.environ['TRAVIS_PULL_REQUEST'] == 'false':
    pass
else:
    EPOCH_TIME = int(time.time())

    PAYLOAD = {
        # issued at time
        'iat': EPOCH_TIME,
        # expiration time
        'exp': EPOCH_TIME + (5 * 60),
        # GitHub App's identifier
        'iss': APP_ID
    }

    WEB_TOKEN = jwt.encode(PAYLOAD, PRIVATE_KEY, algorithm='RS256')

    HEADERS = {"Authorization": "Bearer {}".format(WEB_TOKEN.decode()),
               "Accept": "application/vnd.github.machine-man-preview+json"}
    # for GHE use  https://github.foo.com/api/v3/app. follow the same pattern at other places
    RESPONSE = requests.get(
        'https://api.github.com/app',
        headers=HEADERS)
    if RESPONSE.status_code != 200:
        status_check(RESPONSE)


    RESPONSE = requests.post(
        'https://api.github.com/installations/{}/access_tokens'.format(INSTALL_ID),
        headers=HEADERS)
    if RESPONSE.status_code != 201:
        status_check(RESPONSE)

    TOKEN = RESPONSE.json()['token']
    HEADERS = {"Authorization": "token {}".format(TOKEN)}

    with open('deploy.txt', 'r') as myfile:
        DEPLOY = myfile.read()

    DATA = {"body": DEPLOY}
    ALL_COMMENTS = requests.get(
        'https://api.github.com/repos/' +
        REPO_NAME +
        '/issues/' +
        PR +
        '/comments',
        headers=HEADERS)
    # delete all old comments
    if ALL_COMMENTS.status_code == 200:
        for comment in ALL_COMMENTS.json():
            if comment['user']['login'] == 'travis-sidekick[bot]':
                url = (comment['url'])
                requests.delete(url, headers=HEADERS)
    else:
        status_check(ALL_COMMENTS)

    # post new comment
    RESPONSE = requests.post(
        'https://api.github.com/repos/' +
        REPO_NAME +
        '/issues/' +
        PR +
        '/comments',
        data=json.dumps(DATA),
        headers=HEADERS)
    if RESPONSE.status_code != 201:
        status_check(RESPONSE)
