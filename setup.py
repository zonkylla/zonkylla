#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  zonkylla Contributors see COPYING for license
#
# Build script for creating package in dist/ directory.
#
# usage:
# python setup.py bdist_egg -- egg package
# python setup.py sdist     -- package for PyPI
#
# install:
# easy_install [-U] dist/<package-name>.egg
# easy_install [-U] <package-name> -i http://path/to/private/index

from setuptools import setup, find_packages


setup(
    name='zonkylla',
    description='Tool for zonky.cz',
    version='0.0.1',
    author='celestian',
    license='GPLv3',
    url='https://github.com/celestian/zonkylla',


    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'zonkylla = zonkylla.__main__:main'
        ]
    },
    install_requires=[
        'docopt',
        'requests',
        'singleton3',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
