#!/bin/bash

pip-chill -v > requirements-dev.txt
if [ $? -eq 0 ]; then
    echo 'DONE: every library installed is listed in the requirements.'
else
    echo 'ERR: libraries listing failed, exiting.'
fi

pip list --outdated --format=json | jq '.[].name' | xargs -n1 pip install -U
if [ $? -eq 0 ]; then
    echo 'DONE: all libraries updated.'
else
    echo 'ERR: lib update failed, exiting.'
fi

pre-commit autoupdate
if [ $? -eq 0 ]; then
    echo 'DONE: "pre-commit" lib and hooks were updated.'
else
    echo 'ERR: "pre-commit" lib update failed, exiting.'
fi

pre-commit run --all-files
if [ $? -eq 0 ]; then
    echo 'DONE: pre-commit actions were executed.'
else
    echo 'ERR: pre-commit action sequence failed, exiting.'
fi
