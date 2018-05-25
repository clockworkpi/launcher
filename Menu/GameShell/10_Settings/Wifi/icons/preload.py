# -*- coding: utf-8 -*- 

import pygame
from pygame.locals import *
from sys import exit
import os
import sys

from beeprint import pp

ICONS_PRELOAD={}


def load_icons():
    basepath = os.path.dirname(os.path.realpath(__file__))

    files = os.listdir(basepath)
    for i in files:
        if os.path.isfile(basepath+"/"+i) and i.endswith(".png"):
            keyname = i.split(".")[0]
            ICONS_PRELOAD[keyname] = pygame.image.load(basepath+"/"+i).convert_alpha()
