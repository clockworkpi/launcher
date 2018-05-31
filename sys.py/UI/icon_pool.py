# -*- coding: utf-8 -*- 

import pygame
from pygame.locals import *
from sys import exit
import os
import sys

from util_funcs  import SkinMap
##pool only store surfaces

class IconPool(object):

    _GameShellIconPath = SkinMap("gameshell/icons/")
    _Icons = {}
    def __init__(self):
        self._Icons= {}

    def Init(self):
        
        files = os.listdir(self._GameShellIconPath)
        for i in files:
            if os.path.isfile(self._GameShellIconPath+"/"+i) and i.endswith(".png"):
                keyname = i.split(".")[0]
                self._Icons[keyname] = pygame.image.load(self._GameShellIconPath+"/"+i).convert_alpha()
                

MyIconPool = IconPool()

