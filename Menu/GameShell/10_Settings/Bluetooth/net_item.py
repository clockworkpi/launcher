# -*- coding: utf-8 -*- 

import pygame

## local UI import
from UI.page   import Page
from UI.label  import Label
from UI.icon_item import IconItem
from UI.multi_icon_item  import MultiIconItem
from UI.icon_pool   import MyIconPool
from UI.skin_manager import MySkinManager


class NetItemMultiIcon(MultiIconItem):
    _CanvasHWND = None
    _Parent     = None
    _Width      = 18
    _Height     = 18
    
    def Draw(self):
        self._CanvasHWND.blit(self._ImgSurf,(self._PosX,self._PosY+(self._Parent._Height-self._Height)/2,self._Width,self._Height),
                              (0,self._IconIndex*self._IconHeight,self._IconWidth,self._IconHeight))
    
class NetItemIcon(IconItem):

    _CanvasHWND = None
    _Parent     = None
    _Width      = 18
    _Height     = 18
    
    def Draw(self):
        self._CanvasHWND.blit(self._ImgSurf,(self._PosX,self._PosY+(self._Parent._Height-self._Height)/2,self._Width,self._Height))

            
class NetItem(object):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 30
    
    _Atts  = {}
    
    _Channel=""  # '10' 
    _Stren = ""  ## 19%

    _Parent = None
    _IsActive = False

    _Icons  = {} ## wifi strength and security icons
    _Labels = {}
    _FontObj = None
    
    _RSSI = 0
    _MacAddr=""
    _Path  = "" #/org/bluez/hci0/dev_34_88_5D_97_FF_26
    
    def __init__(self):
        self._Labels = {}
        self._Icons = {}

    def SetActive(self,act):
        self._IsActive = act
    
    def Init(self, path, object):
        self._Path = path
        self._Atts = object 
        
        is_active=False
        if "Address" in object:
            self._MacAddr = object["Address"]
        
        if  "Connected" in object:
            if object["Connected"] == 1:
                is_active=True
        
        if is_active:
            self.SetActive(is_active)
        

        name_label = Label()
        name_label._PosX = 12
        name_label._CanvasHWND = self._Parent._CanvasHWND

        mac_addr = self._MacAddr
        
        if "Name" in object:
            if len(object["Name"]) > 3:
                mac_addr = object["Name"]
        
        if "RSSI" in object:
            print(object["RSSI"])
            self._RSSI = int(object["RSSI"])
        
        mac_addr = mac_addr[:34]
        
        name_label.Init(mac_addr,self._FontObj)
        
        self._Labels["mac_addr"] = name_label

        done_icon = NetItemIcon()
        done_icon._ImgSurf = MyIconPool.GiveIconSurface("done")
        done_icon._CanvasHWND = self._Parent._CanvasHWND
        done_icon._Parent = self
        
        self._Icons["done"] = done_icon
        ## reuse the resource from TitleBar
        #pp(theString)
    
    
    def Connect(self,notworkentry=None):
        """ Execute connection. """
        #dev = dbus.Interface(bus.get_object("org.bluez", "/org/bluez/hci0/dev_"+"34_88_5D_97_FF_26"), "org.bluez.Device1")
        proxy_obj = self._Parent._Dbus.get_object("org.bluez",self._Path)
        dev = self._Parent._Dbus.Interface(proxy_obj, "org.bluez.Device1")
        dev.Connect()

    def Draw(self):
        #pygame.draw.line(self._Parent._CanvasHWND,(169,169,169),(self._PosX,self._PosY),(self._PosX+self._Width,self._PosY),1)
        for i in self._Labels:
            self._Labels[i]._PosY = self._PosY + (self._Height - self._Labels[i]._Height)/2
            self._Labels[i].Draw()
            
        if self._IsActive:
            self._Icons["done"].NewCoord(320-22,self._PosY)
            self._Icons["done"].Draw()
        
        pygame.draw.line(self._Parent._CanvasHWND,MySkinManager.GiveColor('Line'),
            (self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)
