# -*- coding: utf-8 -*- 
import pygame
import validators
import  commands

from UI.constants import Width,Height,ICON_TYPES
from UI.simple_name_space import SimpleNamespace
from UI.page  import Page
from UI.label  import Label
from UI.icon_item import IconItem
from UI.icon_pool import MyIconPool
from UI.keys_def  import CurKeys, IsKeyMenuOrB
from UI.skin_manager import MySkinManager
from UI.lang_manager import MyLangManager

from libs.DBUS  import is_wifi_connected_now,get_wifi_ip

class TinyCloudPage(Page):
    _FootMsg =  ["Nav","","","Back",""]
    _MyList = []
    
    _ListFontObj = MyLangManager.TrFont("varela13")
    
    _AList = {}
    _Labels = {}

    _Coords = {}
    
    _URLColor  = MySkinManager.GiveColor('URL')
    _TextColor = MySkinManager.GiveColor('Text')
    _Scrolled = 0
    
    _PngSize = {}
    
    _DrawOnce = False
    _Scroller = None
    _Scrolled = 0
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}

    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self._DrawOnce = False

    def SetCoords(self):

        self._Coords["forID"] = SimpleNamespace()
        self._Coords["forID"].x = 15
        self._Coords["forID"].y = 11

        self._Coords["forKey"] = SimpleNamespace()
        self._Coords["forKey"].x = 71
        self._Coords["forKey"].y = self._Coords["forID"].y

        self._Coords["key_and_pass"] = SimpleNamespace()
        self._Coords["key_and_pass"].x = 36 # 141
        self._Coords["key_and_pass"].y = self._Coords["forID"].y

        self._Coords["forssh"] = SimpleNamespace()
        self._Coords["forssh"].x = self._Coords["forID"].x
        self._Coords["forssh"].y = 36

        self._Coords["ssh_addr"] = SimpleNamespace()
        self._Coords["ssh_addr"].x = self._Coords["forID"].x
        self._Coords["ssh_addr"].y = 54

        self._Coords["forwin"] = SimpleNamespace()
        self._Coords["forwin"].x = self._Coords["forID"].x
        self._Coords["forwin"].y = 80

        self._Coords["samba_games"] = SimpleNamespace()
        self._Coords["samba_games"].x = self._Coords["forID"].x
        self._Coords["samba_games"].y = 97

        self._Coords["samba_music"] = SimpleNamespace()
        self._Coords["samba_music"].x = self._Coords["samba_games"].x
        self._Coords["samba_music"].y = 115

        self._Coords["for_airplay"] = SimpleNamespace()
        self._Coords["for_airplay"].x = self._Coords["forID"].x
        self._Coords["for_airplay"].y = 140

        self._Coords["airplay_name"] = SimpleNamespace()
        self._Coords["airplay_name"].x = 68
        self._Coords["airplay_name"].y = self._Coords["for_airplay"].y
        
        self._Coords["for-usb-eth"] = SimpleNamespace()
        self._Coords["for-usb-eth"].x = self._Coords["forID"].x
        self._Coords["for-usb-eth"].y = 163
        
        self._Coords["usb-eth-addr"] = SimpleNamespace()
        self._Coords["usb-eth-addr"].x = 112
        self._Coords["usb-eth-addr"].y = self._Coords["for-usb-eth"].y

        self._Coords["bg"]          = SimpleNamespace()
        self._Coords["bg"].x        = self._Width/2
        self._Coords["bg"].y        = self._Height/2

        self._Coords["online"]          = SimpleNamespace()
        self._Coords["online"].x        = 266
        self._Coords["online"].y        = 99

    def SetLabels(self):
        if is_wifi_connected_now():
            self._IP = get_wifi_ip()
            print("TinyCould : %s" % self._IP)
            try:
                if validators.ip_address.ipv4(self._IP) == False:
                    self._IP = "xxx.xxx.xxx.xxx"
            except:
                print("ip error %s " % self._IP)
                self._IP = "xxx.xxx.xxx.xxx"
            
        else:
            self._IP = "xxx.xxx.xxx.xxx"
        
        hostname = commands.getstatusoutput("hostname")[1]
        if hostname == "":
            hostname = "clockworkpi"
                    
        labels = \
        [["forssh","For ssh and scp:",self._ListFontObj,self._TextColor],
         ["ssh_addr","ssh cpi@%s" % self._IP, self._ListFontObj,self._URLColor],
         ["forwin", "For Windows network:",    self._ListFontObj, self._TextColor],
         ["samba_games", "\\\\%s\games" % self._IP, self._ListFontObj,self._URLColor],
         ["samba_music", "\\\\%s\music" % self._IP, self._ListFontObj,self._URLColor],
         ["forID",      "ID:",                     self._ListFontObj, self._TextColor],
         ["forKey",     "Key:",                    self._ListFontObj, self._TextColor],
         ["key_and_pass", "cpi",                   self._ListFontObj, self._URLColor],
         ["for_airplay", "Airplay:",               self._ListFontObj, self._TextColor],
         ["airplay_name",hostname,            self._ListFontObj, self._URLColor],
         ["for-usb-eth","USB-Ethernet:",            self._ListFontObj, self._TextColor],
         ["usb-eth-addr","192.168.10.1",            self._ListFontObj, self._URLColor]]

        for i in labels:
            l = Label()
            l.SetCanvasHWND(self._CanvasHWND)
            l.Init(i[1],i[2])
            l.SetColor(i[3])
            self._Labels[ i[0] ] = l

        self.SetCoords() ##
        
    def Init(self):

        
        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._HWND = self._Screen._CanvasHWND
                self._CanvasHWND = pygame.Surface( (self._Screen._Width,self._Screen._Height) )
        
        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height

        self._PngSize["bg"] = (253,114)
        self._PngSize["online"] = (75,122)
        
        bgpng = IconItem()
        bgpng._ImgSurf = MyIconPool.GiveIconSurface("needwifi_bg")
        bgpng._MyType = ICON_TYPES["STAT"]
        bgpng._Parent = self
        bgpng.Adjust(0,0,self._PngSize["bg"][0],self._PngSize["bg"][1],0)

        self._Icons["bg"] = bgpng
        
        onlinepng = IconItem()
        onlinepng._ImgSurf = MyIconPool.GiveIconSurface("online")
        onlinepng._MyType = ICON_TYPES["STAT"]
        onlinepng._Parent = self
        onlinepng.Adjust(0,0,self._PngSize["online"][0], self._PngSize["online"][1],0)

        self._Icons["online"] = onlinepng

        self.SetLabels()

    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
    def Draw(self):
        if self._DrawOnce == False:
            self.ClearCanvas()

            if is_wifi_connected_now():
                
                self._Icons["online"].NewCoord(self._Coords["online"].x, self._Coords["online"].y)
                self._Icons["online"].Draw()

                self.SetLabels()
                
                for i in self._Labels:
                    if i in self._Coords:
                        self._Labels[i].NewCoord( self._Coords[i].x, self._Coords[i].y)
                        self._Labels[i].Draw()

                self._Labels["key_and_pass"].NewCoord( 103,self._Coords["key_and_pass"].y)
                self._Labels["key_and_pass"].Draw()

            else:
                self._Labels["for-usb-eth"].NewCoord(self._Coords["for-usb-eth"].x+55, self._Coords["for-usb-eth"].y)
                self._Labels["for-usb-eth"].Draw()
                
                self._Labels["usb-eth-addr"].NewCoord(self._Coords["usb-eth-addr"].x+55, self._Coords["usb-eth-addr"].y)
                self._Labels["usb-eth-addr"].Draw()                
                
                self._Icons["bg"].NewCoord(self._Coords["bg"].x, self._Coords["bg"].y)
                self._Icons["bg"].Draw()

                
            self._DrawOnce = True
            
        if self._HWND != None:
            self._HWND.fill(MySkinManager.GiveColor('White'))
            self._HWND.blit(self._CanvasHWND,(self._PosX,self._PosY,self._Width, self._Height ) )
            
            
        
class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = TinyCloudPage()
        self._Page._Screen = main_screen
        self._Page._Name ="Tiny cloud"
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
    
        
