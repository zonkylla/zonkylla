#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Configuration module'''

import configparser
import logging
from pathlib import Path
import sys

from zonkylla.abstract.singleton_meta import Singleton


class Config(metaclass=Singleton):
    '''Configuration class'''

    def __init__(self, **kwargs):
        '''Init the configuration'''

        self.logger = logging.getLogger('zonkylla.Core.Config')

        self._db_file = None

        self.config = configparser.ConfigParser()

        for name, value in kwargs.items():
            if name == 'config_file':
                if not Path(value).is_file():
                    self.logger.critical(
                        "Error: Configuration file '%s' doesn't exist!", value)
                    sys.exit(1)

                try:
                    self.config.read(value)
                    self._db_file = self.config['zonkylla']['db_file']
                except KeyError as err:
                    self.logger.error(
                        "KeyError [%s] in configuration file '%s' occured!",
                        err, value)

    @property
    def db_file(self):
        '''Database file'''
        return self._db_file
