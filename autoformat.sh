#!/usr/bin/env bash

# Obtain the path to the work directory
RELATIVE_SOURCE_PATH=`dirname ${BASH_SOURCE[@]}`
SOURCE_PATH=`readlink -f ${RELATIVE_SOURCE_PATH}`

# Removing of trailing spaces
sed --in-place 's/[[:space:]]\+$//' `find ${SOURCE_PATH} -type f -name '*.md'`
sed --in-place 's/[[:space:]]\+$//' `find ${SOURCE_PATH} -type f -name '*.feature'`

# Reformat all markdown files to markdown_github
for filename in `find ${SOURCE_PATH} -type f -name '*.md'`; do

    pandoc \
        -s \
        --smart \
        -f markdown_github \
        -t markdown_github \
        -o ${filename}.tmp \
        ${filename}

    mv -f ${filename}.tmp ${filename}

done

autopep8 --max-line-length=100 -i -aaa -r ${SOURCE_PATH}/zonkylla/
autopep8 --max-line-length=100 -i -aaa -r ${SOURCE_PATH}/features/

autopep8 --max-line-length=100 -i -aaa ${SOURCE_PATH}/setup.py
