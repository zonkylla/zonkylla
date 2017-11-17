#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

"""zonkylla
Usage:
  zonkylla.py [-t] [-d] update <user> [--config=CONFIG]
  zonkylla.py [-d] status [--config=CONFIG]
  zonkylla.py [-d] loans [--config=CONFIG]
  zonkylla.py [-d] loan-investments [--config=CONFIG]
  zonkylla.py [-d] user-investments [--config=CONFIG]
  zonkylla.py [-d] transactions [--config=CONFIG]
  zonkylla.py [-d] notifications [--config=CONFIG]
  zonkylla.py (-h | --help)
  zonkylla.py interactive [--config=CONFIG]
  zonkylla.py --api-version
  zonkylla.py --version
Options:
  -t                Connect to mock server.
  -d                Debugging output.
  --config=CONFIG   Database file [default: ./zonkylla.cfg].
  -h --help         Show this screen.
  --api-version     Show version of supported zonky.cz API version.
  --version         Show version.
"""


import os
import getpass
import sys
import logging
from docopt import docopt
import pkg_resources

from .core.config import Config
from .core.zonky import Zonky
from .update import update_from_zonky
from .core.models import Loan, LoanInvestment, UserInvestment, Transaction, Notification, Wallet


def get_host(args):
    """Return host url
       due to argument it could be real or test
    """

    if args['-t']:
        host = 'https://private-anon-212b7e4eaf-zonky.apiary-mock.com'
    else:
        host = 'https://api.zonky.cz'
    return host


def get_password():
    """Obtain password
       a) from environment variable named 'ZONKYLLA_PASSWORD'
       b) by prompt the user
    """

    try:
        password = os.environ['ZONKYLLA_PASSWORD']
    except KeyError:
        if sys.stdin.isatty():
            password = getpass.getpass('Password: ')
        else:
            password = sys.stdin.readline().rstrip()

    return password


def print_list(items=None):
    '''Prints content of a list or do nothing'''
    if items is None:
        return
    elif isinstance(items, list):
        print('---\n'.join([str(item) for item in items]))
    else:
        return


def main():
    """
    Entry point
    """
    args = docopt(
        __doc__,
        version=pkg_resources.require('zonkylla')[0].version)

    host = get_host(args)

    Config(config_file=args['--config'])

    if args['--api-version']:
        zonky = Zonky(host)
        print(zonky.zonky_api_version)
        return

    if args['-d']:
        logging.basicConfig(level=logging.DEBUG)

    if args['update']:

        username = args['<user>']
        password = get_password()

        update_from_zonky(host, username, password)
        return

    if args['status']:

        wallet = Wallet.all()
        if not wallet:
            return

        print(wallet[0])

        print('#', ':' * 79)
        print('#', ':: Status')
        print('#', ':' * 79)
        print('#', ':: | Available Balance :: {} Kč '.format(wallet[0].availableBalance))
        print('#', ':: | Blocked Balance   :: {} Kč '.format(wallet[0].blockedBalance))
        print('#', ':: | Credit Sum        :: {} Kč '.format(wallet[0].creditSum))
        print('#', ':' * 79)

    if args['interactive']:
        import IPython
        IPython.embed()

    if args['loans']:
        items = Loan.all()
        print_list(items)

    if args['loan-investments']:
        items = LoanInvestment.all()
        print_list(items)

    if args['user-investments']:
        items = UserInvestment.all()
        print_list(items)

    if args['transactions']:
        items = Transaction.all()
        print_list(items)

    if args['notifications']:
        items = Notification.all()
        print_list(items)


if __name__ == '__main__':
    main()
