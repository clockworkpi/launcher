# -*- coding: utf-8 -*- 

import pygame
import os


## local UI import
from UI.page  import Page
from UI.constants import ICON_TYPES,Width,Height
from UI.icon_item import IconItem
from UI.icon_pool import MyIconPool
from UI.label  import Label
from UI.fonts  import fonts
from UI.util_funcs import midRect

from libs.roundrects import aa_round_rect

class StoragePage(Page):

    _Icons = {}
    _BGpng  = None
    _BGwidth = 96
    _BGheight = 73
    _BGlabel  = None
    _FreeLabel = None
    
    _BGmsg    = "%.1fGB of %.1fGB Used"
    _DskUsg   = None

    _HighColor = pygame.Color(51,166,255)
    _FootMsg    = ["Nav.","","","Back",""]
    
    def __init__(self):
        Page.__init__(self)
        
        self._Icons = {}


    def DiskUsage(self):
        statvfs = os.statvfs('/')

        total_space = (statvfs.f_frsize * statvfs.f_blocks)/1024.0/1024.0/1024.0

        avail_space = ( statvfs.f_frsize * statvfs.f_bavail) / 1024.0 / 1024.0/ 1024.0

        return avail_space,total_space
        
    def Init(self):

        self._DskUsg = self.DiskUsage()
        
        self._CanvasHWND = self._Screen._CanvasHWND
        self._Width =  self._Screen._Width
        self._Height = self._Screen._Height
        
        self._BGpng = IconItem()
        self._BGpng._ImgSurf = MyIconPool._Icons["icon_sd"]
        self._BGpng._MyType = ICON_TYPES["STAT"]
        self._BGpng._Parent = self
        
        self._BGpng.AddLabel(self._BGmsg % (self._DskUsg[1]-self._DskUsg[0], self._DskUsg[1]), fonts["varela15"])
        self._BGpng.Adjust(0,0,self._BGwidth,self._BGheight,0)

        
        self._BGlabel = Label()
        self._BGlabel.SetCanvasHWND(self._CanvasHWND)

        usage_percent = (self._DskUsg[0]/self._DskUsg[1] )*100.0
        
        self._BGlabel.Init("%d%%"% int(usage_percent),fonts["varela25"])
        self._BGlabel.SetColor( self._HighColor )
        
        self._FreeLabel = Label()
        self._FreeLabel.SetCanvasHWND(self._CanvasHWND)
        self._FreeLabel.Init("Free",fonts["varela13"])
        self._FreeLabel.SetColor(self._BGlabel._Color)

        
    def OnLoadCb(self):
        pass
    
    def Draw(self):
        self.ClearCanvas()
        
        self._BGpng.NewCoord(self._Width/2,self._Height/2-10)
        self._BGpng.Draw()
        self._BGlabel.NewCoord(self._Width/2-28,self._Height/2-30)
        self._BGlabel.Draw()

        self._FreeLabel.NewCoord(self._BGlabel._PosX+10   ,self._Height/2)
        self._FreeLabel.Draw()

        #bgcolor = (238,238,238), fgcolor = (126,206,244)
        #aa_round_rect
        usage_percent = (self._DskUsg[0]/self._DskUsg[1] )
        if usage_percent < 0.1:
            usage_percent = 0.1

        rect_ = midRect(self._Width/2,self._Height-30,170,17, Width,Height)

        aa_round_rect(self._CanvasHWND,rect_, (193,193,193),5,0,(193,193,193))

        
        rect2 = midRect(self._Width/2,self._Height-30,int(170*(1.0-usage_percent)),17, Width,Height)

        rect2.left = rect_.left
        rect2.top  = rect_.top
        
        aa_round_rect(self._CanvasHWND,rect2, (126,206,244),5,0,(126,206,244))        
        
class APIOBJ(object):

    _StoragePage = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._StoragePage = StoragePage()

        self._StoragePage._Screen = main_screen
        self._StoragePage._Name ="Storage"
        self._StoragePage.Init()
        
        
    def API(self,main_screen):
        if main_screen !=None:
            main_screen.PushPage(self._StoragePage)
            main_screen.Draw()
            main_screen.SwapAndShow()
    


OBJ = APIOBJ()
def Init(main_screen):    
    OBJ.Init(main_screen)
def API(main_screen):
    OBJ.API(main_screen)
    
        
