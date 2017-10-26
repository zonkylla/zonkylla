zonkylla
========

[![Build Status](https://travis-ci.org/celestian/zonkylla.svg?branch=master)](https://travis-ci.org/celestian/zonkylla) [![Code Climate](https://codeclimate.com/github/celestian/zonkylla/badges/gpa.svg)](https://codeclimate.com/github/celestian/zonkylla)

Tool for zonky.cz

Preparation
-----------

-   [Fedora 26](doc/prepare_f26.md)

Usage
-----

-   Run

    ``` bash
    $ virtualenv-3.6 venv
    $ source venv/bin/activate
    $ python setup.py install
    $ zonkylla
    $ deactivate
    ```

-   Testing run with mock

    ``` bash
    echo 'test' | python -m zonkylla -t test
    ```

Resources
---------

-   <http://docs.zonky.apiary.io>
-   <http://pre-commit.com>
-   <http://docs.python-requests.org/en/master/>
-   <https://requests-mock.readthedocs.io/en/latest/>
-   <http://requests-oauthlib.readthedocs.io/en/latest/index.html>
-   <https://sqlite.org/lang.html>
