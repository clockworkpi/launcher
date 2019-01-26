#!/bin/bash

cd /home/cpi/launcher 
feh --bg-center /home/cpi/launcher/sys.py/gameshell/wallpaper/updating.png
git pull
git reset --hard $1
feh --bg-center /home/cpi/launcher/sys.py/gameshell/wallpaper/loading.png 
./load.sh

