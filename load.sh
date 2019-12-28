#!/bin/bash

BASENAME=$(dirname "$0")

cd "$BASENAME"/sys.py || exit

python run.py
