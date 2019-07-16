# -*- coding: utf-8 -*- 
import os
import pygame
#import math
#mport subprocess
import platform
#from beeprint import pp
from libs.roundrects import aa_round_rect

## local UI import
from UI.lang_manager import MyLangManager

class APIOBJ(object):

    _Page = None
    
    def __init__(self):
        pass
    def Init(self,main_screen):
        pass
    def API(self,main_screen):
        if main_screen !=None:
            main_screen._MsgBox.SetText("Rebooting to LauncherGo")
            main_screen._MsgBox.Draw()
            main_screen.SwapAndShow()
            pygame.time.delay(300)
            if "arm" in platform.machine():
                os.system("sed -i s/launcher/launchergo/g ~/.bashrc" )
                os.system("sudo reboot")

OBJ = APIOBJ()
def Init(main_screen):    
    OBJ.Init(main_screen)
def API(main_screen):
    OBJ.API(main_screen)
