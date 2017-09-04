#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

import json
import pkg_resources

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth


USER_AGENT = 'zonkylla/{} ({})'.format(
    pkg_resources.require('zonkylla')[0].version,
    'https://github.com/celestian/zonkylla')


class Client:

    def __init__(self, host, username, password):
        self._host = host
        self._client_id = 'web'
        self._client_secret = 'web'
        self._token_url = '{}/oauth/token'.format(self._host)
        self._scope = ['SCOPE_APP_WEB']
        self._headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT,
        }
        self._token_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'User-Agent': USER_AGENT,
        }

        auth = HTTPBasicAuth(self._client_id, self._client_secret)

        client = LegacyApplicationClient(
            client_id=self._client_id,
        )

        session = OAuth2Session(
            client=client,
            auto_refresh_url=self._token_url,
            token_updater=self.token_saver,
            scope=self._scope,
        )

        session.fetch_token(
            token_url=self._token_url,
            username=username,
            password=password,
            scope=self._scope,
            auth=auth,
            headers=self._token_headers,
        )

        self._session = session

    def token_saver(self, token):
        self._session.token = token

    def request(self, method, url, data=None):
        return self._session.request(
            method,
            url,
            data=data,
            headers=self._headers,
            client_id=self._client_id,
            client_secret=self._client_secret)

    def get_wallet(self):
        url = '{}/users/me/wallet'.format(self._host)
        return self.request('get', url).json()


class Zonky:

    def __init__(self, host, username, password):
        self._client = Client(host, username, password)

    def pretty_print(self, data):
        print(json.dumps(data, sort_keys=True, indent=2))

    def hello(self):
        self.pretty_print(self._client.get_wallet())
