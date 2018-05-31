# -*- coding: utf-8 -*- 

import pygame

## local UI import
from UI.page   import Page
from UI.label  import Label
from UI.fonts  import fonts
from UI.icon_item import IconItem
from UI.multi_icon_item  import MultiIconItem
from UI.icon_pool   import MyIconPool


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

    _Bssid=""    # 50:3A:A0:51:18:3C
    _Essid=""    # MERCURY_EB88

    ## extra infomations
    _dhcphostname = "GameShell"
    _ip   = None      #eg 192.168.31.141
    _dns_domain = None
    _gateway    = None  #eg 192.168.31.1
    _use_global_dns = 0 ## eg 0 == False, 1 == True
    _netmask    = None ##eg 255.255.255.0
    _usedhcphostname= 0
    _bitrate = "auto"
    _allow_lower_bitrates = 0
    _dns3 = None
    _dns2 = None  ## eg 1.1.1.1
    _dns1 = None  ## eg 8.8.8.8
    _use_settings_globally = 0 
    _use_static_dns = 0 # eg: 1 == True
    _search_domain = None
    
    _Encrypt=""  # WPA2
    _Channel=""  # '10' 
    _Stren = ""  ## 19%
    _NetId    = 0   ##  0-n
    _Mode  = ""  ## Master or AdHoc
    _Parent = None
    _IsActive = False

    _Icons  = {} ## wifi strength and security icons
    _Labels = {}
    _FontObj = None
    
    def __init__(self):
        self._Labels = {}
        self._Icons = {}

    def SetActive(self,act):
        self._IsActive = act
    
    def UpdateStrenLabel(self, strenstr): ## strenstr should be 'number',eg:'90'
        self._Stren = self._Parent._Daemon.FormatSignalForPrinting(strenstr) 
        self._Labels["stren"]._Text = self._Stren

    def Init(self, i, is_active):
        # Pick which strength measure to use based on what the daemon says
        # gap allocates more space to the first module
        if self._Parent._Daemon.GetSignalDisplayType() == 0:
            strenstr = 'quality'
            gap = 4  # Allow for 100%
        else:
            strenstr = 'strength'
            gap = 7  # -XX dbm = 7
        self._NetId = i
        # All of that network property stuff
        self._Stren = self._Parent._Daemon.FormatSignalForPrinting(
                str(self._Parent._Wireless.GetWirelessProperty(self._NetId, strenstr)))
        
        self._Essid = self._Parent._Wireless.GetWirelessProperty(self._NetId, 'essid')
        self._Bssid = self._Parent._Wireless.GetWirelessProperty(self._NetId, 'bssid')

        if self._Parent._Wireless.GetWirelessProperty(self._NetId, 'encryption'):
            self._Encrypt = \
                self._Parent._Wireless.GetWirelessProperty(self._NetId, 'encryption_method')
        else:
            self._Encrypt = 'Unsecured'

        self._Mode = \
            self._Parent._Wireless.GetWirelessProperty(self._NetId, 'mode')  # Master, Ad-Hoc
        self._Channel = self._Parent._Wireless.GetWirelessProperty(self._NetId, 'channel')
        theString = '  %-*s %25s %9s %17s %6s %4s' % \
            (gap, self._Stren, self._Essid, self._Encrypt, self._Bssid, self._Mode,
                self._Channel)
        
        if is_active:
            theString = ">> "+theString[1:]
            self.SetActive(is_active)
        


        essid_label = Label()
        essid_label._PosX = 36
        #essid_label._PosY = self._PosY +  (self._Height - self._FontObj.render(self._Essid,True,(83,83,83)).get_height())/2
        essid_label._CanvasHWND = self._Parent._CanvasHWND

        if len(self._Essid) > 19:
            essid_ = self._Essid[:20]
        else:
            essid_ = self._Essid
        
        essid_label.Init(essid_,self._FontObj)
        self._Labels["essid"] = essid_label

        stren_label = Label()
        #stren_label._PosY = self._PosY +  (self._Height - self._FontObj.render(self._Stren,True,(83,83,83)).get_height())/2
        stren_label._CanvasHWND = self._Parent._CanvasHWND

        stren_label.Init(self._Stren,self._FontObj)
        stren_label._PosX = self._Width - 23 - stren_label.Width() - 2
        self._Labels["stren"] = stren_label
        

        lock_icon = NetItemIcon()
        lock_icon._ImgSurf = MyIconPool._Icons["lock"]
        lock_icon._CanvasHWND = self._Parent._CanvasHWND
        lock_icon._Parent = self
        self._Icons["lock"] = lock_icon
        
        done_icon = NetItemIcon()
        done_icon._ImgSurf = MyIconPool._Icons["done"]
        done_icon._CanvasHWND = self._Parent._CanvasHWND
        done_icon._Parent = self
        
        self._Icons["done"] = done_icon


        ## reuse the resource from TitleBar
        nimt = NetItemMultiIcon()
        nimt._ImgSurf = self._Parent._Screen._TitleBar._Icons["wifistatus"]._ImgSurf
        nimt._CanvasHWND = self._Parent._CanvasHWND
        nimt._Parent = self
        self._Icons["wifistatus"] = nimt

        #pp(theString)
    
    
    def Connect(self,notworkentry=None):
        """ Execute connection. """
        self._Parent._Wireless.ConnectWireless(self._NetId)

    
    def Draw(self):
        #pygame.draw.line(self._Parent._CanvasHWND,(169,169,169),(self._PosX,self._PosY),(self._PosX+self._Width,self._PosY),1)        
        for i in self._Labels:
            self._Labels[i]._PosY = self._PosY + (self._Height - self._Labels[i]._Height)/2
            self._Labels[i].Draw()
            
        if self._IsActive:
            self._Icons["done"].NewCoord(14,self._PosY)
            self._Icons["done"].Draw()

        if self._Encrypt != "Unsecured":
            self._Icons["lock"].NewCoord( self._Width -23 - self._Labels["stren"].Width() - 2 - 18, self._PosY)
            self._Icons["lock"].Draw()
        
        ge = self._Parent._Screen._TitleBar.GetWifiStrength( self._Stren.replace('%',''))
        
        if ge > 0:
            self._Icons["wifistatus"]._IconIndex = ge
            self._Icons["wifistatus"].NewCoord(self._Width-23,self._PosY)
            self._Icons["wifistatus"].Draw()
            
        else:
            self._Icons["wifistatus"]._IconIndex = 0
            self._Icons["wifistatus"].NewCoord(self._Width-23,self._PosY)
            self._Icons["wifistatus"].Draw()
        
        pygame.draw.line(self._Parent._CanvasHWND,(169,169,169),(self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)        
        

