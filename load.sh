#!/bin/bash

BASENAME=`dirname "$0"`

cd $BASENAME/sys.py

if [ ! -f ~/.apps_menu_updated ]
then
cd ~/apps/Menu && git pull origin gcores
if [ $? -eq 0 ]; then
touch ~/.apps_menu_updated
fi
cd -
fi

python run.py


