#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Database module'''

import os
import datetime
import logging
from pathlib import Path
import sqlite3
import sys
import yaml

from zonkylla.core.config import Config
from zonkylla.abstract.singleton_meta import Singleton
from zonkylla.core.utils import iso2datetime

DB_VERSION = 3


class Database(metaclass=Singleton):
    '''Connection with sqlite3 database'''

    def __init__(self):
        '''Init the connection'''

        self.logger = logging.getLogger('zonkylla.Abstract.Database')

        self._schema = None
        self._connection = None
        self._last_update = None
        self._db_file = ''
        self._db_exists = None
        self.can_be_empty = True

    @property
    def schema(self):
        '''Database schema'''
        if not self._schema:
            schema_file = os.path.join(sys.prefix, 'zonkylla', 'data', 'tables.yaml')
            with open(schema_file, 'r') as stream:
                self._schema = yaml.load(stream)
        return self._schema

    @property
    def connection(self):
        '''DB connection which is established when needed'''
        if not self._connection:
            self._connection = sqlite3.connect(self.db_file)
        return self._connection

    @property
    def db_file(self):
        '''Last update of database'''
        if not self._db_file:
            self._db_file = Config().db_file
        return self._db_file

    @property
    def db_exists(self):
        '''Boolean if database file exists'''
        if not self._db_exists:
            self._db_exists = Path(self.db_file).is_file()

        return self._db_exists

    @property
    def last_update(self):
        '''Last update of database'''
        if not self._last_update:
            sql = 'SELECT MAX(updated) AS m_updated FROM z_internals'
            res = self.execute(sql).fetchone()
            last_dt = res['m_updated']
            self._last_update = iso2datetime(last_dt) if last_dt else None

        return self._last_update

    def _check_if_can_be_empty(self):
        if not self.can_be_empty:
            if not self.last_update:
                self.logger.warning(
                    "Empty database '%s', run 'zonkylla update', please.",
                    self.db_file)

    def check_db_version(self):
        '''Check the version of DB'''

        sql = 'SELECT MAX(db_version) AS mdb_version FROM z_internals'
        res = self.execute(sql).fetchone()

        if not res['mdb_version']:
            sql = 'INSERT INTO z_internals (db_version) VALUES (?)'
            self.execute(sql, [(DB_VERSION)])
            return

        if res['mdb_version'] != DB_VERSION:
            self.logger.error(
                "Old version of database schema, remove file '%s', please.",
                self.db_file)
            sys.exit(1)

    def _convert_value(self, table, key, value):
        '''Convert value due to database schema'''

        def convert_bool(value):
            '''Convert bool to str'''

            if 'true' in str(value).lower():
                value = 1
            elif 'false' in str(value).lower():
                value = 0
            elif int(value) == 1:
                value = 1
            elif int(value) == 0:
                value = 0

            return value
            # end of function

        if value is None:
            return None

        value_type = self.schema[table]['columns'][key]

        value_convertion = {
            'text': str,
            'int': int,
            'real': float,
            'bool': convert_bool,
            'datetime': (lambda v: v),
        }

        try:
            return value_convertion[value_type](value)
        except BaseException:
            raise TypeError(table, key, value)

    def _create_sql_cmd(self, table):
        '''Return create SQL command'''

        cmd = 'CREATE TABLE IF NOT EXISTS {} (\n'.format(table)
        items = []

        pk_col_type = 'INTEGER PRIMARY KEY {}'.format(
            self.schema[table]['primary_key']['order'].upper())
        is_autoincrement = self.schema[table]['primary_key']['autoincrement']

        for column_name, column_type in self.schema[table]['columns'].items():

            col_type = column_type.upper()
            if column_type == 'bool':
                col_type = 'INT'

            is_pk = self.schema[table]['primary_key']['name'] == column_name
            is_auto = is_pk and is_autoincrement

            items += ['{} {} {}'.format(column_name,
                                        pk_col_type if is_pk else col_type,
                                        'AUTOINCREMENT' if is_auto else '')]

        cmd += '\t' + ',\n\t'.join(items) + '\n)'

        return cmd

    def create(self):
        '''Prepare the structure if doesn't exist'''

        sql_commands = []
        for table in self.schema:
            sql_commands.append(self._create_sql_cmd(table))

        for sql_command in sql_commands:
            self.execute(sql_command)

    def clear_table(self, table):
        '''Clear given table'''
        sql_command = 'DELETE FROM {}'.format(table)
        self.execute(sql_command)

    def mark_update(self):
        '''Mark that databse was updated'''
        sql = 'INSERT INTO z_internals (updated) VALUES (?)'
        self.execute(sql, [(datetime.datetime.now())])

    def execute(self, sql, data=None):
        """Executes SQL query with or without data"""

        def dict_factory(cursor, row):
            '''Dictionary factory for row_factory'''
            result = {}
            for idx, col in enumerate(cursor.description):
                result[col[0]] = row[idx]
            return result
        # end of function

        if data is None:
            many = False
        elif isinstance(data, list):
            many = bool(all(isinstance(member, (tuple, list))
                            for member in data))
        else:
            raise TypeError

        try:
            with self.connection as con:
                con.row_factory = dict_factory
                con = con.cursor()
                self.logger.debug("Executing '%s'", sql)
                if many:
                    self.logger.debug("with many data: '%s'", data)
                    result = con.executemany(sql, data)
                else:
                    if data:
                        self.logger.debug("with data: '%s'", data)
                        result = con.execute(sql, data)
                    else:
                        result = con.execute(sql)
            return result

        except sqlite3.Error as err:
            print("sqlite3.Error occured: {}".format(err.args))
            raise

    def insert_or_update(self, table, data):
        '''Common insert or update query'''

        if not data:
            return

        rows = []
        for dat in data:
            row = []
            cols = []

            for key, value in dat.items():
                # whitelisting only columns in schema
                if key not in self.schema[table]['columns'].keys():
                    self.logger.warning(
                        "'%s.%s' with value '%s' present in API response but not in DB schema",
                        table,
                        key,
                        value)
                    continue
                cols.append(key)
                row.append(self._convert_value(table, key, value))

            rows.append((row))
            columns = ', '.join(cols)
            placeholders = ', '.join('?' * len(cols))

        sql = 'INSERT OR REPLACE INTO {}({}) VALUES ({})'.format(
            table, columns, placeholders)
        self.execute(sql, rows)

    def get_one(self, table, record_id):
        '''Returns data from one row of a table'''

        self._check_if_can_be_empty()

        select_sql = '*'
        sql = 'SELECT {} FROM {} WHERE id == {}'.format(
            select_sql, table, record_id)
        return self.execute(sql).fetchone()

    def get_all(self, table, record_ids=None):
        '''Returns multiple data from multiple rows of a table'''

        self._check_if_can_be_empty()

        select_sql = '*'
        if isinstance(record_ids, list):
            record_ids_sql = 'WHERE id IN (' + ', '.join(
                [str(record_id) for record_id in record_ids]) + ')'
        else:
            record_ids_sql = ''

        sql = 'SELECT {} FROM {} {}'.format(select_sql, table, record_ids_sql)
        return self.execute(sql).fetchall()
