#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

import datetime
import time
import json

import requests
import requests_mock

from zonkylla.zonky import OAuthClient


def mock_headers():

    return {
        'Server': 'nginx',
        'Date': datetime.datetime.utcnow().strftime("%a, %d %b %Y %H-%M-%S GMT"),
        'Content-Type': 'application/json;charset=UTF-8',
        'Transfer-Encoding': 'chunked',
        'Connection': 'keep-alive',
        'Keep-Alive': 'timeout=3',
        'Vary': 'Accept-Encoding',
        'Access-Control-Allow-Methods': 'POST, PUT, GET, OPTIONS, DELETE, PATCH',
        'Access-Control-Max-Age': '3600',
        'Access-Control-Allow-Headers': 'origin, x-requested-with, content-type, authorization, x-order, x-size, x-page, x-authorization-code, x-captcha-response, if-none-match',
        'Access-Control-Expose-Headers': 'x-total, x-sms-authorization, www-authenticate, etag',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Cache-Control': 'no-cache, no-store, max-age=0, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'X-Frame-Options': 'DENY',
        'X-Zonky-Req': 'fO0Ne2u6MXLzflSs',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'Content-Security-Policy': "default-src https: 'unsafe-inline' 'unsafe-eval' data: blob:; connect-src 'self' https://api.zonky.cz;",
        'Content-Encoding': 'text/plain; charset=utf-8'}


def test_oauthclient():

    def oauth_token_text_callback(request, context):
        if 'password' in request.text:
            oauth_token_response = json.dumps({
                "access_token": "small_token",
                "token_type": "bearer",
                "refresh_token": "bigger_token",
                "expires_in": 1,
                "scope": 'SCOPE_APP_WEB'})
        else:
            oauth_token_response = json.dumps({
                "access_token": "middle_token",
                "token_type": "bearer",
                "refresh_token": "bigger_token",
                "expires_in": 2,
                "scope": 'SCOPE_APP_WEB'})

        return oauth_token_response

    def get_wallet_text_callback(request, context):
        wallet_response = json.dumps({
            "id": 1,
            "balance": 1000,
            "availableBalance": 900,
            "blockedBalance": 100,
            "creditSum": 20000,
            "debitSum": 0,
            "variableSymbol": "0123456789",
            "account": {
                "id": 1,
                "accountNo": "0000000123456789",
                "accountBank": "6000",
                "accountName": "P2P JUMBO"
            }})

        return wallet_response

    username = 'mock_user@zonky.mock'
    password = 'passw@rd'
    host = 'https://zonky.mock'

    with requests_mock.Mocker() as m:

        mocked_header = mock_headers()
        m.post('{}/oauth/token'.format(host), headers=mocked_header,
               text=oauth_token_text_callback, reason='None')
        m.get('{}/users/me/wallet'.format(host), headers=mocked_header,
              text=get_wallet_text_callback, reason='None')

        oauth_client = OAuthClient(host, username, password)

        time.sleep(2)

        #wallet = oauth_client.get_wallet()
        #assert 900 == wallet['availableBalance']

        for i in range(len(m.request_history)):
            print('[{}] hostname: {}'.format(i, m.request_history[i].hostname))
            print('[{}] port: {}'.format(i, m.request_history[i].port))
            print('[{}] method: {}'.format(i, m.request_history[i].method))
            print('[{}] text: {}'.format(i, m.request_history[i].text))

        assert True
