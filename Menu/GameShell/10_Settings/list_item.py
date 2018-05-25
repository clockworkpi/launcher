# -*- coding: utf-8 -*- 

import pygame



## local UI import
from UI.page   import Page
from UI.label  import Label
from UI.fonts  import fonts

# a item for List
# - - - - - - - - - - - -- 
# | Icon  Text.....    > |
# ------------------------

import myvars # icons_path


class ListItem(object):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 30

    _Labels = {}
    _Icons  = {}
    _Fonts  = {}

    _LinkObj = None
    
    def __init__(self):
        self._Labels = {}
        self._Icons  = {}
        self._Fonts  = {}


    
    
    def Init(self,text):

        #self._Fonts["normal"] = fonts["veramono12"]
        
        l = Label()
        l._PosX = 16
        l.SetCanvasHWND(self._Parent._CanvasHWND)

        l.Init(text,self._Fonts["normal"])
        self._Labels["Text"] = l


    def Draw(self):

        self._Labels["Text"]._PosY = self._PosY + (self._Height - self._Labels["Text"]._Height)/2
        self._Labels["Text"].Draw()

        pygame.draw.line(self._Parent._CanvasHWND,(169,169,169),(self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)
    

