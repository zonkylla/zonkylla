#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Database module'''

from abc import ABCMeta
import ast
import sys
import logging

from zonkylla.abstract.abs_database import Database


class DatabaseClient(metaclass=ABCMeta):
    '''Connection with sqlite3 database'''

    def __init__(self):
        '''Init the connection'''

        self.logger = logging.getLogger('zonkylla.core.DatabaseClient')
        self.dbase = Database()

    @property
    def last_update(self):
        '''Last update of database'''
        return self.dbase.last_update

    def check_if_exists(self):
        '''Check if DB exists'''
        return self.dbase.db_exists

    def check_db_version(self):
        '''Check DB version'''
        self.dbase.check_db_version()

    def get_loan(self, loan_id):
        '''Returns a loan data'''
        return self.dbase.get_one('a_loans', loan_id)

    def get_loan_investments(self, loan_investment_ids=None):
        '''Returns multiple loan investments data'''
        return self.dbase.get_all('a_loan_investments', loan_investment_ids)


class DBCreator(DatabaseClient):
    '''Creator of database'''

    def __init__(self):
        DatabaseClient.__init__(self)
        self.check_if_exists()

    def create_if_not_exist(self):
        '''Create DB if not exists'''
        if self.dbase.db_exists:
            self.dbase.check_db_version()
        else:
            self.dbase.create()


class DBUpdaterClient(DatabaseClient):
    '''Updater database client'''

    def __init__(self):
        DatabaseClient.__init__(self)
        if not self.check_if_exists():
            self.logger.warning(
                "Missing database file '%s', run 'zonkylla init', please.",
                self.dbase.db_file)
            sys.exit(1)

    def prepare_for_data_update(self):
        '''Prepare DB for data update
           ...it drop some tables if it is necessary
        '''
        self.dbase.clear_table('a_wallet')
        self.dbase.clear_table('a_blocked_amounts')

    def mark_update(self):
        '''Mark that database was updated'''
        self.dbase.mark_update()

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
            'BORROWER_HEAL',
            'LOAN_PENALTY_PAID',
        ]

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


class DBModelerClient(DatabaseClient):
    '''Modeler database client'''

    def __init__(self):
        DatabaseClient.__init__(self)
        self.dbase.can_be_empty = False

    def get_loans(self, loan_ids=None):
        '''Returns multiple loans data'''
        return self.dbase.get_all('a_loans', loan_ids)

    def get_loan_investment(self, loan_investment_id):
        '''Returns a loan investment data'''
        return self.dbase.get_one('a_loan_investments', loan_investment_id)

    def get_user_investment(self, user_investment_id):
        '''Returns a user investment data'''
        return self.dbase.get_one('a_user_investments', user_investment_id)

    def get_user_investments(self, user_investment_ids=None):
        '''Returns multiget_user investments data'''
        return self.dbase.get_all('a_user_investments', user_investment_ids)

    def get_transaction(self, transaction_id):
        '''Returns a transaction data'''
        return self.dbase.get_one('a_transactions', transaction_id)

    def get_transactions(self, transaction_ids=None):
        '''Returns multiple transactions data'''
        return self.dbase.get_all('a_transactions', transaction_ids)

    def get_notification(self, notification_id):
        '''Returns a notification data'''
        return self.dbase.get_one('a_notifications', notification_id)

    def get_notifications(self, notification_ids=None):
        '''Returns multiple notifications data'''
        return self.dbase.get_all('a_notifications', notification_ids)

    def get_wallet(self, wallet_id):
        '''Returns a wallet data'''
        return self.dbase.get_one('a_wallet', wallet_id)

    def get_wallets(self, wallet_ids=None):
        '''Returns multiple wallet data'''
        return self.dbase.get_all('a_wallet', wallet_ids)
