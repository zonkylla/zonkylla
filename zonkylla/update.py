#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Data update by zonky'''

from .core.zonky import Zonky
from .core.database import Database


def update_by_zonky(host, username, password):
    """Update all data (wallet, loans) for user by zonky"""

    database = Database()
    last_dt = database.get_last_transaction_date()

    zonky = Zonky(host, username, password)
    transactions = zonky.get_transactions(from_dt=last_dt)
    database.insert_transactions(transactions)

    loan_ids = database.missing_loan_ids()
    missing_loans = list(map(lambda l: zonky.get_loan(l), loan_ids))
    database.insert_loans(missing_loans)
