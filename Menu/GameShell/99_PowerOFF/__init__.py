# -*- coding: utf-8 -*- 

import pygame

#UI lib
from UI.constants    import RUNSYS
from UI.keys_def     import CurKeys, IsKeyStartOrA, IsKeyMenuOrB
from UI.confirm_page import ConfirmPage
from UI.lang_manager import MyLangManager
from UI.skin_manager import MySkinManager

import config

class PowerOffConfirmPage(ConfirmPage):
    
    _ConfirmText = MyLangManager.Tr("Awaiting Input")
    _FootMsg = ["Nav","","Reboot","Cancel","Shutdown"]

    def CheckBattery(self):
        try:
            f = open(config.Battery)
        except IOError:
            print( "PowerOFF open %s failed" % config.Battery)
            return 0
        else:
            with f:
                bat_uevent = {}
                content = f.readlines()
                content = [x.strip() for x in content]
                for i in content:
                    pis = i.split("=")
                    if len(pis) > 1:
                        bat_uevent[pis[0]] = pis[1]

                if "POWER_SUPPLY_CAPACITY" in bat_uevent:
                    cur_cap = int(bat_uevent["POWER_SUPPLY_CAPACITY"])
                else:
                    cur_cap = 0
                
                return cur_cap
                    
        return 0
        
    def KeyDown(self,event):
        
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if IsKeyStartOrA(event.key):
            if self.CheckBattery() < 20:
                cmdpath = "feh --bg-center %s;" % MySkinManager.GiveWallpaper("gameover.png")
            else:
                cmdpath = "feh --bg-center %s;" % MySkinManager.GiveWallpaper("seeyou.png")
            
            cmdpath += "sleep 3;"
            
            #cmdpath += "echo 'halt -p' > /tmp/halt_cmd"
            
            cmdpath += "sudo halt -p"
            pygame.event.post( pygame.event.Event(RUNSYS, message=cmdpath))
            
        if event.key == CurKeys["X"]:
            cmdpath = "feh --bg-center %s;" % MySkinManager.GiveWallpaper("seeyou.png")
            cmdpath += "sleep 3;"
            cmdpath += "sudo reboot"
            pygame.event.post( pygame.event.Event(RUNSYS, message=cmdpath))


class APIOBJ(object):

    _StoragePage = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = PowerOffConfirmPage()

        self._Page._Screen = main_screen
        self._Page._Name ="Power OFF"
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
    
