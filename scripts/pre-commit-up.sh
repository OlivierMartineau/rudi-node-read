#!/bin/bash

pip list --outdated --format=json | jq '.[].name' | xargs -n1 pip install -U
echo 'DONE: all libraries upgraded'

pre-commit autoupdate
echo 'DONE: pre-commit libraries updated'
