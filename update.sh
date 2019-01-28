#!/bin/bash

cd /home/cpi/launcher 
feh --bg-center /home/cpi/launcher/sys.py/gameshell/wallpaper/updating.png
git pull
git reset --hard $1
git submodule init
git submodule update
feh --bg-center /home/cpi/launcher/sys.py/gameshell/wallpaper/loading.png 
./load.sh

