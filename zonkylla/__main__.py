#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

"""zonkylla
Usage:
  zonkylla.py [-t] <user>
  zonkylla.py (-h | --help)
  zonkylla.py --version
Options:
 -t            Connect to mock server.
 -h --help     Show this screen.
 --version     Show version.
"""


import os
import getpass
import sys
from docopt import docopt
import pkg_resources

from .zonky import Zonky


def main():
    """
    Entry point
    """
    args = docopt(
        __doc__,
        version=pkg_resources.require('zonkylla')[0].version)

    username = args['<user>']
    password = None
    try:
        password = os.environ['ZONKYLLA_PASSWORD']
    except KeyError:
        if sys.stdin.isatty():
            password = getpass.getpass('Password: ')
        else:
            password = sys.stdin.readline().rstrip()

    print(username, 'password is provided' if password else 'password is not provided')

    url = None
    if args['-t']:
        url = 'https://private-anon-212b7e4eaf-zonky.apiary-mock.com'
    else:
        url = 'https://api.zonky.cz'

    zonky = Zonky(url, username, password)
    zonky.hello()


if __name__ == '__main__':
    main()
