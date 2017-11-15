#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Reports module'''

from .models import UserInvestment
from .payment_plan import PaymentPlan


def upcoming_transactions():
    '''Returns list of dicts with upcoming transactions'''
    calendars = [PaymentPlan(ui).payment_calendar for ui in UserInvestment.all()]

    # flatten nested list of events
    transactions = [item for sublist in calendars for item in sublist]

    transactions.sort(key=lambda t: t['payment_date'])
    return transactions
