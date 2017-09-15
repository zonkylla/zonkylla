#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

"""zonkylla
Usage:
  zonkylla.py [-t] [-d] <user>
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

from .zonky import Zonky


def main():
    """
    Entry point
    """
    args = docopt(
        __doc__,
        version=pkg_resources.require('zonkylla')[0].version)

    if args['-t']:
        host = 'https://private-anon-212b7e4eaf-zonky.apiary-mock.com'
    else:
        host = 'https://api.zonky.cz'

    if args['-d']:
        logging.basicConfig(level=logging.DEBUG)

    if args['--api-version']:
        zonky = Zonky(host)
        print(zonky.zonky_api_version)
        return

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

    zonky = Zonky(host, username, password)
    zonky.hello()


if __name__ == '__main__':
    main()
