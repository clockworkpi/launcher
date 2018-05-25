# -*- coding: utf-8 -*- 

import pygame
import os

from libs.roundrects import aa_round_rect

#UI lib
from constants import Width,Height,ICON_TYPES
from page   import Page,PageSelector
from label  import Label
from fonts  import fonts
from util_funcs import midRect
from keys_def   import CurKeys



class ListPageSelector(PageSelector):
    _BackgroundColor = pygame.Color(131,199,219)

    def __init__(self):
        self._PosX = 0
        self._PosY = 0
        self._Height = 0
        self._Width  = Width

    def AnimateDraw(self,x2,y2):
        pass

    def Draw(self):
        idx = self._Parent._PsIndex
        if idx > (len(self._Parent._MyList)-1):
            idx = len(self._Parent._MyList)
            if idx > 0:
                idx -=1
            elif idx == 0: #Nothing
                return
        
        x = self._Parent._MyList[idx]._PosX+2
        y = self._Parent._MyList[idx]._PosY+1
        h = self._Parent._MyList[idx]._Height -3
        
        self._PosX = x
        self._PosY = y
        self._Height = h

        aa_round_rect(self._Parent._CanvasHWND,  
                    (x,y,self._Width-4,h),self._BackgroundColor,4,0,self._BackgroundColor)



class ConfirmPage(Page):

    _Icons = {}
    _Selector=None
    _FootMsg = ["Nav","","","Cancel","Yes"]
    _MyList = []
    _ListFont = fonts["veramono20"]
    _MyStack = None
    _FileName     = ""
    _TrashDir     = ""
    _ConfirmText = "Confirm?"
    _BGPosX      = 0
    _BGPosY      = 0
    _BGWidth     = 0
    _BGHeight    = 0
    _Parent      = None
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}
        self._CanvasHWND = None
        self._MyList = []
        
    def Reset(self):
        self._MyList[0].SetText(self._ConfirmText)
        self._MyList[0]._PosX = (self._Width - self._MyList[0]._Width)/2
        self._MyList[0]._PosY = (self._Height - self._MyList[0]._Height)/2
        
        self._BGPosX = self._MyList[0]._PosX-10
        self._BGPosY = self._MyList[0]._PosY-10
        self._BGWidth = self._MyList[0]._Width+20
        self._BGHeight = self._MyList[0]._Height+20

        
    def SnapMsg(self,msg):
        self._MyList[0].SetText(msg)
        self._MyList[0]._PosX = (self._Width - self._MyList[0]._Width)/2
        self._MyList[0]._PosY = (self._Height - self._MyList[0]._Height)/2

        self._BGPosX = self._MyList[0]._PosX-10
        self._BGPosY = self._MyList[0]._PosY-10
        self._BGWidth = self._MyList[0]._Width+20
        self._BGHeight = self._MyList[0]._Height+20
        
    def Init(self):
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height

        self._CanvasHWND = self._Screen._CanvasHWND

        ps = ListPageSelector()
        ps._Parent = self
        self._Ps = ps
        self._PsIndex = 0

        li = Label()
        li.SetCanvasHWND(self._CanvasHWND)
        li.Init(self._ConfirmText,self._ListFont)
        
        li._PosX = (self._Width - li._Width)/2
        li._PosY = (self._Height - li._Height)/2

        self._BGPosX = li._PosX-10
        self._BGPosY = li._PosY-10
        self._BGWidth = li._Width+20
        self._BGHeight = li._Height+20
        
        self._MyList.append(li)
        
    def KeyDown(self,event):
        
        if event.key == CurKeys["Menu"] or event.key == CurKeys["A"]:            
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
    def DrawBG(self):
        _rect = pygame.Rect(self._BGPosX,self._BGPosY,self._BGWidth,self._BGHeight)
        
        pygame.draw.rect(self._CanvasHWND,(255,255,255),_rect,0)
        pygame.draw.rect(self._CanvasHWND,(83,83,83),_rect,1)
        
    def Draw(self):
        #self.ClearCanvas()
        
        self.DrawBG()
        for i in self._MyList:
            i.Draw()

        self.Reset()
