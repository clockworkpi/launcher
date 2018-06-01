# -*- coding: utf-8 -*- 

import pygame
#from beeprint import pp
import os

## local UI import
from UI.constants import ICON_TYPES
from UI.page   import Page
from UI.label  import Label
from UI.fonts  import fonts
from UI.icon_item import IconItem
from UI.util_funcs import midRect

# a item for List
# - - - - - - - - - - - -- 
# | Icon  Text.....    > |
# ------------------------


class ListItemIcon(IconItem):

    _CanvasHWND = None
    _Parent     = None
    _Width      = 18
    _Height     = 18
    
    def Draw(self):
        self._CanvasHWND.blit(self._ImgSurf,(self._PosX,self._PosY+(self._Parent._Height-self._Height)/2,self._Width,self._Height))

class ListItem(object):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 32

    _Labels = {}
    _Icons  = {}
    _Fonts  = {}
    _MyType = ICON_TYPES["EXE"]
    _LinkObj = None
    _Path    = ""
    _Active  = False
    _Playing = False ## play or pause
    _Parent  = None
    
    def __init__(self):
        self._Labels = {}
        self._Icons  = {}
        self._Fonts  = {}

    def IsFile(self):
        if self._MyType == ICON_TYPES["FILE"]:
            return True

        return False
    def IsDir(self):
        if self._MyType == ICON_TYPES["DIR"]:
            return True

        return False
    
    def Init(self,text):

        #self._Fonts["normal"] = fonts["veramono12"]
        
        l = Label()
        l._PosX = 20
        l.SetCanvasHWND(self._Parent._CanvasHWND)

        if self._MyType == ICON_TYPES["DIR"] or self._MyType == ICON_TYPES["FILE"]:
            self._Path = text

        label_text = os.path.basename(text)
        
        if self._MyType == ICON_TYPES["DIR"]:
            l.Init(label_text,self._Fonts["normal"])
        else:
            l.Init(label_text,self._Fonts["normal"])


        self._Labels["Text"] = l

        

    def Draw(self):
        if self._Path != "[..]":
            self._Labels["Text"]._PosX = 23
        else:
            self._Labels["Text"]._PosX = 3
            
        self._Labels["Text"]._PosY = self._PosY + (self._Height - self._Labels["Text"]._Height)/2
        self._Labels["Text"].Draw()

        """
        if self._Active == True:
            pass
        """
        if self._MyType == ICON_TYPES["DIR"] and self._Path != "[..]":
            self._Parent._Icons["sys"]._IconIndex = 0
            self._Parent._Icons["sys"].NewCoord(self._PosX+12,self._PosY+ (self._Height - self._Parent._Icons["sys"]._Height)/2+self._Parent._Icons["sys"]._Height/2)
            self._Parent._Icons["sys"].Draw()

        if self._MyType == ICON_TYPES["FILE"]:
            self._Parent._Icons["sys"]._IconIndex = 1
            self._Parent._Icons["sys"].NewCoord(self._PosX+12,self._PosY+ (self._Height - self._Parent._Icons["sys"]._Height)/2+self._Parent._Icons["sys"]._Height/2)
            self._Parent._Icons["sys"].Draw()
        
        pygame.draw.line(self._Parent._CanvasHWND,(169,169,169),(self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)
    

