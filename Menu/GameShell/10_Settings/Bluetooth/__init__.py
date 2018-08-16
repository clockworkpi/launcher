
# -*- coding: utf-8 -*- 

import pygame
#import math
import  commands

#from beeprint import pp
from libs.roundrects import aa_round_rect

from libs.DBUS import  bus, adapter,devices

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
from UI.skin_manager import SkinManager

from UI.multilabel import MultiLabel


class BleListSelector(PageSelector):
    _BackgroundColor = SkinManager().GiveColor('Front')

    def __init__(self):
        self._PosX = 0
        self._PosY = 0
        self._Height = 0

    def AnimateDraw(self,x2,y2):
        pass 

    def Draw(self):
        idx = self._Parent._PsIndex
        if idx < len( self._Parent._WirelessList):
            x = self._Parent._WirelessList[idx]._PosX+11
            y = self._Parent._WirelessList[idx]._PosY+1
            h = self._Parent._WirelessList[idx]._Height -3
        
            self._PosX = x
            self._PosY = y
            self._Height = h

            aa_round_rect(self._Parent._CanvasHWND,  
                          (x,y,self._Width,h),self._BackgroundColor,4,0,self._BackgroundColor)

class BleListMessageBox(Label):
    _Parent = None

    def Draw(self):
        my_text = self._FontObj.render( self._Text,True,self._Color)
        w  = my_text.get_width()
        h  = my_text.get_height()
        x  = (self._Parent._Width - w)/2
        y =  (self._Parent._Height - h)/2
        padding = 10 
        pygame.draw.rect(self._CanvasHWND,SkinManager().GiveColor('White'),(x-padding,y-padding, w+padding*2,h+padding*2))

        pygame.draw.rect(self._CanvasHWND,SkinManager().GiveColor('Black'),(x-padding,y-padding, w+padding*2,h+padding*2),1)

        self._CanvasHWND.blit(my_text,(x,y,w,h))



class BluetoothPage(Page):
    _WirelessList = []
    #Wicd dbus part
    _Adapter = None
    _Dbus     = None
    _Devices  = None
    
    _BlePassword = ""
    _Connecting = False
    _Scanning   = False 
    
    _PrevState = None
    _Selector = None
    
    _ShowingMessageBox = False 
    _MsgBox            = None
    _ConnectTry        = 0
    _BlockCb           = None
    
    _LastStatusMsg     = ""
    _FootMsg           = ["Nav.","Scan","Info","Back","Enter"]
    _Scroller          = None
    _ListFontObj       = fonts["notosanscjk15"]

    _InfoPage          = None
    
    def __init__(self):
        Page.__init__(self)
        self._WirelessList = []
        self._CanvasHWND = None
    
    def Init(self):
        
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height  
    
        #self._CanvasHWND = pygame.Surface((self._Width,self._Height))
        self._CanvasHWND = self._Screen._CanvasHWND

        ps = BleListSelector()
        ps._Parent = self
        ps._Width = Width - 12
        
        self._Ps = ps
        self._PsIndex = 0
        
        msgbox = WifiListMessageBox()
        msgbox._CanvasHWND = self._CanvasHWND
        msgbox.Init(" ",fonts["veramono12"])
        msgbox._Parent = self
        
        self._MsgBox = msgbox     

    def DbusPropertiesChanged:## signal_name = "PropertiesChanged",
        pass
    
    def GenNetworkList(self):
        self._WirelessList = []
        start_x = 0
        start_y = 0

        for network_id,v in enumerate(self._Devices):
            ni = NetItem()
            ni._Parent = self
            ni._PosX = start_x
            ni._PosY = start_y + network_id* NetItem._Height
            ni._Width = Width
            ni._FontObj = self._ListFontObj
            ni.Init()
            self._WirelessList.append(ni)

        self._PsIndex = 0   
    
    def Rescan():
        if self._Adapter!= None:
            self._Adapter.StopDiscovery()
            self._Adapter.StartDiscovery()
    
    def KeyDown:
        
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            if self._Adapter != None:
                _connecting = self._Wireless.CheckIfBluetoothConnecting()
                if _connecting:
                    self.ShutDownConnecting()
                    self.ShowBox("ShutDownConnecting...")
                else:
                    self.AbortedAndReturnToUpLevel()
            else:
                self.HideBox()
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
        
        if event.key == CurKeys["X"]:
            self.Rescan()   
    
    def Draw():
        self.ClearCanvas()
        if len(self._WirelessList) == 0:
            return
        
        self._Ps.Draw()
        for i in self._WirelessList:
            i.Draw()
            
        self._Scroller.UpdateSize( len(self._WirelessList)*NetItem._Height, self._PsIndex*NetItem._Height)
        self._Scroller.Draw()










class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = BluetoothPage()
        self._Page._Dbus = bus
        self._Page._Devices = devices
        self._Page._Adapter = adapter
        
        self._Page._Screen = main_screen
        self._Page._Name ="Bluetooth"
        
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
