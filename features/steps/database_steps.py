#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Database steps'''

from behave import given  # pylint: disable=no-name-in-module

from zonkylla.core.config import Config
from zonkylla.core.database import DBCreator
from zonkylla.core.database import DBUpdaterClient


@given(u'we have this data in wallet')
def step_impl(context):
    '''Save data into wallet in database'''

    Config(config_file=context.scenario_config_file)

    empty_database = DBCreator()
    empty_database.create_if_not_exist()

    database = DBUpdaterClient()
    for row in context.table:
        database.insert_wallet([{
            'availableBalance': row['availableBalance'],
            'blockedBalance': row['blockedBalance'],
            'creditSum': row['creditSum'],
        }])
