#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Data update by zonky'''

from .core.zonky import Zonky
from .core.database import Database


def update_by_zonky(host, username, password):
    """Update all data (wallet, loans) for user by zonky"""

    zonky = Zonky(host, username, password)
    transactions = zonky.get_transactions()
    database = Database()
    database.insert_transactions(transactions)
