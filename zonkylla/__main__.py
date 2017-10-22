#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

"""zonkylla
Usage:
  zonkylla.py [-t] [-d] update <user>
  zonkylla.py [-d] loans
  zonkylla.py [-d] loan-investments
  zonkylla.py [-d] user-investments
  zonkylla.py [-d] transactions
  zonkylla.py [-d] notifications
  zonkylla.py (-h | --help)
  zonkylla.py --api-version
  zonkylla.py --version
Options:
  -t             Connect to mock server.
  -d             Debugging output.
  -h --help      Show this screen.
  --api-version  Show version of supported zonky.cz API version.
  --version      Show version.
"""


import os
import getpass
import sys
import logging
from docopt import docopt
import pkg_resources

from .core.zonky import Zonky
from .update import update_from_zonky
from .core.models import Loan, LoanInvestment, UserInvestment, Transaction, Notification


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
