#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Behave environment'''


def before_all(context):
    '''Setup environemnt before all behaves'''
    context.config_file = 'zonkylla-test.cfg'
    context.cli_options = '--config=' + context.config_file
