# -*- coding: utf-8 -*- 
import re
import pygame
#import math
import  commands
import dbus
from beeprint import pp
from libs.roundrects import aa_round_rect

from libs.DBUS import  bus, adapter,devices

#import gobject
#from wicd import misc 
## local UI import
from UI.constants import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys, IsKeyStartOrA, IsKeyMenuOrB
from UI.scroller   import ListScroller
from UI.icon_pool  import MyIconPool
from UI.icon_item  import IconItem
from UI.multi_icon_item import MultiIconItem
from UI.skin_manager import MySkinManager
from UI.confirm_page import ConfirmPage
from UI.info_page_list_item import InfoPageListItem

from UI.multilabel import MultiLabel
from UI.lang_manager import MyLangManager
from UI.keyboard import Keyboard

from net_item import NetItem

from agent import BleAgent,BleAgentPairPage

class BleForgetConfirmPage(ConfirmPage):

    _ConfirmText = MyLangManager.Tr("ConfirmForgetQ")
    
    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
        if IsKeyStartOrA(event.key):
            self.SnapMsg(MyLangManager.Tr("Deleting"))
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
            try:
                #self._Parent._Adapter.RemoveDevice()
                print("try to RemoveDevice")
            except Exception,e:
                print(str(e))
            
            pygame.time.delay(400)
            
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
                    
    def Draw(self):
        #self.ClearCanvas()
        self.DrawBG()
        for i in self._MyList:
            i.Draw()
        
        self.Reset()


class BleInfoPageSelector(PageSelector):
    _BackgroundColor = MySkinManager.GiveColor('Front')

    def __init__(self):
        self._PosX = 0
        self._PosY = 0
        self._Height = 0
        
    def AnimateDraw(self,x2,y2):
        pass 

    def Draw(self):
        idx = self._Parent._PsIndex
        if idx < len( self._Parent._MyList):
            x = self._PosX+2
            y = self._Parent._MyList[idx]._PosY+1
            h = self._Parent._MyList[idx]._Height -3
        
            self._PosX = x
            self._PosY = y
            self._Height = h

            aa_round_rect(self._Parent._CanvasHWND,  
                          (x,y,self._Width-4,h),self._BackgroundColor,4,0,self._BackgroundColor)

class BleInfoPage(Page):
    _FootMsg =  ["Nav","Forget","Disconnect","Back",""]
    _MyList = []
    _ListFontObj = MyLangManager.TrFont("varela15")
    _ListSmFontObj = MySkinManager.GiveFont("varela12")  # small font
    _ListSm2FontObj= MySkinManager.GiveFont("varela11")
    
    _AList = {}
    _Path = ""
    def Init(self):
        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._CanvasHWND = self._Screen._CanvasHWND

        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height
        
        ps = BleInfoPageSelector()
        ps._Parent = self
        self._Ps = ps
        self._PsIndex = 0
         
        #_AList is an object 
        self.GenList()

        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = 2
        self._Scroller._PosY = 2
        self._Scroller.Init()
        
        self._ConfirmPage1 = BleForgetConfirmPage()
        self._ConfirmPage1._Screen = self._Screen
        self._ConfirmPage1._Name   = "ConfirmForget"
        self._ConfirmPage1._Parent = self
        self._ConfirmPage1.Init() 
        
    def GenList(self):
        if self._AList== None:
            return
        self._MyList = []
        self._PsIndex = 0
        start_x  = 0
        start_y  = 0
         
        for i,v in enumerate( self._AList):
            #print(i,v) # (0, dbus.String(u'AddressType'))
            
            li = InfoPageListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + i*InfoPageListItem._Height
            li._Width  = Width
            li._Fonts["normal"] = self._ListFontObj
            
            if v == "UUIDs":
                li._Fonts["small"] = self._ListSm2FontObj
            else:
                li._Fonts["small"] = self._ListSmFontObj
            
            li.Init( str(v) )
            li._Flag = v
            
            if v =="UUIDs":
                if len(self._AList[v]) > 1:
                    pp(self._AList[v][0])
                    sm_text = str(self._AList[v][0])
                else:
                    sm_text = "<empty>"
            else:
                sm_text = str(self._AList[v]) 
            
            if sm_text == "0":
                sm_text="No"
            elif sm_text == "1":
                sm_text="Yes"
            
            sm_text = sm_text[:20]
            li.SetSmallText(sm_text)
            
            li._PosX = 2
            self._MyList.append(li)                      

    def TryToForget(self):
        global adapter
        proxy_obj = bus.get_object("org.bluez", self._Path)
        dev = dbus.Interface(proxy_obj, "org.bluez.Device1")
        
        self._Screen._MsgBox.SetText("Forgeting")
        self._Screen._MsgBox.Draw()
        self._Screen.SwapAndShow()        
        
        try:
            adapter.RemoveDevice(dev)
        except Exception,e:
            err_name = e.get_dbus_name()
            if err_name == "org.freedesktop.DBus.Error.NoReply":
                self._Screen._MsgBox.SetText("DBus noreply")
            else:
                self._Screen._MsgBox.SetText("Forget failed")
            
            self._Screen._MsgBox.Draw()
            self._Screen.SwapAndShow()
        
        pygame.time.delay(500)
        
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()    
    
    def TryToDisconnect(self):
        global bus
        
        if "Connected" in self._AList:
            if self._AList["Connected"] == 0:
                return
        
        proxy_obj = bus.get_object("org.bluez", self._Path)
        dev = dbus.Interface(proxy_obj, "org.bluez.Device1")
        
        self._Screen._FootBar.UpdateNavText("Disconnecting")
        self._Screen._MsgBox.SetText("Disconnecting")
        self._Screen._MsgBox.Draw()
        self._Screen.SwapAndShow()
        
        try:
            dev.Disconnect()
        except Exception,e:
            err_name = e.get_dbus_name()
            if err_name == "org.freedesktop.DBus.Error.NoReply":
                self._Screen._MsgBox.SetText("DBus noreply")
            else:
                self._Screen._MsgBox.SetText("Disconnect failed")
            self._Screen._MsgBox.Draw()
            self._Screen.SwapAndShow()
        
        pygame.time.delay(500)
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
        self._Screen._FootBar.ResetNavText()        
        
    
    def Click(self):
        if self._PsIndex >= len(self._MyList):
            return
        
        cur_li = self._MyList[self._PsIndex]
        print(cur_li._Flag)
        if cur_li._Flag in self._AList:
            print(self._AList[ cur_li._Flag ])
        
    def OnLoadCb(self):
        if self._AList != None:
            if "Connected" in self._AList:
                if self._AList["Connected"] == 1:
                    self._FootMsg[1] = "Disconnect"
                else:
                    self._FootMsg[1] = ""
        
        self.GenList()

    def OnReturnBackCb(self):
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()

    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
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
        
        if IsKeyStartOrA(event.key):
            self.Click()
            
        if event.key == CurKeys["X"]:
            self.TryToDisconnect()
        
        if event.key == CurKeys["Y"]:
            self.TryToForget()
        
        
    def Draw(self):
        if len(self._MyList) == 0:
            return
        
        self.ClearCanvas()

        if len(self._MyList) * InfoPageListItem._Height > self._Height:
            self._Ps._Width = self._Width - 10
            self._Ps._PosX  = 9
            self._Ps.Draw()        
            for i in self._MyList:
                i.Draw()
            
            self._Scroller.UpdateSize(len(self._MyList)*InfoPageListItem._Height, self._PsIndex*InfoPageListItem._Height)
            self._Scroller.Draw()
        
        else:
            self._Ps._Width = self._Width
            self._Ps.Draw()
            for i in self._MyList:
                i.Draw() 
        

            

class BleListSelector(PageSelector):
    _BackgroundColor = MySkinManager.GiveColor('Front')

    def __init__(self):
        self._PosX = 0
        self._PosY = 0
        self._Height = 0

    def AnimateDraw(self,x2,y2):
        pass 

    def Draw(self):
        idx = self._Parent._PsIndex
        if idx < len( self._Parent._MyList):
            x = self._Parent._MyList[idx]._PosX+2
            y = self._Parent._MyList[idx]._PosY+1
            h = self._Parent._MyList[idx]._Height -3
        
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
        pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('White'),(x-padding,y-padding, w+padding*2,h+padding*2))

        pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('Black'),(x-padding,y-padding, w+padding*2,h+padding*2),1)

        self._CanvasHWND.blit(my_text,(x,y,w,h))



class BluetoothPage(Page):
    _MyList = []
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
    _FootMsg           = ["Nav","Info","Scan","Back","TryConnect"]
    _Scroller          = None
    _ListFontObj       = MyLangManager.TrFont("notosanscjk15")

    _InfoPage          = None
    
    _ADAPTER_DEV  = "hci0"
    
    _Offline = False
    
    _Leader = None
    
    def __init__(self):
        Page.__init__(self)
        self._MyList = []
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
        msgbox.Init(" ",MyLangManager.TrFont("veramono12"))
        msgbox._Parent = self
        
        self._MsgBox = msgbox     

        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = 2
        self._Scroller._PosY = 2
        self._Scroller.Init()
        
        self.GenNetworkList()
        
        self._InfoPage = BleInfoPage()
        self._InfoPage._Screen = self._Screen
        self._InfoPage._Name   = "BluetoothInfo"
        self._InfoPage.Init()        

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
        print("DbusPropertiesChanged")
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
        
        self._Devices = devices
        self.print_normal(address, devices[path])
        
        self.RefreshDevices()
        self.GenNetworkList()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
    def ShutDownConnecting(self):
        print("Bluetooth Shutdown connecting...")
    
    def AbortedAndReturnToUpLevel(self):
        self.HideBox()
        self._Screen._FootBar.ResetNavText()
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
    
    
    def CheckIfBluetoothConnecting(self):
        return True

    def TryConnect(self):
        global bus
        
        if self._PsIndex >= len(self._MyList):
            return
        
        cur_li = self._MyList[self._PsIndex]
        print(cur_li._Path)
        
        if "Connected" in cur_li._Atts:
            if cur_li._Atts["Connected"] == 1:
                return
        
        proxy_obj = bus.get_object("org.bluez", cur_li._Path)
        dev = dbus.Interface(proxy_obj, "org.bluez.Device1")
        
        self._Screen._FootBar.UpdateNavText("Connecting")
        self.ShowBox(MyLangManager.Tr("Connecting"))
        
        self._Leader._MyAgent.device_obj = dev
        self._Leader._MyAgent.dev_path = cur_li._Path
        
        try:
            dev.Pair(reply_handler=self._Leader._MyAgent.pair_reply, 
                                error_handler=self._Leader._MyAgent.pair_error,timeout=60000)
        except Exception,e:
            print(str(e))        
        
        
        #self.HideBox()
        #self._Screen._FootBar.ResetNavText()
        
    def RefreshDevices(self):
        global devices
        devices = {}
        try:
            proxy_obj = bus.get_object("org.bluez", "/")
            manager = dbus.Interface(proxy_obj,"org.freedesktop.DBus.ObjectManager")
            objects = manager.GetManagedObjects()
            for path, interfaces in objects.iteritems():
                if "org.bluez.Device1" in interfaces:
                    devices[path] = interfaces["org.bluez.Device1"] ## like /org/bluez/hci0/dev_xx_xx_xx_yy_yy_yy
        except Exception,e:
            print(str(e))
            devices={}
        
        self._Devices = devices
        
    
    def GenNetworkList(self):
        self._MyList = []
        start_x = 0
        start_y = 0
        
        counter = 0
        for i,v in enumerate(self._Devices):
            if "Name" in self._Devices[v]:
                if len(self._Devices[v]["Name"]) < 2:
                    continue
                if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", self._Devices[v]["Name"].lower()): ## skip xx:xx:xx:xx:xx
                    continue
            else:
                continue
            
            ni = NetItem()
            ni._Parent = self
            ni._PosX = start_x
            ni._PosY = start_y + counter* NetItem._Height
            ni._Width = Width
            ni._FontObj = self._ListFontObj
            
            ni.Init(v,self._Devices[v])
            
            counter += 1
            self._MyList.append(ni)

        self._PsIndex = 0   
    
    def Rescan(self):
        if self._Screen._CurrentPage != self:
            return
        
        self._Scanning = True
        self.ShowBox(MyLangManager.Tr("BluetoothScanning"))
        self._Screen._FootBar.UpdateNavText("Scanning")
        
        proxy_obj = self._Dbus.get_object("org.bluez", "/org/bluez/" + self._ADAPTER_DEV)
        adapter_props = dbus.Interface(proxy_obj,"org.freedesktop.DBus.Properties")
        discoverying = adapter_props.Get("org.bluez.Adapter1", "Discovering") 
        print("discoverying", discoverying)
        
        
        if self._Adapter!= None:
            try:
                self._Adapter.StopDiscovery()
            except Exception,e:
                print(str(e))
            
            try:
                self._Adapter.StartDiscovery()
            except Exception,e:
                err_name = e.get_dbus_name()
                if err_name == "org.freedesktop.DBus.Error.NoReply":
                    print("start discovery timeout")
                else:
                    print("start discovery unknown err: ", str(e))
            
    def OnReturnBackCb(self):
        self.RefreshDevices()
        self.GenNetworkList()
    
    def OnLoadCb(self):
        self._Offline = False
        if self._Screen._TitleBar._InAirPlaneMode == False:
            out = commands.getstatusoutput("hcitool dev | grep hci0 |cut -f3") ## bluetooth maybe dead after airplane mode
            if len(out[1]) < 17:
                self._Offline = True
                print("Bluetooth OnLoadCb ,can not find hci0 alive,try to reboot")
            else:
                self.RefreshDevices()
                self.GenNetworkList()
        else:
            self._Offline = True
            
    def KeyDown(self,event):
        
        if IsKeyMenuOrB(event.key):
            if self._Offline == True:
                self.AbortedAndReturnToUpLevel()
                return
            
            if self._Adapter != None:
                try:
                    self._Adapter.StopDiscovery()
                except Exception,e:
                    print(str(e))
                
                _connecting = self.CheckIfBluetoothConnecting()
                if _connecting:
                    self.ShutDownConnecting()
                    self.ShowBox(MyLangManager.Tr("ShutDownConnecting"))
                    self.AbortedAndReturnToUpLevel()
                else:
                    self.AbortedAndReturnToUpLevel()
            else:
                self.HideBox()
                self.ReturnToUpLevelPage()
                self._Screen.Draw()
                self._Screen.SwapAndShow()
            
            self._Screen._FootBar.ResetNavText()
            
        if event.key == CurKeys["Up"]:
            self.ScrollUp()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        if event.key == CurKeys["Down"]:
            self.ScrollDown()
            self._Screen.Draw()
            self._Screen.SwapAndShow()       
        
        if event.key == CurKeys["X"]:
            if self._Offline == False:
                self.Rescan()   

        if event.key == CurKeys["Y"]:
            if len(self._MyList) == 0:
                return
            if self._Offline == True:
                return
            
            self._InfoPage._AList = self._MyList[self._PsIndex]._Atts
            self._InfoPage._Path  = self._MyList[self._PsIndex]._Path
            self._Screen.PushPage(self._InfoPage)
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
        if IsKeyStartOrA(event.key):
            if self._Offline == False:
                self.TryConnect()

    def Draw(self):
        self.ClearCanvas()
        if len(self._MyList) == 0:
            return
                
        if len(self._MyList) * NetItem._Height > self._Height:
            self._Ps._Width = self._Width - 11
            self._Ps.Draw()
            
            for i in self._MyList:
                i.Draw()        
            
            self._Scroller.UpdateSize( len(self._MyList)*NetItem._Height, self._PsIndex*NetItem._Height)
            self._Scroller.Draw()
        else:
            self._Ps._Width = self._Width
            self._Ps.Draw()

            for i in self._MyList:
                i.Draw()



BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/gameshell/bleagent"

class APIOBJ(object):

    _Page = None
    _PairPage = None
    _Page3 = None
    _Prompts = {} # string key,string value
    _PromptType = None
    _MyAgent = None
    
    def __init__(self):
        self._Prompts["PIN"]=""
        self._Prompts["PASS"]=""

    def OnKbdReturnBackCb(self):
        if self._PromptType == None:
            return
        else:
            if self._PromptType in self._Prompts:
                inputed = "".join(self._Page3._Textarea._MyWords)
                self._Prompts[self._PromptType] = inputed
            
            self._PromptType = None ##clear 
                
        
    def Ask(self,prompt,prompt_type=None):
        
        self._Screen.PushPage(self._Page3)
        self._Page3.SetPassword("")
        self._Page3._Name = prompt
        self._Page3._Caller = self
        
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
        if prompt_type != None:
            self._PromptType = prompt_type
        
    def RegisterMyAgent(self):
        global AGENT_PATH, bus,devices,adapter
        
        capability = "KeyboardDisplay"
        self._MyAgent = BleAgent(bus, AGENT_PATH)
        self._MyAgent._Leader = self
        
        obj = bus.get_object(BUS_NAME, "/org/bluez");
        manager = dbus.Interface(obj, "org.bluez.AgentManager1")
        manager.RegisterAgent(AGENT_PATH, capability)
        print("BleAgent %s registered" % AGENT_PATH)
        
    def Init(self,main_screen):
        global bus,devices,adapter
        
        self._Page = BluetoothPage()
        self._Page._Dbus = bus
        self._Page._Devices = devices
        self._Page._Adapter = adapter
        
        self._Page._Screen = main_screen
        self._Page._Name ="Bluetooth"
        
        self._Page._Leader = self
        
        self._Page.Init()
        
        self._PairPage = BleAgentPairPage()
        self._PairPage._Screen = main_screen
        self._PairPage._Name = "Bluetooth"
        self._PairPage.Init()
        
        self._Page3= Keyboard()
        self._Page3._Name = "Enter"
        self._Page3._Screen = main_screen
        self._Page3.Init()
        
        bus.add_signal_receiver(self._Page.DbusPropertiesChanged,
            dbus_interface = "org.freedesktop.DBus.Properties",
            signal_name = "PropertiesChanged",
            arg0 = "org.bluez.Device1",
            path_keyword = "path")
        
        self.RegisterMyAgent()
        
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
