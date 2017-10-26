#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Data update by zonky'''

from .core.zonky import Zonky
from .core.database import DBUpdaterClient


def update_from_zonky(host, username, password):
    """Update all data for user from zonky"""

    zonky = Zonky(host, username, password)
    database = DBUpdaterClient()

    zonky.update(database)
