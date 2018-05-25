# -*- coding: utf-8 -*- 
import pygame

from util_funcs  import midRect

from libs.roundrects import aa_round_rect

class ListScroller(object):
    _PosX = 0
    _PosY = 0
    _Width = 7
    _Height = 0
    _MinHeight = 6 ## tested 
    _Parent    = None
    _Color     = pygame.Color(131,199,219)
    
    _StartX   = 0
    _StartY   = 0
    _EndX     = 0
    _EndY     = 0
    _Value    = 0
    _CanvasHWND = None
    
    def __init__(self):
        pass

    def Init(self):
        self.SetCanvasHWND(self._Parent._CanvasHWND)

    def SetCanvasHWND(self,canvas):
        self._CanvasHWND = canvas
        
    def AnimateDraw(self,x2,y2):
        pass

    def UpdateSize(self,bigheight,dirtyheight):
        bodyheight =  float(self._Parent._Height) / float(bigheight)
        if bodyheight > 1:
            bodyheight = 1 ## 100%

        margin = 4
        self._Height  = bodyheight * self._Parent._Height - margin ## Draw body
        
        if self._Height < self._MinHeight:
            self._Height = self._MinHeight
        
        self._StartX = self._Width/2
        self._StartY = margin/2+self._Height/2

        self._EndX   = self._Width/2
        self._EndY   = self._Parent._Height - margin/2 - self._Height/2

        process  = float(dirtyheight) / float(bigheight)
        value    = process* (self._EndY - self._StartY)

        self._Value = int(value)
        
    def Draw(self):
        
        start_rect = midRect(self._PosX+self._StartX,self._StartY+self._Value,self._Width,self._Height,self._Parent._Width,self._Parent._Height)
        aa_round_rect(self._CanvasHWND,start_rect, self._Color,3,0, self._Color)
