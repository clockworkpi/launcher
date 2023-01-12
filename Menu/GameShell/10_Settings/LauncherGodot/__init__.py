# -*- coding: utf-8 -*-
import os
import pygame
#import math
#mport subprocess
#from beeprint import pp
from libs.roundrects import aa_round_rect

## local UI import
from UI.keys_def     import CurKeys, IsKeyStartOrA, IsKeyMenuOrB
from UI.util_funcs import ArmSystem
from UI.lang_manager import MyLangManager
from UI.confirm_page import ConfirmPage

class SwitchToLauncherGoConfirmPage(ConfirmPage):

    def KeyDown(self,event):

        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if IsKeyStartOrA(event.key):
            # TODO - we could git clone if godot-launcher  is not installed
            # TODO - check connected to internet
            #self._Screen._MsgBox.SetText("Installing LauncherGodot")
            #ArmSystem("git clone https://github.com/samdze/godot-launcher.git")
            self._Screen._MsgBox.SetText("Rebooting to LauncherGodot")
            self._Screen._MsgBox.Draw()
            self._Screen.SwapAndShow()
            pygame.time.delay(300)
            ArmSystem("sed -i s/launcher/godot-launcher/g /home/cpi/.bashrc" )
            ArmSystem("sudo reboot")


class APIOBJ(object):

    _Page = None

    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = SwitchToLauncherGoConfirmPage()
        self._Page._Screen = main_screen
        self._Page._Name ="Switch To LauncherGodot"
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
