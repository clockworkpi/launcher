# -*- coding: utf-8 -*- 

import pygame
from libs.roundrects import aa_round_rect

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

import myvars # icons_path

class ListItemIcon(IconItem):

    _CanvasHWND = None
    _Parent     = None
    _Width      = 18
    _Height     = 18
    
    def Draw(self):
        self._CanvasHWND.blit(self._ImgSurf,(self._PosX,self._PosY+(self._Parent._Height-self._Height)/2,self._Width,self._Height))


class ListItemLabel(Label):

    _ActiveColor  = pygame.Color(175,90,0)
    _Active = False
    def Draw(self):

        self._FontObj.set_bold(self._Active)
        
        """
        if self._Active == True:
            my_text = self._FontObj.render( self._Text,True,self._ActiveColor)
        else:
            my_text = self._FontObj.render( self._Text,True,self._Color)
        """
        
        my_text = self._FontObj.render( self._Text,True,self._Color)
        self._CanvasHWND.blit(my_text,(self._PosX,self._PosY,self._Width,self._Height))

    
class ListItem(object):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 30

    _Labels = {}
    _Icons  = {}
    _Fonts  = {}
    _MyType = ICON_TYPES["EXE"]
    _LinkObj = None
    _Path    = ""
    _Active  = False
    _Playing = False ## play or pause
    _PlayingProcess = 0 # 0 - 100
    _Parent  = None
    
    
    def __init__(self):
        self._Labels = {}
        self._Icons  = {}
        self._Fonts  = {}


    def Init(self,text):

        #self._Fonts["normal"] = fonts["veramono12"]
        
        l = ListItemLabel()
        l._PosX = 22
        l.SetCanvasHWND(self._Parent._CanvasHWND)

        if self._MyType == ICON_TYPES["DIR"]:
            l.Init(text,self._Fonts["normal"])
            self._Path = text
        else:
            l.Init(text,self._Fonts["normal"])
            self._Path = text


        self._Labels["Text"] = l
        
        
    def NewCoord(self,x,y):
        self._PosX = x
        self._PosY = y

    def Draw(self):

        if self._MyType == ICON_TYPES["DIR"] and self._Path != "[..]":
            self._Parent._Icons["sys"]._IconIndex = 0
            self._Parent._Icons["sys"].NewCoord(self._PosX+12,self._PosY+ (self._Height - self._Parent._Icons["sys"]._Height)/2+self._Parent._Icons["sys"]._Height/2)
            self._Parent._Icons["sys"].Draw()

        if self._MyType == ICON_TYPES["FILE"]:
            self._Parent._Icons["sys"]._IconIndex = 1
            self._Parent._Icons["sys"].NewCoord(self._PosX+12,self._PosY+ (self._Height - self._Parent._Icons["sys"]._Height)/2+self._Parent._Icons["sys"]._Height/2)
            self._Parent._Icons["sys"].Draw()
        
        if self._Active == True:
            self._Labels["Text"]._Active = True
        else:
            self._Labels["Text"]._Active = False

        
        self._Labels["Text"]._PosY = self._PosY + (self._Height - self._Labels["Text"]._Height)/2
            
        pygame.draw.line(self._Parent._CanvasHWND,(169,169,169),(self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)

        if self._Playing == True:
            self._Labels["Text"]._Active =True
            self._Labels["Text"].Draw()
            #_rect = midRect(10,self._PosY+15,10,10,self._Parent._Width,self._Parent._Height)
            #aa_round_rect(self._Parent._CanvasHWND,_rect,(0,0,0),3,0,(0,0,0))
            #pygame.draw.polygon(self._Parent._CanvasHWND, (0,0,0), [[6, self._PosY+7], [11, self._PosY+14],[6, self._PosY+21]], 2)
            
            if self._PlayingProcess > 0:
                seek_posx = int(self._Width * self._PlayingProcess/100.0)
                pygame.draw.line(self._Parent._CanvasHWND,(255,169,169),(self._PosX,self._PosY+self._Height-2),(self._PosX+seek_posx,self._PosY+self._Height-2),2)   

        else:
            self._Labels["Text"].Draw()

