#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Zonky clients module'''


from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
import logging
from time import sleep
from itertools import chain
from urllib.parse import urljoin
import pkg_resources

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import requests

from .utils import datetime2iso

DEFAULT_WAIT_TIME = 0.1
DEFAULT_PAGE_SIZE = 100


class AbstractClient(metaclass=ABCMeta):
    """Abstract class for Zonky clients"""

    def __init__(self, host):
        self._host = host
        self._headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': self._user_agent,
        }
        self._time_lock = datetime.now()
        self.logger = logging.getLogger('zonkylla.AbstractClient')

    @property
    def zonky_api_version(self):
        """Version of zonky API"""
        return '0.58.0'

    @property
    def _user_agent(self):
        return 'zonkylla/{} ({})'.format(pkg_resources.require('zonkylla')
                                         [0].version, 'https://github.com/celestian/zonkylla')

    def _wait(self):
        '''Wait until time lock is released'''
        while datetime.now() < self._time_lock:
            sleep(DEFAULT_WAIT_TIME)

    def _update_time_lock(self):
        '''Set new time lock'''
        self._time_lock = datetime.now() + timedelta(milliseconds=500)

    def _join_url(self, url_parts):
        '''Join url'''
        return urljoin(self._host, '/'.join(s.strip('/') for s in url_parts))

    def _request(self, method, url, params=None, headers=None):
        """Method for sending of request to Zonky

        :param method:  GET, POST, PATCH, DELETE
        :param url:     url as tuple without base
        :param data:    data
        :return:        json with result
        """

        if params is None:
            params = {}
        if headers is None:
            headers = {}

        headers.update(self._headers)
        headers.setdefault('X-Page', str(0))
        headers.setdefault('X-Size', str(DEFAULT_PAGE_SIZE))

        self._wait()
        response = self._client().request(
            method.lower(),
            self._join_url(url),
            params=params,
            headers=headers,
            **self._additional_params()
        )
        self._update_time_lock()

        result = response.json()

        if 'X-Total' in response.headers:
            xpage = int(headers['X-Page'])
            xsize = int(headers['X-Size'])
            if ((xpage + 1) * xsize) < int(response.headers['X-Total']):
                headers['X-Page'] = str(xpage + 1)
                result = result + self._request(method, url, params, headers)

        self.logger.debug("Result: '%s'", result)
        return result

    @abstractmethod
    def _client(self):
        """Client object"""
        raise NotImplementedError

    def _additional_params(self):  # pylint: disable=no-self-use
        """Additional parameters used when making request"""
        return {}

    def get(self, url, params=None, headers=None):
        """GET Method"""
        return self._request('GET', url, params, headers)

    def post(self, url, params=None, headers=None):
        """POST Method"""
        return self._request('POST', url, params, headers)

    def patch(self, url, params=None, headers=None):
        """PATCH Method"""
        return self._request('PATCH', url, params, headers)

    def delete(self, url, params=None, headers=None):
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
        self._token_url = self._join_url(('oauth', 'token'))
        self._scope = ['SCOPE_APP_WEB']
        self._token_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'User-Agent': self._user_agent,
        }

        self.logger = logging.getLogger('zonkylla.OAuthClient')

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
            'client_id': self._client_id,
            'client_secret': self._client_secret,
        }


class Client(AbstractClient):
    """Client for Zonky"""

    def __init__(self, host):
        """

        :param host:  URL of Zonky
        """

        AbstractClient.__init__(self, host)
        self.logger = logging.getLogger('zonkylla.Client')

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
        return self._oauth_client.get(('users', 'me', 'wallet'))

    def get_blocked_amounts(self):
        """Blocked amounts"""
        return self._oauth_client.get(
            ('users', 'me', 'wallet', 'blocked-amounts'))

    def get_transactions(self, from_dt=None):
        """List of transactions"""
        params = {}
        headers = {}

        if from_dt:
            params['transaction.transactionDate__gte'] = datetime2iso(from_dt)

        headers['X-Order'] = 'transaction.transactionDate'

        return self._oauth_client.get(
            ('users', 'me', 'wallet', 'transactions'), params, headers)

    def get_loans(self):
        """List of loans on zonky"""
        return self._client.get(('loans', 'marketplace'))

    def get_loan(self, loan_id):
        """Detail of loan"""
        return self._client.get(('loans', str(loan_id)))

    def get_loan_investments(self, loan_id):
        """Loan's investments"""
        params = {}
        headers = {}

        headers['X-Order'] = 'timeCreated'

        return self._oauth_client.get(
            ('loans', str(loan_id), 'investments'), params, headers)

    def get_user_investments(self):
        """User's investments"""
        params = {}
        headers = {}

        headers['X-Order'] = 'timeCreated'

        return self._oauth_client.get(
            ('users', 'me', 'investments'), params, headers)

    def get_user_notifications(self):
        '''User's notifications'''

        params = {}
        headers = {}

        return self._oauth_client.get(
            ('users', 'me', 'notifications'), params, headers)

    def update(self, database):
        '''Update all data for user from zonky'''

        last_dt = database.get_last_transaction_date()

        print('# Download wallet')
        database.insert_wallet([self.get_wallet()])

        print('# Download blocked amounts')
        database.insert_blocked_amounts(self.get_blocked_amounts())

        print('# Update transactions')
        database.insert_transactions(self.get_transactions(from_dt=last_dt))

        print('# Download missing loans')
        loan_ids = database.missing_loan_ids()
        missing_loans = [self.get_loan(loan_id) for loan_id in loan_ids]
        database.insert_loans(missing_loans)

        print('# Download loan investments')
        loan_investments = list(chain.from_iterable(
            [self.get_loan_investments(loan_id) for loan_id in loan_ids]))
        database.insert_loan_investments(loan_investments)

        print('# Download user investments')
        database.insert_user_investments(self.get_user_investments())

        print('# Download user notifications')
        database.insert_user_notifications(self.get_user_notifications())

        print('# Calculate notification relations')
        database.update_user_notifications_relations()
