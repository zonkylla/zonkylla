#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

"""zonkylla
Usage:
  zonkylla.py
  zonkylla.py (-h | --help)
  zonkylla.py --version
Options:
 -h --help     Show this screen.
 --version     Show version.
"""

from docopt import docopt
import pkg_resources


def main(args):
    """
    Entry point
    """
    print(args)


if __name__ == '__main__':
    ARGS = docopt(
        __doc__,
        version=pkg_resources.require('zonkylla')[0].version)
    main(ARGS)
