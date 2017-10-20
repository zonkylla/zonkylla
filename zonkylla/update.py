#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Data update by zonky'''

from itertools import chain

from .core.zonky import Zonky
from .core.database import Database


def update_from_zonky(host, username, password):
    """Update all data (wallet, loans) for user from zonky"""

    database = Database()
    last_dt = database.get_last_transaction_date()

    zonky = Zonky(host, username, password)

    print('# Update transactions')
    transactions = zonky.get_transactions(from_dt=last_dt)
    database.insert_transactions(transactions)

    print('# Download missing loans')
    loan_ids = database.missing_loan_ids()
    missing_loans = [zonky.get_loan(loan_id) for loan_id in loan_ids]
    database.insert_loans(missing_loans)

    print('# Download loan investments')
    loan_investments = list(chain.from_iterable(
        [zonky.get_loan_investments(loan_id) for loan_id in loan_ids]))
    database.insert_loan_investments(loan_investments)

    print('# Download user investments')
    user_investments = zonky.get_user_investments()
    database.insert_user_investments(user_investments)

    print('# Download user notifications')
    user_notifications = zonky.get_user_notifications()
    database.insert_user_notifications(user_notifications)

    print('# Calculate notification relations')
    database.update_user_notifications_relations()
