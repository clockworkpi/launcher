# -*- coding: utf-8 -*- 

import pygame

from beeprint import pp
from libs.roundrects import aa_round_rect
import gobject
from wicd import misc 
## local UI import
from UI.constants import Width,Height
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.fonts  import fonts
from UI.util_funcs import midRect,SwapAndShow
from UI.keys_def   import CurKeys
from UI.scroller   import ListScroller
from UI.confirm_page import ConfirmPage

from net_item import NetItem

import myvars


class InfoPageListItem(object):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 30

    _Labels = {}
    _Icons  = {}
    _Fonts  = {}

    _LinkObj = None
    
    def __init__(self):
        self._Labels = {}
        self._Icons  = {}
        self._Fonts  = {}

    def SetSmallText(self,text):
        
        l = Label()
        l._PosX = 40
        l.SetCanvasHWND(self._Parent._CanvasHWND)
        l.Init(text,self._Fonts["small"])
        self._Labels["Small"] = l
        
    def Init(self,text):

        #self._Fonts["normal"] = fonts["veramono12"]
        
        l = Label()
        l._PosX = 10
        l.SetCanvasHWND(self._Parent._CanvasHWND)

        l.Init(text,self._Fonts["normal"])
        self._Labels["Text"] = l

    def Draw(self):
        
        self._Labels["Text"]._PosY = self._PosY + (self._Height - self._Labels["Text"]._Height)/2
        self._Labels["Text"].Draw()

        if "Small" in self._Labels:
            self._Labels["Small"]._PosX = self._Width - self._Labels["Small"]._Width-5
            
            self._Labels["Small"]._PosY = self._PosY + (self._Height - self._Labels["Small"]._Height)/2
            self._Labels["Small"].Draw()
        
        pygame.draw.line(self._Parent._CanvasHWND,(169,169,169),(self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)
    


class WifiDisconnectConfirmPage(ConfirmPage):

    _ConfirmText = "Confirm Disconnect?"
    
    def KeyDown(self,event):
        if event.key == CurKeys["Menu"] or event.key == CurKeys["A"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
        if event.key == CurKeys["B"]:
            self.SnapMsg("Disconnecting...")
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
            self._Parent._Daemon.Disconnect()
            
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
        
class WifiInfoPageSelector(PageSelector):
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
            
class WifiInfoPage(Page):
    _FootMsg =  ["Nav.","Disconnect","","Back",""]
    _MyList = []
    _ListFontObj = fonts["varela15"]

    _Wireless = None
    _Daemon   = None
    
    _AList = {}
    _NetworkId = -1
    
    def GenList(self):
        
        self._MyList = []
        if self._NetworkId != -1:
            self._AList["ip"]["value"] = "Not Connected"
            
            if self._Wireless.GetCurrentNetworkID(self._Wireless.GetIwconfig()) == self._NetworkId:
                ip = self._Wireless.GetWirelessIP('')
            
                if ip is not None:
                    self._AList["ip"]["value"] = ip
            
            self._AList["bssid"]["value"] = self._Wireless.GetWirelessProperty(self._NetworkId,"bssid")
        
        start_x  = 0
        start_y  = 0
        
        for i,v in enumerate( self._AList):
            li = InfoPageListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + i*InfoPageListItem._Height
            li._Width  = Width
            li._Fonts["normal"] = self._ListFontObj
            li._Fonts["small"] = fonts["varela12"]
            
            if self._AList[v]["label"] != "":
                li.Init(  self._AList[v]["label"] )
            else:
                li.Init( self._AList[v]["key"] )

            li._Flag = self._AList[v]["key"]

            li.SetSmallText( self._AList[v]["value"] )
            
            self._MyList.append(li)
            
    def Init(self):
        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._CanvasHWND = self._Screen._CanvasHWND

        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height

        ps = WifiInfoPageSelector()
        ps._Parent = self
        self._Ps = ps
        self._PsIndex = 0

        ip = {}
        ip["key"] = "ip"
        ip["label"] = "IP"
        ip["value"] = "Not Connected"
        
        bssid = {}
        bssid["key"] = "bssid"
        bssid["label"] = "BSSID"
        bssid["value"] = ""
        
        self._AList["ip"] = ip
        self._AList["bssid"] = bssid
        
        self.GenList()

        self._DisconnectConfirmPage = WifiDisconnectConfirmPage()
        self._DisconnectConfirmPage._Screen = self._Screen
        self._DisconnectConfirmPage._Name   = "Confirm Disconnect"
        self._DisconnectConfirmPage._Parent = self
        self._DisconnectConfirmPage.Init()
        
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
        print(cur_li._Flag)        

    def TryDisconnect(self):
        if self._Wireless.GetCurrentNetworkID(self._Wireless.GetIwconfig()) == self._NetworkId \
           and self._Wireless.GetWirelessIP('') is not None:
            self._Screen.PushPage(self._DisconnectConfirmPage)
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        else:
            return
        
    def OnLoadCb(self):
        if self._Wireless.GetCurrentNetworkID(self._Wireless.GetIwconfig()) == self._NetworkId \
           and self._Wireless.GetWirelessIP('') is not None:
            self._FootMsg[1] = "Disconnect"
        else:
            self._FootMsg[1] =  ""

        self.GenList()

    def OnReturnBackCb(self):
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
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

        if event.key == CurKeys["X"]:
            self.TryDisconnect()
                                
    def Draw(self):
        self.ClearCanvas()
        self._Ps.Draw()

        for i in self._MyList:
            i.Draw()


        
    
class WifiListSelector(PageSelector):
    _BackgroundColor = pygame.Color(131,199,219)

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


class WifiListMessageBox(Label):
    _Parent = None

    def Draw(self):
        my_text = self._FontObj.render( self._Text,True,self._Color)
        w  = my_text.get_width()
        h  = my_text.get_height()
        x  = (self._Parent._Width - w)/2
        y =  (self._Parent._Height - h)/2
        padding = 10 
        pygame.draw.rect(self._CanvasHWND,(255,255,255),(x-padding,y-padding, w+padding*2,h+padding*2))        

        pygame.draw.rect(self._CanvasHWND,(0,0,0),(x-padding,y-padding, w+padding*2,h+padding*2),1)

        self._CanvasHWND.blit(my_text,(x,y,w,h))

class WifiList(Page):
    _WirelessList = []
    #Wicd dbus part
    _Wireless = None
    _Daemon   = None
    _Dbus     = None
    _WifiPassword = ""
    _Connecting = False
    _Scanning   = False 
    
    _PrevWicdState = None
    
    _Selector = None
    
    _ShowingMessageBox = False 
    _MsgBox            = None
    _ConnectTry        = 0
    _BlockingUI        = False
    _BlockCb           = None
    
    _LastStatusMsg     = ""
    _FootMsg           = ["Nav.","Scan","Info","Back","Enter"]
    _EncMethods        = None
    _Scroller          = None
    _ListFontObj       = fonts["notosanscjk15"]

    _InfoPage          = None
    
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

    def GenNetworkList(self):
        self._WirelessList = []
        start_x = 0
        start_y = 0

        for network_id in range(0,self._Wireless.GetNumberOfNetworks()):
            is_active = \
                self._Wireless.GetCurrentSignalStrength("") != 0 and \
                self._Wireless.GetCurrentNetworkID(self._Wireless.GetIwconfig()) == network_id \
                and self._Wireless.GetWirelessIP('') is not None

            ni = NetItem()
            ni._Parent = self
            ni._PosX = start_x
            ni._PosY = start_y + network_id* NetItem._Height
            ni._Width = Width
            ni._FontObj = self._ListFontObj
            #ni._Bssid   = self._Wireless.GetWirelessProperty(network_id,"bssid")
            
            ni.Init(network_id,is_active)
            self._WirelessList.append(ni)

        self._PsIndex = 0
        
    def Disconnect(self):
        self._Connecting= False
        self._Daemon.Disconnect()
    ## force to disconnect
    def ShutDownConnecting(self):
        print("Shutdownconnecting...",self._ConnectTry)
        self._Daemon.CancelConnect()
        self._Daemon.SetForcedDisconnect(True)
        self._Connecting = False

    def Rescan(self,sync=False):
        print("start Rescan")
        if self._Wireless != None:
            self._Wireless.Scan(sync)

## dbus signal functions
    def DbusScanFinishedSig(self):

        if self._Screen._CurrentPage != self:
            return
        self.ResetPageSelector()
        
        self.UpdateNetList(force_check=True)

        self._Scanning = False
        self.HideBox()
        self._BlockingUI = False
        print("dbus says scan finished")

    def DbusScanStarted(self):
        if self._Screen._CurrentPage !=self:
            return
        
        self._Scanning = True
        self.ShowBox("Wifi scanning...")
        self._BlockingUI = True
        print("dbus says start scan...")


    def UpdateNetList(self,state=None,info=None,force_check=False,firstrun=False):

        if self._Daemon == None:
            return
        
        if not state:
            state,trash = self._Daemon.GetConnectionStatus()
            print("state")
            pp(state)
            print("Trash: ")
            pp(trash)

        if force_check or self._PrevWicdState != state:
            self.GenNetworkList() ## refresh the network list 
        
        if info != None:
            if len(info) > 3:
                _id  = int(info[3])
                if _id < len(self._WirelessList):
                    self._WirelessList[_id].UpdateStrenLabel( str(info[2]))

        self._PrevWicdState = state
        
    def SetConnectingStatus(self,fast):
        
        wireless_connecting = self._Wireless.CheckIfWirelessConnecting()

        """
        if self._ConnectTry > 5000:
            #wicd itself will take a very long time to try to connect ,will not block forever,just make it faster to dropout
            self.ShutDownConnecting()
            self._ConnectTry = 0
            self._BlockingUI = False
            return False
        """
        
        if wireless_connecting:
            if not fast:
                iwconfig = self._Wireless.GetIwconfig()
            else:
                iwconfig = ''
            essid = self._Wireless.GetCurrentNetwork(iwconfig)
            stat = self._Wireless.CheckWirelessConnectingMessage()
            if self._LastStatusMsg != "%s: %s"%(essid,stat):
                print("%s: %s" %(essid,stat))
                self._LastStatusMsg = "%s: %s"%(essid,stat)
                self.ShowBox(self._LastStatusMsg)
                
                self._Screen._FootBar.UpdateNavText(self._LastStatusMsg)
                SwapAndShow()
                
            #self._ConnectTry+=1

            return True
        else:
            self._Connecting = False
            return self._Connecting

    def UpdateStatus(self):
        print("UpdateStatus")
        wireless_connecting = self._Wireless.CheckIfWirelessConnecting()
        fast = not self._Daemon.NeedsExternalCalls()
        
        self._Connecting = wireless_connecting
        
        if self._Connecting:
            gobject.timeout_add(250,self.SetConnectingStatus,fast)
        else:
            if not fast:
                iwconfig = self._Wireless.GetIwconfig()
            else:
                iwconfig = ''

            if self.CheckForWireless(iwconfig,self._Wireless.GetWirelessIP(''),None):
                return True
            else:
                print("Not Connected")
                return True

    def DbusDaemonStatusChangedSig(self,state=None,info=None):
        if self._Screen._CurrentPage != self:
            return

        print("in DbusDaemonStatusChangedSig")
        """
        dbus.UInt32(2L)
        ['192.168.31.141', 'TP-LINK4G', '88', '0', '72.2 Mb/s']
        """
        pp(info)
        self.UpdateNetList(state,info)
        if info != None:
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        

    def DbusConnectResultsSent(self,result):
        print(" in DbusConnectResultsSent")
        """
         in DbusConnectResultsSent
        'dhcp_failed'
        dbus says start scan...

        """
        if result != None:
            print(result)
            
        self._Connecting = False
        self._BlockingUI = False
        if self._BlockCb != None:
            self._BlockCb()
            self._BlockCb = None

        self._Screen._FootBar.ResetNavText()
    
    def CheckForWireless(self,iwconfig,wireless_ip,set_status):
        if not wireless_ip:
            return False
        network = self._Wireless.GetCurrentNetwork(iwconfig)
        if not network:
            return False
        network = misc.to_unicode(network)
        if daemon.GetSignalDisplayType() == 0:
            strength = self._Wireless.GetCurrentSignalStrength(iwconfig)
        else:
            strength = self._Wireless.GetCurrentDBMStrength(iwconfig)

        if strength is None:
            return False
        strength = misc.to_unicode(self._Daemon.FormatSignalForPrinting(strength))
        ip = misc.to_unicode(wireless_ip)

        print(_('Connected to $A at $B (IP: $C)').replace
                    ('$A', network).replace
                    ('$B', strength).replace
                    ('$C', ip))
        
        return True

    def ConfigWireless(self,password):
        netid = self._PsIndex
        print(netid," ", password)
        """
        self._Wireless.SetWirelessProperty(netid,"dhcphostname","GameShell")
        self._Wireless.SetWirelessProperty(netid,"ip","None")
        self._Wireless.SetWirelessProperty(netid,"dns_domain","None")
        self._Wireless.SetWirelessProperty(netid,"gateway","None")
        self._Wireless.SetWirelessProperty(netid,"use_global_dns",0)
        self._Wireless.SetWirelessProperty(netid,"netmask","None")
        self._Wireless.SetWirelessProperty(netid,"usedhcphostname",0) ## set 1 to use hostname above
        self._Wireless.SetWirelessProperty(netid,"bitrate","auto")
        self._Wireless.SetWirelessProperty(netid,"allow_lower_bitrates",0)
        self._Wireless.SetWirelessProperty(netid,"dns3","None")
        self._Wireless.SetWirelessProperty(netid,"dns2","None")
        self._Wireless.SetWirelessProperty(netid,"dns1","None")
        self._Wireless.SetWirelessProperty(netid,"use_settings_globally",0)
        self._Wireless.SetWirelessProperty(netid,"use_static_dns",0)
        self._Wireless.SetWirelessProperty(netid,"search_domain","None")
        """
        self._Wireless.SetWirelessProperty(netid,"enctype","wpa-psk")
        self._Wireless.SetWirelessProperty(netid,"apsk",password)
        self._Wireless.SetWirelessProperty(netid,"automatic",1)

        
        self._WirelessList[netid].Connect()
        print("after Connect")
        self.UpdateStatus()

    def GetWirelessEncrypt(self,network_id):
        results = []
        activeID = -1
        for x,enc_type in enumerate(self._EncMethods):
            if enc_type["type"] == self._Wireless.GetWirelessProperty(network_id,"enctype"):
                activeID = x
                break

        if activeID == -1:
            return results
        
        for type_ in ['required','optional']:
            fields = self._EncMethods[activeID][type_]
            for field in fields:
                try:
                    text = field[1].lower().replace(' ','_')
                except KeyError:
                    text = field[1].replace(' ','_')
                
                value = self._Wireless.GetWirelessProperty(network_id, field[0])
                results.append({text:value})
        """
        [{'preshared_key': 'blah blah blah',},]

        or nothing 
        [{'identity': None,},{'password': None,},]

        """
        return results

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
    

    def AbortedAndReturnToUpLevel(self):
        self.HideBox()
        self._Screen._FootBar.ResetNavText()
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
    def KeyDown(self,event):

        if self._BlockingUI == True:
            print("UI blocking ...")
            return
        
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            if self._Wireless != None:
                wireless_connecting = self._Wireless.CheckIfWirelessConnecting()
                if wireless_connecting:
                    self.ShutDownConnecting()
                    self.ShowBox("ShutDownConnecting...")
                    self._BlockingUI=True
                    self._BlockCb = self.AbortedAndReturnToUpLevel
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
            
        if event.key == CurKeys["Enter"]: ## enter to set password,enter is B on GM
            if len(self._WirelessList) == 0:
                return
            
            wicd_wirelss_encrypt_pwd = self.GetWirelessEncrypt(self._PsIndex)
            
            if self._WirelessList[self._PsIndex]._IsActive:
                self.ShowBox( self._Wireless.GetWirelessIP('')    )
            else:
                self._Screen.PushCurPage()
                self._Screen.SetCurPage( myvars.PasswordPage )
                
                thepass = ""
                for i in wicd_wirelss_encrypt_pwd:
                    if "preshared_key" in i:
                        if i["preshared_key"] != None:
                            if len(i["preshared_key"]) > 0:
                                thepass = i["preshared_key"]
                                break
                
                myvars.PasswordPage.SetPassword(thepass)
                self._Screen.Draw()
                self._Screen.SwapAndShow()
                
                """
                try:
                    self._Screen.Draw()
                    self._Screen.SwapAndShow()
                except Exception as e: 
                    print(e)
                    exit(-1)
                """
        if event.key == CurKeys["X"]:
            self.Rescan(False)
            
        if event.key == CurKeys["Y"]:
            if len(self._WirelessList) == 0:
                return

            self._InfoPage._NetworkId = self._PsIndex
            self._InfoPage._Wireless  = self._Wireless
            self._InfoPage._Daemon    = self._Daemon
            
            self._Screen.PushPage(self._InfoPage)
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            

    def Init(self):
        
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height

        #self._CanvasHWND = pygame.Surface((self._Width,self._Height))
        self._CanvasHWND = self._Screen._CanvasHWND

        ps = WifiListSelector()
        ps._Parent = self
        ps._Width = Width - 12
        
        self._Ps = ps
        self._PsIndex = 0
        
        msgbox = WifiListMessageBox()
        msgbox._CanvasHWND = self._CanvasHWND
        msgbox.Init(" ",fonts["veramono12"])
        msgbox._Parent = self
        
        self._MsgBox = msgbox 

        self._EncMethods = misc.LoadEncryptionMethods() # load predefined templates from /etc/wicd/...

        """
  {
    'fields': [],
    'name': 'WPA 1/2 (Passphrase)',
    'optional': [],
    'protected': [
      ['apsk', 'Preshared_Key'],
    ],
    'required': [
      ['apsk', 'Preshared_Key'],
    ],
    'type': 'wpa-psk',
  },
        """
        
        self.UpdateNetList(force_check=True,firstrun=True)

        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = 2
        self._Scroller._PosY = 2
        self._Scroller.Init()


        self._InfoPage = WifiInfoPage()
        self._InfoPage._Screen = self._Screen
        self._InfoPage._Name   = "Wifi info"
        self._InfoPage.Init()
        
    def Draw(self):
        self.ClearCanvas()

        if len(self._WirelessList) == 0:
            return
        
        self._Ps.Draw()
        for i in self._WirelessList:
            i.Draw()

        
        self._Scroller.UpdateSize( len(self._WirelessList)*NetItem._Height, self._PsIndex*NetItem._Height)
        self._Scroller.Draw()
