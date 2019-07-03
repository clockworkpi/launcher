# -*- coding: utf-8 -*- 

import pygame 
from label  import Label
from skin_manager import MySkinManager
from widget     import Widget
class InfoPageListItem(Widget):
    _Height = 30

    _Labels = {}
    _Icons  = {}
    _Fonts  = {}

    _LinkObj = None
    _ReadOnly = False
    
    def __init__(self):
        self._Labels = {}
        self._Icons  = {}
        self._Fonts  = {}

    def SetSmallText(self,text):
        
        l = Label()
        l._PosX = 40
        l.SetCanvasHWND(self._Parent._CanvasHWND)
        l.Init(text,self._Fonts["small"])
        self._Labels["Small"] = l
        
    def Init(self,text):

        #self._Fonts["normal"] = fonts["veramono12"]
        
        l = Label()
        l._PosX = 10
        l.SetCanvasHWND(self._Parent._CanvasHWND)

        l.Init(text,self._Fonts["normal"])
        self._Labels["Text"] = l

    def Draw(self):
        if self._ReadOnly == True:
            self._Labels["Text"].SetColor(MySkinManager.GiveColor("ReadOnlyText"))
        else:
            self._Labels["Text"].SetColor(MySkinManager.GiveColor("Text"))

        
        self._Labels["Text"]._PosX = self._Labels["Text"]._PosX + self._PosX
        self._Labels["Text"]._PosY = self._PosY + (self._Height - self._Labels["Text"]._Height)/2
        self._Labels["Text"].Draw()
        self._Labels["Text"]._PosX = self._Labels["Text"]._PosX - self._PosX

        if "Small" in self._Labels:
            self._Labels["Small"]._PosX = self._Width - self._Labels["Small"]._Width-5
            
            self._Labels["Small"]._PosY = self._PosY + (self._Height - self._Labels["Small"]._Height)/2
            self._Labels["Small"].Draw()
        
        pygame.draw.line(self._Parent._CanvasHWND,MySkinManager.GiveColor('Line'),(self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)
