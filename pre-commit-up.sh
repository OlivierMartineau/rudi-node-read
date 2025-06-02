#!/bin/bash

echo "----- Activating venv"
VENV_DIR=.venv
python3.12 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

if [ $? -eq 0 ]; then
    echo 'DONE: venv activated'
else
    echo 'ERR: venv could not be activated, exiting.'
    exit 1
fi
alias python=$VENV_DIR/bin/python3
alias pip=$VENV_DIR/bin/pip3

echo "----- Updating the tool libraries"
pip install --upgrade pip setuptools wheel
pip install --upgrade pip-chill pip-upgrade-outdated pre-commit
pip install -r requirements-dev.txt

echo "----- Updating the libraries installed"
# pip list --outdated --format=json | jq '.[].name' | xargs -n1 pip install -U
pip_upgrade_outdated
if [ $? -eq 0 ]; then
    echo 'DONE: all libraries updated.'
else
    echo 'ERR: lib update failed, exiting.'
    exit 1
fi

echo "----- Upgrading pre-commit"
pre-commit autoupdate
if [ $? -eq 0 ]; then
    echo 'DONE: "pre-commit" lib and hooks were updated.'
else
    echo 'ERR: "pre-commit" lib update failed, exiting.'
    exit 1
fi

pip-chill >requirements-dev.txt
if [ $? -eq 0 ]; then
    echo 'DONE: every library installed is listed in the requirements.'
else
    echo 'ERR: libraries listing failed, exiting.'
    exit 1
fi

echo "----- Pre-commit checks"
pre-commit run --all-files
if [ $? -eq 0 ]; then
    echo 'DONE: pre-commit actions were executed.'
else
    echo 'ERR: pre-commit action sequence failed, exiting.'
    exit 1
fi

echo "----- The end"
echo "Mise à jour des dépendances terminée."
