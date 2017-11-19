#!/usr/bin/env bash

# Obtain the path to the work directory
RELATIVE_SOURCE_PATH=`dirname ${BASH_SOURCE[@]}`
SOURCE_PATH=`readlink -f ${RELATIVE_SOURCE_PATH}`

TMP_FILE=`mktemp`

autopep8 --max-line-length=100 --diff -aaa -r ${SOURCE_PATH}/zonkylla/ > ${TMP_FILE}
autopep8 --max-line-length=100 --diff -aaa -r ${SOURCE_PATH}/features/ > ${TMP_FILE}

autopep8 --max-line-length=100 --diff -aaa ${SOURCE_PATH}/setup.py > ${TMP_FILE}

if [ -s ${TMP_FILE} ]
then
    cat ${TMP_FILE}
    rm -f ${TMP_FILE}
    exit 1
else
    rm -f ${TMP_FILE}
    exit 0
fi
