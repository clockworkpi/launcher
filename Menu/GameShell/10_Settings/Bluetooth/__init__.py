# -*- coding: utf-8 -*- 

import pygame
#import math
import  commands
import dbus
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

from net_item import NetItem


class BleInfoPage(Page):
    _FootMsg =  ["Nav.","Disconnect","Forget","Back",""]
    _MyList = []
    _ListFontObj = fonts["varela15"]    


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
            x = self._Parent._WirelessList[idx]._PosX+2
            y = self._Parent._WirelessList[idx]._PosY+1
            h = self._Parent._WirelessList[idx]._Height -3
        
            self._PosX = x
            self._PosY = y
            self._Height = h

            aa_round_rect(self._Parent._CanvasHWND,  
                          (x,y,self._Width-4,h),self._BackgroundColor,4,0,self._BackgroundColor)

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
    
    _ADAPTER_DEV  = "hci0"
    
    def __init__(self):
        Page.__init__(self)
        self._WirelessList = []
        self._CanvasHWND = None
    
    def ShowBox(self,msg):
        
        self._MsgBox._Text = msg
        self._ShowingMessageBox = True
        self._Screen.Draw()
        self._MsgBox.Draw()
        self._Screen.SwapAndShow()
    
    def HideBox(self):
        self.Draw()
        self._ShowingMessageBox = False
        self._Screen.SwapAndShow()    
    
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
        
        msgbox = BleListMessageBox()
        msgbox._CanvasHWND = self._CanvasHWND
        msgbox.Init(" ",fonts["veramono12"])
        msgbox._Parent = self
        
        self._MsgBox = msgbox     

        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = 2
        self._Scroller._PosY = 2
        self._Scroller.Init()
        
        self.GenNetworkList()
        

    def print_normal(self,address, properties):
        print("[ " + address + " ]")

        for key in properties.keys():
            value = properties[key]
            if type(value) is dbus.String:
                value = unicode(value).encode('ascii', 'replace')
            if (key == "Class"):
                print("    %s = 0x%06x" % (key, value))
            else:
                print("    %s = %s" % (key, value))

        print()

	properties["Logged"] = True

    def skip_dev(self,old_dev, new_dev):
        if not "Logged" in old_dev:
            return False
        if "Name" in old_dev:
            return True
        if not "Name" in new_dev:
            return True
        return False

    def DbusPropertiesChanged(self, interface, changed, invalidated, path):
        global devices
        
        if interface != "org.bluez.Device1":
            return

        if path in devices:
            dev = devices[path]

            if self.skip_dev(dev, changed):
                return
            devices[path] = dict(devices[path].items() + changed.items())
        else:
            devices[path] = changed

        if "Address" in devices[path]:
            address = devices[path]["Address"]
        else:
            address = "<unknown>"

        self.print_normal(address, devices[path])

    def ShutDownConnecting(self):
        print("Shutdownconnecting...")
    
    def AbortedAndReturnToUpLevel(self):
        self.HideBox()
        self._Screen._FootBar.ResetNavText()
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
    def CheckIfBluetoothConnecting(self):
        return True
    
    
    def GenNetworkList(self):
        self._WirelessList = []
        start_x = 0
        start_y = 0

        for i,v in enumerate(self._Devices):
            ni = NetItem()
            ni._Parent = self
            ni._PosX = start_x
            ni._PosY = start_y + i* NetItem._Height
            ni._Width = Width
            ni._FontObj = self._ListFontObj
            
            ni.Init(v,self._Devices[v])
            
            self._WirelessList.append(ni)

        self._PsIndex = 0   
    
    def Rescan(self):
        proxy_obj = self._Dbus.get_object("org.bluez", "/org/bluez/" + self._ADAPTER_DEV)
        adapter_props = dbus.Interface(proxy_obj,"org.freedesktop.DBus.Properties")
        discoverying = adapter_props.Get("org.bluez.Adapter1", "Discovering") 
        print(discoverying)
        
        if self._Adapter!= None:
            try:
                self._Adapter.StopDiscovery()
            except Exception,e:
                print(str(e))
            
            try:
                self._Adapter.StartDiscovery()
            except Exception,e:
                print(str(e))
            

    def ScrollUp(self):
        if len(self._WirelessList) == 0:
            return
        self._PsIndex-=1
        if self._PsIndex < 0:
            self._PsIndex = 0
        
        cur_ni = self._WirelessList[self._PsIndex]
        if cur_ni._PosY < 0:
            for i in range(0,len(self._WirelessList)):
                self._WirelessList[i]._PosY += self._WirelessList[i]._Height
            
    def ScrollDown(self):
        if len(self._WirelessList) == 0:
            return
        self._PsIndex+=1
        if self._PsIndex >= len(self._WirelessList):
            self._PsIndex = len(self._WirelessList) -1
       
        cur_ni = self._WirelessList[self._PsIndex]
        if cur_ni._PosY + cur_ni._Height > self._Height:
            for i in range(0,len(self._WirelessList)):
                self._WirelessList[i]._PosY -= self._WirelessList[i]._Height
    
    def KeyDown(self,event):
        
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            if self._Adapter != None:
                _connecting = self.CheckIfBluetoothConnecting()
                if _connecting:
                    self.ShutDownConnecting()
                    self.ShowBox("ShutDownConnecting...")
                    self.AbortedAndReturnToUpLevel()
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
    
    def Draw(self):
        self.ClearCanvas()
        if len(self._WirelessList) == 0:
            return
                
        if len(self._WirelessList) * NetItem._Height > self._Height:
            self._Ps._Width = self._Width - 11
            self._Ps.Draw()
            
            for i in self._WirelessList:
                i.Draw()        
            
            self._Scroller.UpdateSize( len(self._WirelessList)*NetItem._Height, self._PsIndex*NetItem._Height)
            self._Scroller.Draw()
        else:
            self._Ps._Width = self._Width
            self._Ps.Draw()

            for i in self._WirelessList:
                i.Draw()








class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    
    def Init(self,main_screen):
        global bus,devices,adapter
        
        self._Page = BluetoothPage()
        self._Page._Dbus = bus
        self._Page._Devices = devices
        self._Page._Adapter = adapter
        
        self._Page._Screen = main_screen
        self._Page._Name ="Bluetooth"
        
        self._Page.Init()
        
        bus.add_signal_receiver(self._Page.DbusPropertiesChanged,
			dbus_interface = "org.freedesktop.DBus.Properties",
			signal_name = "PropertiesChanged",
			arg0 = "org.bluez.Device1",
			path_keyword = "path")
            
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
