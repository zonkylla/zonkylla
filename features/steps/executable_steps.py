#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Executable steps'''

import os
from pathlib import Path
import shutil
import subprocess
import sys
import sqlite3
import yaml
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


@given(u'there is no "{file_name}" file here')
def step_impl(context, file_name):  # pylint: disable=unused-argument
    '''Check the file_name doesn't exist'''

    target_file = Path(file_name)
    if target_file.is_file():
        os.remove(target_file)


@given(u'there is empty file "{file_name}"')
def step_impl(context, file_name):  # pylint: disable=unused-argument
    '''Create empty file'''

    target_file = Path(file_name)
    empty_file = open(target_file, 'w')
    empty_file.close()


@given(u'there is file "{file_name}" with old structure')
def step_impl(context, file_name):  # pylint: disable=unused-argument
    '''Create file with old structure'''

    command = 'zonkylla init'
    if context.cli_options:
        command = command + ' ' + context.cli_options

    result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout.decode('utf-8'))
    print(result.stderr.decode('utf-8'), file=sys.stderr)

    con = sqlite3.connect(file_name)
    with con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("UPDATE z_internals SET db_version = -1 WHERE id = 1")


@given(u'we provided password "{password}"')
def step_impl(context, password):  # pylint: disable=unused-argument
    '''Provide password to environment'''
    os.environ['ZONKYLLA_PASSWORD'] = password


@when(u'we run "{command}"')
def step_impl(context, command):
    '''Run command and print outputs'''

    if context.cli_options:
        command = command + ' ' + context.cli_options

    completed_process = subprocess.run(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    context.return_code = completed_process.returncode
    print(completed_process.stdout.decode('utf-8'))
    print(completed_process.stderr.decode('utf-8'), file=sys.stderr)


@then(u'return code is "{return_code}"')
def step_impl(context, return_code):
    '''Check return code'''
    assert context.return_code == int(return_code)


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


@then(u'file "{file_name}" is created')
def step_impl(context, file_name):  # pylint: disable=unused-argument
    '''Check if file is created'''
    assert Path(file_name).is_file()


@then(u'there is proper database structure within file "{file_name}"')
def step_impl(context, file_name):  # pylint: disable=unused-argument
    '''Check the database structure'''

    schema_file = os.path.join(sys.prefix, 'zonkylla', 'data', 'tables.yaml')
    with open(schema_file, 'r') as stream:
        schema = yaml.load(stream)
        given_names = list(schema.keys())

    con = sqlite3.connect(file_name)
    with con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        rows = cur.fetchall()
        actual_names = [row['name'] for row in rows]

    for name in given_names:
        assert name in actual_names
