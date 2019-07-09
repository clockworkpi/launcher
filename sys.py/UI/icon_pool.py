# -*- coding: utf-8 -*- 

import pygame
from pygame.locals import *
from sys import exit
import os
import sys

from skin_manager import MySkinManager
##pool only store surfaces

class IconPool(object):

    _GameShellIconPath = MySkinManager.GiveIcon("gameshell/icons/")
    _Icons = {}
    _Sizes = {}
    def __init__(self):
        self._Icons= {}

    def Init(self):
        
        files = os.listdir(self._GameShellIconPath)
        for i in files:
            if os.path.isfile(self._GameShellIconPath+"/"+i) and i.endswith(".png"):
                keyname = i.split(".")[0]
                self._Icons[keyname] = pygame.image.load(self._GameShellIconPath+"/"+i).convert_alpha()
                self._Sizes[keyname] = self._Icons[keyname].get_size()
    
    def Width(self,keyname):
        if keyname in self._Sizes:
            return self._Sizes[keyname][0]
            
    def Height(self,keyname):
        if keyname in self._Sizes:
            return self._Sizes[keyname][1]
            
    def GiveIconSurface(self,imgname): ## imgname is the png file name without .png
        if imgname in self._Icons: 
            return self._Icons[imgname]
        else:
            icon_file = MySkinManager.GiveIcon("gameshell/icons/"+imgname+".png")
            if os.path.isfile(icon_file):
                keyname = imgname
                self._Icons[keyname] = pygame.image.load(icon_file).convert_alpha()
                self._Sizes[keyname] = self._Icons[keyname].get_size()
                return self._Icons[keyname]
        
        return None # this will cause panic,if not found both in theme and default skin folder
        
##global Handler
MyIconPool = None

def InitMyIconPool():
    global MyIconPool
    if MyIconPool == None:
        MyIconPool = IconPool()

InitMyIconPool()


