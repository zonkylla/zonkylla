#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Executable steps'''

import os
import shutil
import subprocess
import sys
from behave import given, when, then  # pylint: disable=no-name-in-module

# pylint: disable=function-redefined


@given(u'we have zonkylla installed')
def step_impl(context):  # pylint: disable=unused-argument
    '''Check if zonkylla is installed'''
    assert shutil.which('zonkylla') is not None


@given(u'we have zonkylla configured properly')
def step_impl(context):
    '''Configure zonkylla'''

    target_config_file = os.path.join(context.scenario_test_dir, 'zonkylla.conf')
    shutil.copyfile(context.base_config_file, target_config_file)


@when(u'we run "{command}"')
def step_impl(context, command):
    '''Run command and print outputs'''

    if context.cli_options:
        command = command + ' ' + context.cli_options

    result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout.decode('utf-8'))
    print(result.stderr.decode('utf-8'), file=sys.stderr)


@then(u'we see "{text}" on stdout')
def step_impl(context, text):
    '''Check if text is on stdout'''
    if 'stdout_capture' in context.__dict__:
        assert text in context.stdout_capture.getvalue()


@then(u'we see "{text}" on stderr')
def step_impl(context, text):
    '''Check if text is on stderr'''
    if 'stderr_capture' in context.__dict__:
        assert text in context.stderr_capture.getvalue()
