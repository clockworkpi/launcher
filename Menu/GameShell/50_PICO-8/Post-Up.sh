#!/bin/bash

mkdir ~/.lexaloffle

cp -rf pico-8 ~/.lexaloffle

mkdir ~/.lexaloffle/pico-8/carts

ln -s ~/.lexaloffle/pico-8/carts/ ~/games/PICO-8/carts

touch .done

