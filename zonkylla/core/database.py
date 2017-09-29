#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Database module'''

from datetime import datetime
import sqlite3

from zonkylla.core.utils import adapt_datetime, convert_datetime, \
    iso2datetime, datetime2tz


class Database:
    '''Connection with sqlite3 database'''

    def __init__(self):
        '''Init the connection'''

        self.database = './zonkylla.db'

        sqlite3.register_adapter(datetime, adapt_datetime)
        sqlite3.register_converter("DATATIME", convert_datetime)

        self.connection = sqlite3.connect(
            self.database, detect_types=sqlite3.PARSE_DECLTYPES)
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
                        transactionDate DATATIME,
                        timeZone INT,
                        PRIMARY KEY(id ASC)
                    )
                ''')
        except sqlite3.Error as err:
            print("sqlite3.Error occured: {}".format(err.args))

    def insert_transactions(self, transactions):
        '''Add transactions to the database'''

        data = []
        for item in transactions:

            dt_struct = iso2datetime(item['transactionDate'])
            dt_tz = datetime2tz(dt_struct)

            data.append((
                item['id'],
                item['amount'],
                item['category'],
                item['customMessage'],
                item['loanId'],
                item['loanName'],
                item['nickName'],
                item['orientation'],
                dt_struct,
                dt_tz))

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
                        transactionDate,
                        timeZone
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data)
        except sqlite3.Error as err:
            print("sqlite3.Error occured: {}".format(err.args))
