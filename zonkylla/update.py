#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Data update by zonky'''

from .core.utils import datetime2iso
from .core.zonky import Zonky
from .core.database import Database


def update_by_zonky(host, username, password):
    """Update all data (wallet, loans) for user by zonky"""

    database = Database()
    last_dt = database.get_last_transaction_date()
    print(datetime2iso(last_dt))

    zonky = Zonky(host, username, password)
    transactions = zonky.get_transactions()
    database.insert_transactions(transactions)
