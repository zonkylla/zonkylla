#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Database module'''

import sqlite3
import yaml

from zonkylla.core.utils import iso2datetime


class Database:
    '''Connection with sqlite3 database'''

    def __init__(self):
        '''Init the connection'''

        self.database = './zonkylla.db'
        self.connection = sqlite3.connect(self.database)
        self._create()

    def _create_sql_cmd(self, name, columns, primary_key):  # pylint: disable=no-self-use
        '''Return create SQL command'''

        cmd = 'CREATE TABLE IF NOT EXISTS {} (\n'.format(name)
        items = []
        for column_name, column_type in columns.items():
            items += ['{} {}'.format(column_name, column_type.upper())]
        cmd += '\t' + ',\n\t'.join(items) + ',\n\t'
        cmd += 'PRIMARY KEY({} {})'.format(
            primary_key['name'], primary_key['order'].upper())
        cmd += '\n)'
        return cmd

    def _create(self):
        '''Prepare the structure if doesn't exist'''

        with open('./data/tables.yaml', 'r') as stream:
            tables = yaml.load(stream)

        sql_commands = []
        for table in tables:
            sql_command = self._create_sql_cmd(
                table, tables[table]['columns'], tables[table]['primary_key'])
            sql_commands.append(sql_command)

        for sql_command in sql_commands:
            try:
                with self.connection as con:
                    con = con.cursor()
                    con.execute(sql_command)
            except sqlite3.Error as err:
                print("sqlite3.Error occured: {}".format(err.args))

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

        try:
            with self.connection as con:
                con = con.cursor()
                con.executemany('''
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
                ''', data)
        except sqlite3.Error as err:
            print("sqlite3.Error occured: {}".format(err.args))

    def get_last_transaction_date(self):
        '''Get the datetime of last update'''
        try:
            with self.connection as con:
                con = con.cursor()
                con.execute('SELECT MAX(transactionDate) FROM Transactions')
                dt_value = con.fetchone()[0]
        except sqlite3.Error as err:
            print("sqlite3.Error occured: {}".format(err.args))

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
            placeholders = ', '.join('?' * len(loan.keys()))

        sql = 'INSERT OR REPLACE INTO Loans({}) VALUES ({})'.format(
            columns, placeholders)
        try:
            with self.connection as con:
                con = con.cursor()
                con.executemany(sql, rows)
        except sqlite3.Error as err:
            print("sqlite3.Error occured: {}".format(err.args))

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
        try:
            with self.connection as con:
                con.row_factory = sqlite3.Row
                con = con.cursor()
                results = con.execute(sql).fetchall()
                return list(map(lambda r: r['loanId'], results))
        except sqlite3.Error as err:
            print("sqlite3.Error occured: {}".format(err.args))
