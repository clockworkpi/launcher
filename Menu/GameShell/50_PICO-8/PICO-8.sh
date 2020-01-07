#!/bin/bash

cd /home/cpi/games/PICO-8/pico-8 || exit
SDL_VIDEODRIVER=x11 DISPLAY=:0 ./pico8_dyn -splore -draw_rect 32,0,256,240
