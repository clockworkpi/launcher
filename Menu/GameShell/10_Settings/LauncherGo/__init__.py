# -*- coding: utf-8 -*- 
import os
import pygame
#import math
#mport subprocess
#from beeprint import pp
from libs.roundrects import aa_round_rect

## local UI import
from UI.util_funcs import ArmSystem
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
            ArmSystem("sed -i s/launcher/launchergo/g ~/.bashrc" )
            ArmSystem("sudo reboot")

OBJ = APIOBJ()
def Init(main_screen):    
    OBJ.Init(main_screen)
def API(main_screen):
    OBJ.API(main_screen)
