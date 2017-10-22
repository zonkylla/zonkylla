#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Models module'''

from abc import ABCMeta
import logging

from .database import Database


class AbstractModel(metaclass=ABCMeta):
    '''Abstract model'''

    database = Database()
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

        self.logger.debug('Initializing %s with ID: %s', type(self).__name__, data['id'])

        for key in list(data.keys()):
            setattr(self, key, data[key])

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
