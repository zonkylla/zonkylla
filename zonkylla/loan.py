#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

from enum import Enum
from datetime import datetime
import yaml


class Rating(Enum):
    AAAAA = 1
    AAAA = 2
    AAA = 3
    AA = 4
    A = 5
    B = 6
    C = 7
    D = 8


class LoanParams(object):
    loan_params_file = "./data/loan_params.yaml"

    def __init__(self):
        with open(self.loan_params_file, 'r') as stream:
            try:
                self.params = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.valid_dates = []
        for param in self.params:
            self.valid_dates.append(param['valid_from'])

    def get_params(self, date, rating):
        period = None
        time_diff = float("inf")

        for dat in self.valid_dates:
            actual_date = datetime.strptime(date, '%Y-%m-%d').date()
            actual_diff = (actual_date - dat).total_seconds()
            if (actual_diff >= 0) and actual_diff < time_diff:
                time_diff = actual_diff
                period = dat

        for param in self.params:
            if param['valid_from'] == period:
                return param[rating]


class Loan(object):

    def __init__(self, rating, start_date, debt, repayment_period):
        self.rating = self._rating(rating)
        self.start_date = start_date
        self.debt = debt
        self.repayment_period = repayment_period

        self.loan_params = LoanParams().get_params(start_date, rating)
        self.total_installment = self.debt * pow(
            (100.0 + self.loan_params['interest']) / 100.0,
            repayment_period / 12.0)

        print(self.total_installment)

    def _rating(self, rating):
        if rating == 'A**':
            return Rating.AAAAA
        if rating == 'A*':
            return Rating.AAAA
        if rating == 'A++':
            return Rating.AAA
        if rating == 'A+':
            return Rating.AA
        if rating == 'A':
            return Rating.A
        if rating == 'B':
            return Rating.B
        if rating == 'C':
            return Rating.C
        if rating == 'D':
            return Rating.D

        #        installment
        #        loss
        #        charge
