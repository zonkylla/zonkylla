#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

from behave import given, when, then, step

from zonkylla.core.config import Config
from zonkylla.core.database import DBUpdaterClient
from zonkylla.core.models import Wallet

@given(u'we have this data in wallet')
def step_impl(context):
    Config(config_file=context.config_file)
    db = DBUpdaterClient()
    db.create_if_not_exist()
    for row in context.table:
        db.insert_wallet([{
            'availableBalance': row['availableBalance'],
            'blockedBalance': row['blockedBalance'],
            'creditSum': row['creditSum'],
        }])
