#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Zonky clients module'''


import json
from abc import ABCMeta, abstractmethod
import pkg_resources

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth


class ABCClient(metaclass=ABCMeta):
    """Abstract class for Zonky clients"""

    @abstractmethod
    def _request(self, method, url, data):
        raise NotImplementedError

    @property
    def _user_agent(self):
        return 'zonkylla/{} ({})'.format(pkg_resources.require('zonkylla')
                                         [0].version, 'https://github.com/celestian/zonkylla')


class Client(ABCClient):  # pylint: disable=too-many-instance-attributes
    """OAuth Client for Zonky"""

    def __init__(self, host, username, password):
        """OAuth Client
        :param host: URL of Zonky
        :param username: Username of Zonky user
        :param password: Password of Zonky user
        """
        self._host = host
        self._client_id = 'web'
        self._client_secret = 'web'
        self._token_url = '{}/oauth/token'.format(self._host)
        self._scope = ['SCOPE_APP_WEB']
        self._headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': self._user_agent,
        }
        self._token_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'User-Agent': self._user_agent,
        }

        auth = HTTPBasicAuth(self._client_id, self._client_secret)

        client = LegacyApplicationClient(
            client_id=self._client_id,
        )

        session = OAuth2Session(
            client=client,
            auto_refresh_url=self._token_url,
            token_updater=self._token_saver,
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

    def _token_saver(self, token):
        """

        :param token:
        :return:
        """
        self._session.token = token

    def _request(self, method, url, data=None):
        """Method for sending of request to Zonky

        :param method: 'get',...
        :param url:
        :param data:
        :return:
        """
        return self._session.request(
            method,
            url,
            data=data,
            headers=self._headers,
            client_id=self._client_id,
            client_secret=self._client_secret)

    def get_wallet(self):
        """

        :return:
        """
        url = '{}/users/me/wallet'.format(self._host)
        return self._request('get', url).json()


class Zonky:
    """Testing class"""

    def __init__(self, host, username, password):
        """

        :param host:
        :param username:
        :param password:
        """
        self._client = Client(host, username, password)

    def pretty_print(self, data):  # pylint: disable=no-self-use
        """

        :param data:
        :return:
        """
        print(json.dumps(data, sort_keys=True, indent=2))

    def hello(self):
        """

        :return:
        """
        self.pretty_print(self._client.get_wallet())
