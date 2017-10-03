#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Database module'''

import sqlite3

from zonkylla.core.utils import iso2datetime


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
                        transactionDate DATETIME,
                        PRIMARY KEY(id ASC)
                    )
                ''')

                con.execute('''
                    CREATE TABLE IF NOT EXISTS Loans (
                        id INT,
                        url TEXT,
                        name TEXT,
                        story TEXT,
                        purpose INT,
                        photos TEXT,
                        userId INT,
                        nickName TEXT,
                        termInMonths INT,
                        interestRate REAL,
                        rating TEXT,
                        topped INT,
                        amount REAL,
                        remainingInvestment REAL,
                        investmentRate REAL,
                        covered INT,
                        datePublished DATETIME,
                        published INT,
                        deadline DATETIME,
                        investmentsCount INT,
                        questionsCount INT,
                        region INT,
                        mainIncomeType TEXT,
                        PRIMARY KEY(id ASC)
                    )
                ''')
        except sqlite3.Error as err:
            print("sqlite3.Error occured: {}".format(err.args))

    def insert_transactions(self, transactions):
        '''Add transactions to the database'''

        data = []
        for item in transactions:

            #dt_struct = iso2datetime()

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
