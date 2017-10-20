#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Database module'''

import ast
import logging
import sqlite3
import yaml

from zonkylla.core.utils import iso2datetime


class Database:
    '''Connection with sqlite3 database'''

    def __init__(self):
        '''Init the connection'''

        self.logger = logging.getLogger('zonkylla.Database')
        self.database = './zonkylla.db'
        self.connection = sqlite3.connect(self.database)

        with open('./data/tables.yaml', 'r') as stream:
            self.schema = yaml.load(stream)

        self._create()

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
        except:
            raise TypeError(table, key, value)

    def _create_sql_cmd(self, table):
        '''Return create SQL command'''

        cmd = 'CREATE TABLE IF NOT EXISTS {} (\n'.format(table)
        items = []
        for column_name, column_type in self.schema[table]['columns'].items():

            col_type = column_type.upper()
            if column_type == 'bool':
                col_type = 'int'

            items += ['{} {}'.format(column_name, col_type)]

        cmd += '\t' + ',\n\t'.join(items) + ',\n\t'
        cmd += 'PRIMARY KEY({} {})'.format(
            self.schema[table]['primary_key']['name'],
            self.schema[table]['primary_key']['order'].upper())
        cmd += '\n)'
        return cmd

    def _create(self):
        '''Prepare the structure if doesn't exist'''

        sql_commands = []
        for table in self.schema:
            sql_commands.append(self._create_sql_cmd(table))

        for sql_command in sql_commands:
            self._execute(sql_command)

    def _execute(self, sql, data=None):
        """Executes SQL query with or without data"""
        if data is None:
            many = False
        elif isinstance(data, list):
            many = bool(all(isinstance(member, (tuple, list))
                            for member in data))
        else:
            raise TypeError

        try:
            with self.connection as con:
                con.row_factory = sqlite3.Row
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

    def _insert_or_update(self, table, data):
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
                        "'%s.%s' present in API response but not in DB schema", table, key)
                    continue
                cols.append(key)
                row.append(self._convert_value(table, key, value))

            rows.append((row))
            columns = ', '.join(cols)
            placeholders = ', '.join('?' * len(cols))

        sql = 'INSERT OR REPLACE INTO {}({}) VALUES ({})'.format(
            table, columns, placeholders)
        self._execute(sql, rows)

    def insert_transactions(self, transactions):
        '''Add transactions to the database'''
        self._insert_or_update('a_transactions', transactions)

    def get_last_transaction_date(self):
        '''Get the datetime of last update'''
        sql = 'SELECT MAX(transactionDate) FROM a_transactions'
        result = self._execute(sql).fetchone()
        dt_value = result[0]

        return iso2datetime(dt_value) if dt_value else None

    def insert_loans(self, loans):
        '''Add loans to the database'''
        self._insert_or_update('a_loans', loans)

    def missing_loan_ids(self):
        '''Get loanId of loans which missing in Loans'''

        sql = '''
            SELECT a_transactions.loanId
            FROM a_transactions
            LEFT JOIN a_loans ON a_transactions.loanId = a_loans.id
            WHERE a_loans.id IS NULL
            AND a_transactions.loanId IS NOT NULL
            GROUP BY a_transactions.loanId;
        '''
        results = self._execute(sql).fetchall()
        return list(map(lambda r: r['loanId'], results))

    def insert_loan_investments(self, investments):
        '''Add investments of loan to the database'''
        self._insert_or_update('a_loan_investments', investments)

    def insert_user_investments(self, investments):
        '''Add user's investments to the database'''
        self._insert_or_update('a_investments', investments)

    def insert_user_notifications(self, notifications):
        '''Add user's notifications'''
        self._insert_or_update('a_notifications', notifications)

    def missing_user_notifications_relations(self):  # pylint: disable=invalid-name
        '''Get a_notifications.id, link of notifications without relations'''

        sql = '''
            SELECT a_notifications.id AS nId, a_notifications.link AS nLink
            FROM a_notifications
            LEFT JOIN z_notifications_relations ON a_notifications.id = z_notifications_relations.notificationId
            WHERE z_notifications_relations.notificationId IS NULL
            AND a_notifications.id IS NOT NULL
            GROUP BY a_notifications.id;
        '''
        results = self._execute(sql).fetchall()

        return [{'id': r['nId'], 'link': r['nLink']} for r in results]

    def update_user_notifications_relations(self):  # pylint: disable=invalid-name
        '''Update of user 's notification's relations'''

        loan_link_type = [
            'LOAN_SUCCESS',
            'LOAN_PREPAYMENT',
            'LOAN_DELAY_INVESTOR',
            'BORROWER_HEAL']

        missing_data = self.missing_user_notifications_relations()

        notification_relations = []
        for data in missing_data:
            link = ast.literal_eval(data['link'])
            relation_type = link['type']

            if link['type'] == 'WALLET_INCOMING':
                foreign_id = link['params']['walletId']
                foreign_table = 'wallet'

            elif link['type'] in loan_link_type:
                foreign_id = link['params']['loanId']
                foreign_table = 'a_loans'

            else:
                self.logger.warning(
                    "'%s' is new notification's type, patch is needed",
                    link['type'])
                continue

            notification_relations.append({'notificationId': data['id'],
                                           'relationType': relation_type,
                                           'foreignId': foreign_id,
                                           'foreignTable': foreign_table})

        self._insert_or_update(
            'z_notifications_relations',
            notification_relations)
