#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Database module'''

import ast
import logging

from zonkylla.abstract.abs_database import Database
from zonkylla.core.utils import iso2datetime


class DatabaseClient:
    '''Connection with sqlite3 database'''

    def __init__(self):
        '''Init the connection'''

        self.logger = logging.getLogger('zonkylla.core.DatabaseClient')
        self.dbase = Database()

    def insert_wallet(self, wallet):
        '''Add user's notifications'''
        self.dbase.insert_or_update('a_wallet', wallet)

    def insert_blocked_amounts(self, blocked_amounts):
        '''Add user's notifications'''
        self.dbase.insert_or_update('a_blocked_amounts', blocked_amounts)

    def insert_transactions(self, transactions):
        '''Add transactions to the database'''
        self.dbase.insert_or_update('a_transactions', transactions)

    def insert_loans(self, loans):
        '''Add loans to the database'''
        self.dbase.insert_or_update('a_loans', loans)

    def insert_loan_investments(self, investments):
        '''Add investments of loan to the database'''
        self.dbase.insert_or_update('a_loan_investments', investments)

    def insert_user_investments(self, investments):
        '''Add user's investments to the database'''
        self.dbase.insert_or_update('a_user_investments', investments)

    def insert_user_notifications(self, notifications):
        '''Add user's notifications'''
        self.dbase.insert_or_update('a_notifications', notifications)

    def get_last_transaction_date(self):
        '''Get the datetime of last update'''
        sql = 'SELECT MAX(transactionDate) FROM a_transactions'
        result = self.dbase.execute(sql).fetchone()
        dt_value = result[0]

        return iso2datetime(dt_value) if dt_value else None

    def get_loan(self, loan_id):
        '''Returns a loan data'''

        select_sql = '*'

        sql = 'SELECT {} FROM a_loans WHERE id == {}'.format(
            select_sql, loan_id)

        return self.dbase.execute(sql).fetchone()

    def get_loans(self, loan_ids=None):
        '''Returns multiple loans data'''

        select_sql = '*'
        if isinstance(loan_ids, list):
            loan_ids_sql = 'WHERE id IN (' + ', '.join(
                [str(loan_id) for loan_id in loan_ids]) + ')'
        else:
            loan_ids_sql = ''

        sql = 'SELECT {} FROM a_loans {}'.format(select_sql, loan_ids_sql)
        result = self.dbase.execute(sql).fetchall()
        return result

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
        results = self.dbase.execute(sql).fetchall()

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

        self.dbase.insert_or_update(
            'z_notifications_relations',
            notification_relations)
