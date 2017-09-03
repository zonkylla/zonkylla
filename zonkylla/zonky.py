#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

import datetime
import json
import pkg_resources

import requests


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

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic d2ViOndlYg==',
            'User-Agent': user_agent,
        }

        payload = {
            'username': username,
            'password': password,
            'grant_type': 'password',
            'scope': 'SCOPE_APP_WEB'}

        request_url = '{}/oauth/token'.format(url)

        response = requests.post(request_url, data=payload, headers=headers)
        if response.status_code == requests.codes.ok:  # pylint: disable=no-member
            data = response.json()
            print(json.dumps(data, sort_keys=True, indent=2))
