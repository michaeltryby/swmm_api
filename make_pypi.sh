#!/usr/bin/env bash

SCRIPTPATH=$(dirname "$BASH_SOURCE")
cd $SCRIPTPATH

python3 setup.py bdist_wheel
python3 -m twine upload dist/*