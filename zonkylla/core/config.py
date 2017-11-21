#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Configuration module'''

import configparser
import logging

from zonkylla.abstract.singleton_meta import Singleton


class Config(metaclass=Singleton):
    '''Configuration class'''

    def __init__(self, **kwargs):
        '''Init the configuration'''

        self.logger = logging.getLogger('zonkylla.Core.Config')

        self.config = configparser.ConfigParser()

        readed = False
        for name, value in kwargs.items():
            if name == 'config_file':
                self.config.read(value)
                readed = True

        if readed:
            self.db_file = self.config['zonkylla']['db_file']
        else:
            self.db_file = None
