#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Database module'''

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

    def _create_sql_cmd(self, table):
        '''Return create SQL command'''

        cmd = 'CREATE TABLE IF NOT EXISTS {} (\n'.format(table)
        items = []
        for column_name, column_type in self.schema[table]['columns'].items():
            items += ['{} {}'.format(column_name, column_type.upper())]
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

    def insert_transactions(self, transactions):
        '''Add transactions to the database'''

        if not transactions:
            return

        data = []
        for item in transactions:
            data.append((
                item['id'],
                item['amount'],
                item['category'],
                item['customMessage'],
                item['loanId'],
                item['loanName'],
                item['nickName'],
                item['orientation'],
                item['transactionDate']))

        sql = '''
            INSERT OR REPLACE INTO Transactions(
                id,
                amount,
                category,
                customMessage,
                loanId,
                loanName,
                nickName,
                orientation,
                transactionDate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        self._execute(sql, data)

    def get_last_transaction_date(self):
        '''Get the datetime of last update'''
        sql = 'SELECT MAX(transactionDate) FROM Transactions'
        result = self._execute(sql).fetchone()
        dt_value = result[0]

        return iso2datetime(dt_value) if dt_value else None

    def insert_loans(self, loans):
        '''Add loans to the database'''

        if not loans:
            return

        rows = []
        for loan in loans:
            row = []
            cols = []

            for key, value in loan.items():

                if key in ['myOtherInvestments']:
                    continue

                cols.append(key)

                if key == 'photos':
                    value = str(value)

                if key in ['topped', 'covered', 'published']:
                    value = 1 if value else 0

                if key in ['region', 'purpose']:
                    value = int(value)

                row.append(value)

            rows.append((row))
            columns = ', '.join(cols)
            placeholders = ', '.join('?' * len(cols))

        sql = 'INSERT OR REPLACE INTO Loans({}) VALUES ({})'.format(
            columns, placeholders)
        self._execute(sql, rows)

    def missing_loan_ids(self):
        '''Get loanId of loans which missing in Loans'''

        sql = '''
            SELECT Transactions.loanId
            FROM Transactions
            LEFT JOIN Loans ON Transactions.loanId = Loans.id
            WHERE Loans.id IS NULL
            AND Transactions.loanId IS NOT NULL
            GROUP BY Transactions.loanId;
        '''
        results = self._execute(sql).fetchall()
        return list(map(lambda r: r['loanId'], results))

    def insert_loan_investments(self, investments):
        '''Add investments of loan to the database'''

        if not investments:
            return

        rows = []
        for investment in investments:
            row = []
            cols = []

            for key, value in investment.items():
                cols.append(key)
                row.append(value)

            rows.append((row))
            columns = ', '.join(cols)
            placeholders = ', '.join('?' * len(investment.keys()))

        sql = 'INSERT OR REPLACE INTO LoanInvestments({}) VALUES ({})'.format(
            columns, placeholders)
        self._execute(sql, rows)
