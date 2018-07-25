# -*- coding: utf-8 -*- 

import pygame
import os
import sys
import commands

from datetime import datetime

#from beeprint import pp

import alsaaudio

##local import
from constants   import ICON_TYPES,Width,Height
from fonts       import fonts
from icon_item   import IconItem
from multi_icon_item import MultiIconItem
from icon_pool   import MyIconPool

from util_funcs  import midRect,SwapAndShow,SkinMap

from config import Battery

from libs.roundrects import aa_round_rect

from libs.DBUS        import is_wifi_connected_now,wifi_strength

icon_base_path = SkinMap("gameshell/titlebar_icons/")
class TitleBar:
    _PosX      = 0
    _PosY      = 0
    _Width     = Width
    _Height    = 25
    _BarHeight  = 24.5
    _LOffset    = 3
    _ROffset    = 3
    _Icons      = {}
    _icon_width = 18
    _icon_height = 18
    _BorderWidth = 1
    _CanvasHWND  = None
    _HWND        = None
    _Title       = ""
    
    _InLowBackLight = -1

    _SkinManager = None

    _InAirPlaneMode = False
    
    def __init__(self):
        self._Icons = {}


    def GObjectRoundRobin(self):
        if self._InLowBackLight < 0:
            self.CheckBatteryStat()
            self.SyncSoundVolume()
            self.UpdateWifiStrength()
            SwapAndShow()
#            print("TitleBar Gobjectroundrobin")
        elif self._InLowBackLight >= 0:
            self._InLowBackLight+=1
            if self._InLowBackLight > 10:
                self.CheckBatteryStat()
                self.SyncSoundVolume()
                self.UpdateWifiStrength()
                self._InLowBackLight = 0
        
        return True
    
    def UpdateWifiStrength(self):
        self.Draw(self._Title)
        
    def GetWifiStrength(self,stren): ##invoke anytime to change title bar icon status
        #0-25
        #25-50
        #50-75
        #75-100
        
        segs = [[-2,-1], [0,25],[25,50],[50,75],[75,100] ]
        
        stren = int(stren)
        ge    = 0

        if stren == 0:
            return ge

        for i,v in enumerate(segs):
            if stren >= v[0] and stren <= v[1]:
                ge = i
                break
        
        return ge

    def SyncSoundVolume(self):
	try:
	        m = alsaaudio.Mixer()
	        vol = m.getvolume()[0]	
	except Exception,e:
		print(str(e))
	        vol = 0

        snd_segs = [ [0,10],[10,30],[30,70],[70,100] ]

        ge = 0
        for i,v in enumerate(snd_segs):
            if vol >= v[0] and vol <= v[1]:
                ge = i
                break

        self._Icons["soundvolume"]._IconIndex = ge
        self._Icons["sound"]       = self._Icons["soundvolume"]

        
    def SetSoundVolume(self,vol):
        pass
    
    def CheckBatteryStat(self): ## 100ms check interval
        content = ""
        bat_uevent = {}
        bat_segs=[ [0,6],[7,15],[16,20], [21,30],[31,50],[51,60],  [61,80],[81,90],[91,100] ]
        
        try:
            f = open(Battery)
        except IOError:
            self._Icons["battery"] = self._Icons["battery_unknown"]
#            print("CheckBatteryStat open failed")
            return False
        else:
            with f:
                content = f.readlines()
                content = [x.strip() for x in content]
                f.close()
                
                for i in content:
                    pis = i.split("=")
                    if len(pis) > 1:
                        bat_uevent[pis[0]] = pis[1]

                #        print(bat_uevent["POWER_SUPPLY_CAPACITY"])

                """
                power_current = int(bat_uevent["POWER_SUPPLY_CURRENT_NOW"])
                if power_current < 270000:
                self._Icons["battery"] = self._Icons["battery_unknown"]
                return False
                """

                if "POWER_SUPPLY_CAPACITY" in bat_uevent:
                    cur_cap = int(bat_uevent["POWER_SUPPLY_CAPACITY"])
                else:
                    cur_cap = 0
                    
                cap_ge = 0
                
                for i,v in enumerate(bat_segs):
                    if cur_cap >= v[0] and cur_cap <= v[1]:
                        cap_ge = i
                        break
        
                if bat_uevent["POWER_SUPPLY_STATUS"] == "Charging":
                    self._Icons["battery_charging"]._IconIndex = cap_ge
                    self._Icons["battery"] = self._Icons["battery_charging"]
            
                    print("Charging %d" % cap_ge)
                else:
                    self._Icons["battery_discharging"]._IconIndex = cap_ge
                    self._Icons["battery"] = self._Icons["battery_discharging"]
                    print("Discharging %d" % cap_ge)
                    
                
        return True
    
    def SetBatteryStat(self,bat):
        pass
    
    def Init(self,screen):
        
        
        start_x = 0
        self._CanvasHWND = pygame.Surface((self._Width,self._Height))
        self._HWND       = screen
        

        icon_wifi_status = MultiIconItem()
        icon_wifi_status._MyType = ICON_TYPES["STAT"]
        icon_wifi_status._ImageName = icon_base_path+"wifi.png"
        icon_wifi_status._Parent = self
        icon_wifi_status.Adjust(start_x+self._icon_width+5,self._icon_height/2+(self._BarHeight-self._icon_height)/2,self._icon_width,self._icon_height,0)
        self._Icons["wifistatus"] = icon_wifi_status    
        
        battery_charging = MultiIconItem()
        battery_charging._MyType = ICON_TYPES["STAT"]
        battery_charging._Parent = self
        battery_charging._ImageName = icon_base_path+"withcharging.png"
        battery_charging.Adjust(start_x+self._icon_width+self._icon_width+8,self._icon_height/2+(self._BarHeight-self._icon_height)/2,self._icon_width,self._icon_height,0)
        
        self._Icons["battery_charging"] = battery_charging

        battery_discharging = MultiIconItem()
        battery_discharging._MyType = ICON_TYPES["STAT"]
        battery_discharging._Parent = self
        battery_discharging._ImageName = icon_base_path+"without_charging.png"
        battery_discharging.Adjust(start_x+self._icon_width+self._icon_width+8,self._icon_height/2+(self._BarHeight-self._icon_height)/2,self._icon_width,self._icon_height,0)

        self._Icons["battery_discharging"] = battery_discharging

        battery_unknown   = IconItem()
        battery_unknown._MyType = ICON_TYPES["STAT"]
        battery_unknown._Parent = self
        battery_unknown._ImageName = icon_base_path+"battery_unknown.png"
        battery_unknown.Adjust(start_x+self._icon_width+self._icon_width+8,self._icon_height/2+(self._BarHeight-self._icon_height)/2,self._icon_width,self._icon_height,0)

        self._Icons["battery_unknown"] = battery_unknown
                        
        self.CheckBatteryStat()

        sound_volume   =  MultiIconItem()
        sound_volume._MyType = ICON_TYPES["STAT"]
        sound_volume._Parent = self
        sound_volume._ImageName = icon_base_path+"soundvolume.png"
        sound_volume.Adjust(start_x+self._icon_width+self._icon_width+8,self._icon_height/2+(self._BarHeight-self._icon_height)/2,self._icon_width,self._icon_height,0)

        self._Icons["soundvolume"] = sound_volume

        self.SyncSoundVolume()


        round_corners   =  MultiIconItem()
        round_corners._IconWidth = 10
        round_corners._IconHeight = 10
        
        round_corners._MyType = ICON_TYPES["STAT"]
        round_corners._Parent = self
        round_corners._ImgSurf = MyIconPool._Icons["roundcorners"]
        round_corners.Adjust(0,0,10,10,0)

        self._Icons["round_corners"] = round_corners
        
        if is_wifi_connected_now():
            print("wifi is connected")
            print( wifi_strength())
        else:
            out = commands.getstatusoutput('sudo rfkill list | grep yes | cut -d " " -f3')
            if out[1] == "yes":
                self._InAirPlaneMode = True
            else:
                self._InAirPlaneMode = False
            
    def ClearCanvas(self):
        self._CanvasHWND.fill( self._SkinManager.GiveColor("TitleBg") )

        self._Icons["round_corners"].NewCoord(5,5)
        self._Icons["round_corners"]._IconIndex = 0
        self._Icons["round_corners"].Draw()

        self._Icons["round_corners"].NewCoord(self._Width-5,5)
        self._Icons["round_corners"]._IconIndex = 1
        self._Icons["round_corners"].Draw()
        
        
        """
        aa_round_rect(self._CanvasHWND,  
                      (0,0,self._Width,self._Height),self._BgColor,8,0, self._BgColor)

        pygame.draw.rect(self._CanvasHWND,self._BgColor,(0,self._Height/2,Width,self._BarHeight), 0 )
        """
        
    def Draw(self,title):
        self.ClearCanvas()
        
        self._Title = title
        
        cur_time =  datetime.now().strftime("%H:%M")
        time_text_size = fonts["varela12"].size(cur_time)
        title_text_size = fonts["varela16"].size(title)

        self._CanvasHWND.blit(fonts["varela16"].render(title,True,self._SkinManager.GiveColor("Text")),midRect(title_text_size[0]/2+self._LOffset,
                                                                    title_text_size[1]/2+(self._BarHeight-title_text_size[1])/2,
                                                                    title_text_size[0],title_text_size[1],Width,Height))
        self._CanvasHWND.blit(fonts["varela12"].render(cur_time,True,self._SkinManager.GiveColor("Text")),midRect(Width-time_text_size[0]/2-self._ROffset,
                                                                        time_text_size[1]/2+(self._BarHeight-time_text_size[1])/2,
                                                                        time_text_size[0],time_text_size[1],Width,Height))

        start_x = Width-time_text_size[0]-self._ROffset-self._icon_width*3 # near by the time_text
        
        self._Icons["sound"].NewCoord(start_x,                      self._icon_height/2+(self._BarHeight-self._icon_height)/2)
        
        #self._Icons["wifi"].NewCoord(start_x+self._icon_width+5,    self._icon_height/2+(self._BarHeight-self._icon_height)/2)
        
        self._Icons["battery"].NewCoord(start_x+self._icon_width+self._icon_width+8,self._icon_height/2+(self._BarHeight-self._icon_height)/2)

        
        if is_wifi_connected_now():
            ge = self.GetWifiStrength(wifi_strength())
            if ge > 0:
                self._Icons["wifistatus"]._IconIndex = ge
                self._Icons["wifistatus"].NewCoord(start_x+self._icon_width+5,self._icon_height/2+(self._BarHeight-self._icon_height)/2)
                self._Icons["wifistatus"].Draw()
            else:
                self._Icons["wifistatus"]._IconIndex = 0
                self._Icons["wifistatus"].Draw()
                print("wifi strength error")
        else:
            if self._InAirPlaneMode == False:
                self._Icons["wifistatus"]._IconIndex = 0
            else:
                self._Icons["wifistatus"]._IconIndex = 5 ## airplane mode icon
            
            self._Icons["wifistatus"].NewCoord(start_x+self._icon_width+5,self._icon_height/2+(self._BarHeight-self._icon_height)/2)
            self._Icons["wifistatus"].Draw()
        
        self._Icons["sound"].Draw()
        
        self._Icons["battery"].Draw()
        
        pygame.draw.line(self._CanvasHWND,self._SkinManager.GiveColor("Line"),(0,self._BarHeight),(self._Width,self._BarHeight),self._BorderWidth)

        if self._HWND != None:
            self._HWND.blit(self._CanvasHWND,(self._PosX,self._PosY,self._Width,self._Height))
