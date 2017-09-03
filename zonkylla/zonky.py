#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

import datetime
import json
import certifi
import pkg_resources

import urllib3


class Token(object):

    def __init__(self, j):
        self.__dict__ = json.loads(j)
        self.timestamp = datetime.datetime.now()

    def __str__(self):
        return json.dumps(self.__dict__, sort_keys=True, indent=2)


class Zonky(object):

    def __init__(self, url, username, password):

        user_agent = 'zonkylla/{} (https://github.com/celestian/zonkylla)'.format(
            pkg_resources.require('zonkylla')[0].version)
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where(),
            headers=user_agent)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic d2ViOndlYg=='
        }

        payload = {
            'username': username,
            'password': password,
            'grant_type': 'password',
            'scope': 'SCOPE_APP_WEB'}

        request_url = '{}/oauth/token'.format(url)

        response = http.request_encode_url(
            'POST',
            request_url,
            headers=headers,
            fields=payload)
        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            print(json.dumps(data, sort_keys=True, indent=2))
