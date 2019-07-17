# -*- coding: utf-8 -*- 

import pygame
import os


## local UI import
from UI.page  import Page
from UI.skin_manager import MySkinManager
from UI.constants import ICON_TYPES,Width,Height
from UI.icon_item import IconItem
from UI.icon_pool import MyIconPool
from UI.label  import Label
from UI.util_funcs import midRect

class StoragePage(Page):

    _Icons = {}
    _BGpng  = None
    _BGwidth = 96
    _BGheight = 73
    _BGlabel  = None
    _FreeLabel = None
    
    _GBmsg    = "%.1fGB of %.1fGB Used"
    _DskUsg   = None

    _TextColor = MySkinManager.GiveColor('Text')
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
        
        self._GBLabel = Label()
        self._GBLabel.SetCanvasHWND(self._CanvasHWND)
        self._GBLabel.Init(self._GBmsg % (self._DskUsg[1]-self._DskUsg[0], self._DskUsg[1]),MySkinManager.GiveFont("varela11") )
        self._GBLabel.SetColor(self._TextColor)
        
        self._PctLabel = Label()
        self._PctLabel.SetCanvasHWND(self._CanvasHWND)

        usage_percent = (self._DskUsg[0]/self._DskUsg[1] )*100.0
        
        
        self._PctLabel.Init("%d%%"% int(usage_percent),MySkinManager.GiveFont("EurostileBold30"))
        self._PctLabel.SetColor( self._TextColor )
        
        self._FreeLabel = Label()
        self._FreeLabel.SetCanvasHWND(self._CanvasHWND)
        self._FreeLabel.Init("FREE",MySkinManager.GiveFont("varela12"))
        self._FreeLabel.SetColor(self._PctLabel._Color)

        
    def OnLoadCb(self):
        pass
    
    def Draw(self):
        self.ClearCanvas()
        
        self._PctLabel.NewCoord(32,102- 33)
        self._PctLabel.Draw()

        self._FreeLabel.NewCoord(33   ,130-25)
        self._FreeLabel.Draw()

        self._GBLabel.NewCoord(145,103-29)
        self._GBLabel.Draw()
        
        #bgcolor = (238,238,238), fgcolor = (126,206,244)

        usage_percent = (self._DskUsg[0]/self._DskUsg[1] )
        if usage_percent < 0.1:
            usage_percent = 0.1

        rect_ = pygame.Rect(144,118-25, 283-144,139-117)

        pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('Text'), rect_, 1)

        
        rect2 = pygame.Rect(144,118-25,int((283-144)*(1.0-usage_percent)),139-117)

        rect2.left = rect_.left
        rect2.top  = rect_.top
        
        pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('Text'),rect2, 0)   
        
        sep_rect = pygame.Rect(129,99-25,2,42)
        
        pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('Inactive'),sep_rect, 0)   
        
        ##4 cross
        self.DrawCross(10,10)
        self.DrawCross(self._Screen._Width-20,10)
        self.DrawCross(10,self._Screen._Height-20)
        self.DrawCross(self._Screen._Width-20,self._Screen._Height-20)
        
        
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
    
        
