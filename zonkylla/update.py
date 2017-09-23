#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Data update by zonky'''

import json

from .core.zonky import Zonky


def update_by_zonky(host, username, password):
    """Update all data (wallet, loans) for user by zonky"""

    zonky = Zonky(host, username, password)

    wallet = zonky.get_wallet()
    print(json.dumps(wallet, sort_keys=True, indent=2))
