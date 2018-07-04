# -*- coding: utf-8 -*- 

import pygame
import sys

from libs.roundrects import aa_round_rect

## local UI import
from UI.constants import Width,Height
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.fonts  import fonts
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys
from UI.scroller   import ListScroller

from list_item  import ListItem

import myvars

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
        if idx < len(self._Parent._MyList):
            x = 2
            y = self._Parent._MyList[idx]._PosY+1
            h = self._Parent._MyList[idx]._Height -3
            
            self._PosX = x
            self._PosY = y
            self._Height = h
            
            aa_round_rect(self._Parent._CanvasHWND,  
                          (x,y,self._Width-4,h),self._BackgroundColor,4,0,self._BackgroundColor)



class ListPage(Page):

    _Icons = {}
    _Selector=None
    
    _FootMsg = ["Nav","","","Back","Enter"]
    _MyList = []
    _ListFontObj = fonts["varela15"]

    _Scroller = None
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}
        self._CanvasHWND = None
        self._MyList = []
        
    def Init(self):
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height

        self._CanvasHWND = self._Screen._CanvasHWND

        ps = ListPageSelector()
        ps._Parent = self
        self._Ps = ps
        self._PsIndex = 0

        #                ""   pkgname, label
        alist         = [["","Wifi","Wi-Fi"],
                         ["","Sound","Sound Volume"],
                         ["","Brightness","BackLight Brightness"],
                         ["","Storage",""],
                         ["","Update", ""],
                         ["","About",  "About"],
                         ["","PowerOFF","Power off"]]

        start_x  = 0
        start_y  = 0

        sys.path.append(myvars.basepath)# add self as import path
        
        for i,v in enumerate(alist):
            li = ListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + i*ListItem._Height
            li._Width  = Width
            li._Fonts["normal"] = self._ListFontObj

            if v[2] != "":
                li.Init(v[2])
            else:
                li.Init(v[1])
            
            if v[1] == "Wifi" or v[1] == "Sound" or v[1] == "Brightness" or v[1] == "Storage" or v[1] == "Update" or v[1] == "About" or v[1] == "PowerOFF":
                li._LinkObj = __import__(v[1])
                init_cb   = getattr(li._LinkObj,"Init",None)
                if init_cb != None:
                    if callable(init_cb):
                        li._LinkObj.Init(self._Screen)
            self._MyList.append(li)

        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = self._Width - 10
        self._Scroller._PosY = 2
        self._Scroller.Init()

    def ScrollUp(self):
        if len(self._MyList) == 0:
            return
        self._PsIndex -= 1
        if self._PsIndex < 0:
            self._PsIndex = 0
        cur_li = self._MyList[self._PsIndex]
        if cur_li._PosY < 0:
            for i in range(0, len(self._MyList)):
                self._MyList[i]._PosY += self._MyList[i]._Height
        

    def ScrollDown(self):
        if len(self._MyList) == 0:
            return
        self._PsIndex +=1
        if self._PsIndex >= len(self._MyList):
            self._PsIndex = len(self._MyList) -1

        cur_li = self._MyList[self._PsIndex]
        if cur_li._PosY +cur_li._Height > self._Height:
            for i in range(0,len(self._MyList)):
                self._MyList[i]._PosY -= self._MyList[i]._Height

    def Click(self):
        cur_li = self._MyList[self._PsIndex]
        if cur_li._LinkObj != None:
            api_cb = getattr(cur_li._LinkObj,"API",None)
            if api_cb != None:
                if callable(api_cb):
                    cur_li._LinkObj.API(self._Screen)

        
    def KeyDown(self,event):
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
        if event.key == CurKeys["Up"]:
            self.ScrollUp()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        if event.key == CurKeys["Down"]:
            self.ScrollDown()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        

        if event.key == CurKeys["Enter"]:
            self.Click()
            
    def Draw(self):
        self.ClearCanvas()

        if len(self._MyList) * ListItem._Height > self._Height:
            self._Ps._Width = self._Width - 11
            
            self._Ps.Draw()
            
            for i in self._MyList:
                i.Draw()
        
            self._Scroller.UpdateSize( len(self._MyList)*ListItem._Height, self._PsIndex*ListItem._Height)
            self._Scroller.Draw()
        else:
            self._Ps._Width = self._Width
            self._Ps.Draw()
            for i in self._MyList:
                i.Draw()

            
