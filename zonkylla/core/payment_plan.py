#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Payment plan module'''

from datetime import datetime
from dateutil.relativedelta import relativedelta

from .utils import iso2datetime


class PaymentPlan():
    '''Payment plan class'''

    def __init__(self, amount, interest_rate, term_in_months, start_date=None):
        if start_date is None:
            start_date = datetime.now()

        self._amount = amount
        self._interest_rate = interest_rate
        self._term_in_months = term_in_months
        self._start_date = iso2datetime(start_date)

    @property
    def amount(self):
        '''Amount'''
        return self._amount

    @property
    def interest_rate(self):
        '''Interest rate'''
        return self._interest_rate

    @property
    def term_in_months(self):
        '''Term in months'''
        return self._term_in_months

    @property
    def start_date(self):
        '''Payment start date'''
        return self._start_date

    def period_to_pay_principal(self, step):
        '''Period to pay principal'''
        return self.monthly_payment * (1 / (self.monthly_interest) ** (self.term_in_months - step))

    def period_to_pay_interest(self, step):
        '''Period to pay interest'''
        return self.monthly_payment * \
            (1 - (1 / (self.monthly_interest) ** (self.term_in_months - step)))

    @property
    def payment_calendar(self):
        '''Return payment calendar'''
        return [{
            'payment_number': i + 1,
            'paid_total': (i + 1) * self.monthly_payment,
            'period_to_pay_principal': self.period_to_pay_principal(i),
            'period_to_pay_interest': self.period_to_pay_interest(i),
            'payment_date': self.start_date + relativedelta(months=i),
        } for i in range(0, self.term_in_months + 1)]

    @property
    def monthly_interest(self):
        '''Monthly interest'''
        return 1 + (self.interest_rate / 12.0)

    @property
    def monthly_payment(self):
        '''Return monthly payment'''
        return self.amount * ((self.monthly_interest ** self.term_in_months) *
                              (self.monthly_interest - 1)) / \
            ((self.monthly_interest ** self.term_in_months) - 1)
