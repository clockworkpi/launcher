# -*- coding: utf-8 -*- 
import pygame

from libs.roundrects import aa_round_rect
## local UI import
from UI.constants import Width,Height
from UI.page   import Page,PageSelector
from UI.skin_manager import MySkinManager

class InfoPageSelector(PageSelector):
    _BackgroundColor = MySkinManager.GiveColor('Front')

    def __init__(self):
        self._Width  = Width

    def AnimateDraw(self,x2,y2):
        pass

    def Draw(self):
        idx = self._Parent._PsIndex
        if idx >= 0 and idx < len(self._Parent._MyList):
            y = self._Parent._MyList[idx]._PosY+1
            h = self._Parent._MyList[idx]._Height -3
            
            self._PosY = y
            self._Height = h
            
            aa_round_rect(self._Parent._CanvasHWND,  
                          (self._PosX,self._PosY,self._Width-4,self._Height),self._BackgroundColor,4,0,self._BackgroundColor)
