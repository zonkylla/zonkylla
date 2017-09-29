#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license

'''Util module'''

import datetime
import dateutil.parser


def adapt_datetime(dt_struct):
    '''Convert datetime to sqlite3 value'''
    return dt_struct.timestamp()


def convert_datetime(dt_struct_stamp):
    '''Convert sqlite3 value to datetime'''
    return datetime.datetime.fromtimestamp(dt_struct_stamp)


def iso2datetime(iso_date):
    '''Convert ISO datetime format to datetime'''
    return dateutil.parser.parse(iso_date)


def datetime2tz(dt_struct):
    '''Get time zone offset from datetime'''
    return dt_struct.tzinfo.utcoffset(dt_struct).total_seconds()


def add_tz(dt_struct, tz_offset):
    '''Add time zone offset to datetime'''
    dt_tz = dateutil.tz.tzoffset(None, tz_offset)
    return dt_struct.replace(tzinfo=dt_tz)


def datetime2iso(dt_struct):
    '''Convert datetime to ISO datetime format'''
    return dt_struct.isoformat(timespec='milliseconds')
