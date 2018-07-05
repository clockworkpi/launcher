# -*- coding: utf-8 -*-

import pygame
import gobject
import commands
## local package import
from constants   import Width,Height,RUNSYS
from label       import Label
from fonts       import fonts
from full_screen import FullScreen

import config

class CounterScreen(FullScreen):

    _CounterFont = fonts["varela120"]
    _TextFont1    = fonts["varela15"]
    _TextFont2    = fonts["varela12"]
    
    _TopLabel = None
    _BottomLabel = None
    _NumberLabel = None
    
    _BGColor = pygame.Color(0,0,0)
    _FGColor = pygame.Color(255,255,255)
    
    _Counting = False
    _Number = 10
    _GobjectIntervalId = -1

    _inter_counter = 0
    
    def GObjectInterval(self):

        self._inter_counter+=1

        if self._Number == 0:
            self._Counting = False    
            print("do the real shutdown")
            
            if config.CurKeySet != "PC":
                cmdpath = "feh --bg-center gameshell/wallpaper/seeyou.png;"
                cmdpath += "sleep 3;"
                cmdpath += "sudo halt -p"
                pygame.event.post( pygame.event.Event(RUNSYS, message=cmdpath))\
            
            return False
    
        if self._inter_counter >=2:
            self._Number -= 1
            if self._Number < 0:
                self._Number = 0
            print("sub Number %d " % self._Number)
            self._inter_counter = 0
            
            self.Draw()
            self.SwapAndShow()


        
        return self._Counting
    
    def StartCounter(self):
        if self._Counting == True:
            return

        self._Number = 10
        self._Counting = True
        
        self._GobjectIntervalId = gobject.timeout_add(500,self.GObjectInterval)
        
    def StopCounter(self):
        if self._Counting == False:
            return
        self._Counting = False
        self._Number = 10

        if self._GobjectIntervalId != -1:
            gobject.source_remove(self._GobjectIntervalId)
            self._GobjectIntervalId = -1
        
        return
                    
    def Init(self):
        self._CanvasHWND = pygame.Surface((self._Width,self._Height))
        self._TopLabel = Label()
        self._TopLabel.SetCanvasHWND(self._CanvasHWND)
        self._TopLabel.Init("System shutdown in", self._TextFont1, self._FGColor)
        
        self._BottomLabel = Label()
        self._BottomLabel.SetCanvasHWND(self._CanvasHWND)
        self._BottomLabel.Init("Press any key to stop countdown", self._TextFont2, self._FGColor)
        
        self._NumberLabel = Label()
        self._NumberLabel.SetCanvasHWND(self._CanvasHWND)
        self._NumberLabel.Init(str(self._Number), self._CounterFont, self._FGColor)
        
    def Draw(self):
        self._CanvasHWND.fill( self._BGColor )

        self._TopLabel.NewCoord(Width/2, 15)
        self._TopLabel.DrawCenter()
        
        self._BottomLabel.NewCoord(Width/2, Height-15)
        self._BottomLabel.DrawCenter()

        self._NumberLabel.NewCoord(Width/2,Height/2)
        self._NumberLabel.SetText(str(self._Number))
        self._NumberLabel.DrawCenter()
        
        
        
