#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Zonky clients module'''


from abc import ABCMeta, abstractmethod
from time import sleep
import pkg_resources

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import requests

from .utils import datetime2iso


class AbstractClient(metaclass=ABCMeta):
    """Abstract class for Zonky clients"""

    def __init__(self, host):
        self._host = host
        self._headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': self._user_agent,
        }

    @property
    def zonky_api_version(self):
        """Version of zonky API"""
        return '0.58.0'

    @property
    def _user_agent(self):
        return 'zonkylla/{} ({})'.format(pkg_resources.require('zonkylla')
                                         [0].version, 'https://github.com/celestian/zonkylla')

    def _request(self, method, url, params={}, headers={}):
        """Method for sending of request to Zonky

        :param method:  GET, POST, PATCH, DELETE
        :param url:     complete url
        :param data:    data
        :return:        json with result
        """
        headers.update(self._headers)
        headers.setdefault('X-Page', str(0))
        headers.setdefault('X-Size', str(10))

        req = self._client().request(
            method.lower(),
            '{}{}'.format(self._host, url),
            params=params,
            headers=headers,
            **self._additional_params()
        )

        result = req.json()

        if 'X-Total' in req.headers:
            if ((int(headers['X-Page']) + 1) *
                    int(headers['X-Size'])) < int(req.headers['X-Total']):
                headers['X-Page'] = str(int(headers['X-Page']) + 1)
                result = result + self._request(method, url, params, headers)
                sleep(0.3)

        return result

    @abstractmethod
    def _client(self):
        """Client object"""
        raise NotImplementedError

    def _additional_params(self): # pylint: disable=no-self-use
        """Additional parameters used when making request"""
        return {}

    def get(self, url, params={}, headers={}):
        """GET Method"""
        return self._request('GET', url, params, headers)

    def post(self, url, params={}, headers={}):
        """POST Method"""
        return self._request('POST', url, params, headers)

    def patch(self, url, params={}, headers={}):
        """PATCH Method"""
        return self._request('PATCH', url, params, headers)

    def delete(self, url, params={}, headers={}):
        """DELETE Method"""
        return self._request('DELETE', url, params, headers)


class OAuthClient(
        AbstractClient):  # pylint: disable=too-many-instance-attributes
    """OAuth Client for Zonky"""

    def __init__(self, host, username, password):
        """OAuth Client
        :param host: URL of Zonky
        :param username: Username of Zonky user
        :param password: Password of Zonky user
        """

        AbstractClient.__init__(self, host)
        self._client_id = 'web'
        self._client_secret = 'web'
        self._token_url = '{}/oauth/token'.format(self._host)
        self._scope = ['SCOPE_APP_WEB']
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
        """Save token

        If you would like to save token to secret place for next use
        you need to do here. Question is -- What is really secret place?

        :param token:
        """
        self._session.token = token

    def _client(self):
        return self._session

    def _additional_params(self):
        return {
            'client_id'    : self._client_id,
            'client_secret': self._client_secret,
        }


class Client(AbstractClient):
    """Client for Zonky"""

    def __init__(self, host):
        """

        :param host:  URL of Zonky
        """

        AbstractClient.__init__(self, host)

    def _client(self):
        return requests


class Zonky:
    """Testing class"""

    def __init__(self, host, username=None, password=None):
        """Interface to zonky API

        :param host:
        :param username:
        :param password:
        """

        self._client = Client(host)

        if username and password:
            self._oauth_client = OAuthClient(host, username, password)
        else:
            self._oauth_client = None

    @property
    def zonky_api_version(self):
        """Version of zonky API"""
        return self._client.zonky_api_version

    def get_wallet(self):
        """Wallet"""
        return self._oauth_client.get('/users/me/wallet')

    def get_transactions(self, from_dt=None):
        """List of transactions"""
        params = {}
        headers = {}

        if from_dt:
            params['transaction.transactionDate__gte'] = datetime2iso(from_dt)

        headers['X-Order'] = 'transaction.transactionDate'

        return self._oauth_client.get(
            '/users/me/wallet/transactions', params, headers)

    def get_loans(self):
        """List of loans on zonky"""
        return self._client.get('/loans/marketplace')

    def get_loan(self, loan_id):
        """Detail of loan"""
        return self._client.get('/loans/{}'.format(loan_id))
