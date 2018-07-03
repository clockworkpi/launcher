# -*- coding: utf-8 -*- 

import pygame
#import math
import  commands

#from beeprint import pp
from libs.roundrects import aa_round_rect
#import gobject
#from wicd import misc 
## local UI import
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

class InfoPageListItem(object):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 20

    _Labels = {}
    _Icons  = {}
    _Fonts  = {}

    _LinkObj = None
    
    def __init__(self):
        self._Labels = {}
        self._Icons  = {}
        self._Fonts  = {}

    def SetSmallText(self,text):
        
        l = MultiLabel()
        l.SetCanvasHWND(self._Parent._CanvasHWND)
        l.Init(text,self._Fonts["small"])
        
        self._Labels["Small"] = l

        #if self._Labels["Small"]._Width > self._Width:
        #    self._Width = self._Labels["Small"]._Width
        if self._Labels["Small"]._Height >= self._Height:
            self._Height = self._Labels["Small"]._Height+10
        
    def Init(self,text):

        #self._Fonts["normal"] = fonts["veramono12"]
        
        l = Label()
        l._PosX = 10
        l.SetCanvasHWND(self._Parent._CanvasHWND)

        l.Init(text,self._Fonts["normal"])
        self._Labels["Text"] = l
        
    def Draw(self):
        
        self._Labels["Text"]._PosY = self._PosY
        self._Labels["Text"].Draw()

        if "Small" in self._Labels:
            self._Labels["Small"]._PosX = self._Labels["Text"]._Width + 16 
            self._Labels["Small"]._PosY = self._PosY 
            self._Labels["Small"].Draw()
        
        
    

class AirplanePage(Page):
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

    _airwire_y = 0
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



        airwire = IconItem()
        airwire._ImgSurf = MyIconPool._Icons["airwire"]
        airwire._MyType = ICON_TYPES["STAT"]
        airwire._Parent = self
        airwire.Adjust(0,0,5,43,0)
        self._Icons["airwire"] = airwire

        GS = IconItem()
        GS._ImgSurf = MyIconPool._Icons["GS"]
        GS._MyType = ICON_TYPES["STAT"]
        GS._Parent = self
        GS.Adjust(0,0,72,95,0)
        self._Icons["GS"] = GS

        DialogBoxs = MultiIconItem()
        DialogBoxs._ImgSurf = MyIconPool._Icons["DialogBoxs"]
        DialogBoxs._MyType = ICON_TYPES["STAT"]
        DialogBoxs._Parent = self
        DialogBoxs._IconWidth = 134
        DialogBoxs._IconHeight = 93
        DialogBoxs.Adjust(0,0,134,372,0)
        self._Icons["DialogBoxs"] = DialogBoxs

        
        """
        bgpng = MultiIconItem()
        bgpng._ImgSurf = MyIconPool._Icons["about_bg"]
        bgpng._MyType = ICON_TYPES["STAT"]
        bgpng._Parent = self
        bgpng.Adjust(0,0,self._BGwidth,self._BGheight,0)
        self._Icons["bg"] = bgpng
        """
        
        
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

    def ToggleModeAni(self): ## with animation
        out = commands.getstatusoutput('sudo rfkill list | grep yes | cut -d " " -f3')
        if out[1] == "yes":
            data = self.EasingData(0,43)
            for _,v in enumerate(data):
                self._airwire_y -= v
                self._dialog_index = 2
                pygame.time.delay(40)

                self._Screen.Draw()
                self._Screen.SwapAndShow()
                
            commands.getstatusoutput("sudo rfkill unblock all")
            self._Screen._TitleBar._InAirPlaneMode = False

        else:
            data = self.EasingData(0,43)
            data.reverse()
            for _,v in enumerate(data):
                self._airwire_y += v
                self._dialog_index = 3
                pygame.time.delay(40)
                self._Screen.Draw()
                self._Screen.SwapAndShow()

            commands.getstatusoutput("sudo rfkill block all")
            self._Screen._TitleBar._InAirPlaneMode = True

        
    def ToggleMode(self):
        out = commands.getstatusoutput('sudo rfkill list | grep yes | cut -d " " -f3')
        print out
        if out[1] == "yes":
            self._Screen._MsgBox.SetText("Turning On")
            self._Screen._MsgBox.Draw()
            commands.getstatusoutput("sudo rfkill unblock all")
            self._Screen._TitleBar._InAirPlaneMode = False
        
        else:
            self._Screen._MsgBox.SetText("Turning Off")
            self._Screen._MsgBox.Draw()
            commands.getstatusoutput("sudo rfkill block all")
            self._Screen._TitleBar._InAirPlaneMode = True

        
    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self._DrawOnce = False
        out = commands.getstatusoutput('sudo rfkill list | grep yes | cut -d " " -f3')
        if out[1] == "yes":
            self._Screen._TitleBar._InAirPlaneMode = True
            self._airwire_y = 50+43
            self._dialog_index = 1
        else:
            self._airwire_y = 50
            self._dialog_index = 0
            self._Screen._TitleBar._InAirPlaneMode = False
        
        
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
            self.ToggleModeAni()
            """
            self.ToggleMode()
            self._Screen.SwapAndShow()
            
            pygame.time.delay(1000)
            
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            """
        """
        if event.key == CurKeys["Up"]:
            self.ScrollUp()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        if event.key == CurKeys["Down"]:
            self.ScrollDown()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        """
                                
    def Draw(self):
        self.ClearCanvas()

        self._Icons["DialogBoxs"].NewCoord(145,23)        
        self._Icons["airwire"].NewCoord(80,self._airwire_y)
        
        self._Icons["DialogBoxs"]._IconIndex = self._dialog_index
        
        self._Icons["DialogBoxs"].DrawTopLeft()
        self._Icons["airwire"].Draw()

        self._Icons["GS"].NewCoord(98,118)
        self._Icons["GS"].Draw()
        
        if self._HWND != None:
            self._HWND.fill((255,255,255))
            
            self._HWND.blit(self._CanvasHWND,(self._PosX,self._PosY,self._Width, self._Height ) )
            
#            self._Scroller.UpdateSize(self._BGheight,abs(self._Scrolled)*3)
#            self._Scroller.Draw()
        
        


class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = AirplanePage()
        self._Page._Screen = main_screen
        self._Page._Name ="Airplane Mode"
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
    
        
