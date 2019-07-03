# -*- coding: utf-8 -*-

import pygame
#from sys import exit
#import os
#import sys

#from libs import easing
#from datetime import datetime

#from beeprint import pp

## local package import
from constants   import Width,Height


class FullScreen(object):
    _PosX  = 0
    _PosY  = 0
    _Width = Width 
    _Height = Height
    _CanvasHWND  = None
    _HWND        = None

    def __init__(self):
        pass

    def Init(self):
        pass

    def SwapAndShow(self):
        if self._HWND != None:
            self._HWND.blit(self._CanvasHWND,(self._PosX,self._PosY,self._Width,self._Height))
            pygame.display.update()
    
    def Draw(self):
        pass
    
