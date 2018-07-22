# -*- coding: utf-8 -*- 

import pygame
import  commands

from libs.roundrects import aa_round_rect
from UI.constants import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.fonts  import fonts
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys
from UI.scroller   import ListScroller
from UI.icon_pool  import MyIconPool
from UI.icon_item  import IconItem
from UI.multi_icon_item import MultiIconItem
from UI.multilabel import MultiLabel

class ButtonsLayoutPage(Page):
    _FootMsg =  ["Nav.","","","Back","Toggle"]
    _MyList = []
    _ListFontObj = fonts["varela13"]
    
    _AList = {}

    _Scrolled = 0
    
    _BGwidth = 320
    _BGheight = 240-24-20

    _DrawOnce = False
    _Scroller = None

    _EasingDur = 30

    _dialog_index = 0
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}

    def GenList(self):
        
        self._MyList = []
        
        
            
    def Init(self):
        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._HWND = self._Screen._CanvasHWND
                self._CanvasHWND = pygame.Surface( (self._Screen._Width,self._BGheight) )

        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height

        DialogBoxs = MultiIconItem()
        DialogBoxs._ImgSurf = MyIconPool._Icons["buttonslayout"]
        DialogBoxs._MyType = ICON_TYPES["STAT"]
        DialogBoxs._Parent = self
        DialogBoxs._IconWidth = 300
        DialogBoxs._IconHeight = 150
        DialogBoxs.Adjust(0,0,134,372,0)
        self._Icons["DialogBoxs"] = DialogBoxs

        self.GenList()
        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = self._Width - 10
        self._Scroller._PosY = 2
        self._Scroller.Init()
        self._Scroller.SetCanvasHWND(self._HWND)

    def ScrollDown(self):
        dis = 10
        if abs(self._Scrolled) <  (self._BGheight - self._Height)/2 + 0:
            self._PosY -= dis
            self._Scrolled -= dis
        
    def ScrollUp(self):
        dis = 10
        if self._PosY < 0:
            self._PosY += dis
            self._Scrolled += dis

    def GetButtonsLayoutMode(self):
        lm = "xbox"
        try:
            with open(".buttonslayout", "r") as f:
                lm = f.read()
        except:
            None
        if lm not in ["xbox","snes"]:
            lm = "xbox"
        return lm

    def ToggleMode(self):
        
        if self.GetButtonsLayoutMode() == "xbox":
            
            with open(".buttonslayout", "w") as f:
                f.write("snes")
            
            self._dialog_index = 1
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        else:

            with open(".buttonslayout", "w") as f:
                f.write("xbox")

            self._dialog_index = 0
            self._Screen.Draw()
            self._Screen.SwapAndShow()

    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self._DrawOnce = False
        
        if self.GetButtonsLayoutMode() == "xbox":
            self._dialog_index = 0
        else:
            self._dialog_index = 1
        
    def OnReturnBackCb(self):
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
    def KeyDown(self,event):
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["B"]:
            self.ToggleMode()
                                
    def Draw(self):
        self.ClearCanvas()

        self._Icons["DialogBoxs"].NewCoord(0,30)        
        self._Icons["DialogBoxs"]._IconIndex = self._dialog_index
        self._Icons["DialogBoxs"].DrawTopLeft()
        
        if self._HWND != None:
            self._HWND.fill((255,255,255))
            self._HWND.blit(self._CanvasHWND,(self._PosX,self._PosY,self._Width, self._Height ) )

class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = ButtonsLayoutPage()
        self._Page._Screen = main_screen
        self._Page._Name ="Buttons Layout"
        self._Page.Init()
        
    def API(self,main_screen):
        if main_screen !=None:
            main_screen.PushPage(self._Page)
            main_screen.Draw()
            main_screen.SwapAndShow()

OBJ = APIOBJ()
def Init(main_screen):    
    OBJ.Init(main_screen)
def API(main_screen):
    OBJ.API(main_screen)
    
