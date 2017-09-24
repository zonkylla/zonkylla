#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Database module'''

import sqlite3


class Database:
    '''Connection with sqlite3 database'''

    def __init__(self):
        '''Init the connection'''

        self.database = './zonkylla.db'
        self.connection = sqlite3.connect(self.database)
        self._create()

    def _create(self):
        '''Prepare the structure if doesn't exist'''

        try:
            with self.connection as con:
                con = con.cursor()
                con.execute('''
                    CREATE TABLE IF NOT EXISTS Transactions (
                        id INT,
                        amount REAL,
                        category TEXT,
                        customMessage TEXT,
                        loanId INT,
                        loanName TEXT,
                        nickName TEXT,
                        orientation TEXT,
                        transactionDate INT,
                        PRIMARY KEY(id ASC)
                    )
                ''')
        except sqlite3.Error as err:
            print("sqlite3.Error occured: {}".format(err.args))

    def insert_transactions(self, transactions):
        '''Add transactions to the database'''

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
        print(data)

        try:
            with self.connection as con:
                con = con.cursor()
                con.executemany('''
                    INSERT INTO Transactions(
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
