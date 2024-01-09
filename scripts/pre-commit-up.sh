#!/bin/bash

pip3 list --outdated --format=json | jq '.[].name' | xargs -n1 pip3 install -U
echo 'DONE: all libraries upgraded'

pre-commit autoupdate
echo 'DONE: pre-commit libraries updated'
