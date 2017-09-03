#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

import datetime
import json
import time
import pkg_resources
from singleton3 import Singleton

import requests

user_agent = 'zonkylla/{} ({})'.format(
    pkg_resources.require('zonkylla')[0].version,
    'https://github.com/celestian/zonkylla')


class Token(metaclass=Singleton):

    def __init__(self, url, username, password):
        self._url = url
        self._username = username
        self._password = password

        self._access_token = None
        self._expires_in = None
        self._refresh_token = None
        self._scope = None
        self._token_type = None

        # just testing
        self._get_token(login=True)
        time.sleep(10)
        self._get_token()

    def _get_token(self, login=False):

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic d2ViOndlYg==',
            'User-Agent': user_agent,
        }

        payload = {
            'scope': 'SCOPE_APP_WEB'}

        if login:
            payload['username'] = self._username
            payload['password'] = self._password
            payload['grant_type'] = 'password'
        else:
            payload['refresh_token'] = self._refresh_token
            payload['grant_type'] = 'refresh_token'

        request_url = '{}/oauth/token'.format(self._url)

        response = requests.post(request_url, data=payload, headers=headers)

        if response.status_code == requests.codes.ok:  # pylint: disable=no-member
            data = response.json()
            print(json.dumps(data, sort_keys=True, indent=2))
        else:
            response.raise_for_status()

        self._access_token = data['access_token']
        self._expires_in = data['expires_in']
        self._refresh_token = data['refresh_token']
        self._scope = data['scope']
        self._token_type = ['token_type']


class Zonky(object):

    def __init__(self, url, username, password):

        Token(url, username, password)

        # print(json.dumps(data, sort_keys=True, indent=2))
