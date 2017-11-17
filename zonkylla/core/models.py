#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Models module'''

from abc import ABCMeta
import logging

from .database import DBModelerClient


class AbstractModel(metaclass=ABCMeta):
    '''Abstract model'''

    database = DBModelerClient()
    logger = logging.getLogger('zonkylla.Models.AbstractModel')

    _get_one_database_method_name = None
    _get_all_database_method_name = None

    @classmethod
    def all(cls):
        '''Returns all records from DB'''
        return [cls(data) for data in cls._load_all()]

    @classmethod
    def find(cls, record_id):
        '''Returns one records from DB by it's ID'''
        return cls(cls._load_one(record_id))

    @classmethod
    def _load_all(cls):
        db_result = cls._get_all_database_method()()

        result_all = []

        for row in db_result:
            result_data = {}
            for key in list(row.keys()):
                result_data[key] = row[key]
            result_all.append(result_data)

        return result_all

    @classmethod
    def _load_one(cls, record_id):
        db_result = cls._get_one_database_method()(record_id)

        result_data = {}
        for key in list(db_result.keys()):
            result_data[key] = db_result[key]

        return result_data

    @classmethod
    def _get_one_database_method(cls):
        method_name = cls._get_one_database_method_name
        if method_name is None:
            raise NotImplementedError
        return getattr(cls.database, method_name)

    @classmethod
    def _get_all_database_method(cls):
        method_name = cls._get_all_database_method_name
        if method_name is None:
            raise NotImplementedError
        return getattr(cls.database, method_name)

    def __init__(self, data):
        self.logger = logging.getLogger(
            'zonkylla.Models.{}'.format(type(self).__name__))

        self.logger.debug('Initializing %s with ID: %s',
                          type(self).__name__, data['id'])

        self.__dict__ = data

    def __str__(self):
        result = ''
        result += type(self).__name__ + ':\n'
        for key, value in self.__dict__.items():
            result += key + ': ' + str(value) + '\n'
        return result


class Loan(AbstractModel):
    '''Loan model'''

    _get_one_database_method_name = 'get_loan'
    _get_all_database_method_name = 'get_loans'

    def __init__(self, data):
        '''Init Loan using id'''
        AbstractModel.__init__(self, data)


class LoanInvestment(AbstractModel):
    '''LoanInvestment model'''

    _get_one_database_method_name = 'get_loan_investment'
    _get_all_database_method_name = 'get_loan_investments'

    def __init__(self, data):
        '''Init LoanInvestment using id'''
        AbstractModel.__init__(self, data)


class UserInvestment(AbstractModel):
    '''UserInvestment model'''

    _get_one_database_method_name = 'get_user_investment'
    _get_all_database_method_name = 'get_user_investments'

    def __init__(self, data):
        '''Init UserInvestment using id'''
        AbstractModel.__init__(self, data)


class Transaction(AbstractModel):
    '''Transaction model'''

    _get_one_database_method_name = 'get_transaction'
    _get_all_database_method_name = 'get_transactions'

    def __init__(self, data):
        '''Init Transaction using id'''
        AbstractModel.__init__(self, data)


class Notification(AbstractModel):
    '''Notification model'''

    _get_one_database_method_name = 'get_notification'
    _get_all_database_method_name = 'get_notifications'

    def __init__(self, data):
        '''Init Notification using id'''
        AbstractModel.__init__(self, data)
