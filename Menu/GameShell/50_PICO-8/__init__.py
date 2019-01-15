# -*- coding: utf-8 -*- 
import pygame
import validators

from UI.constants import Width,Height,ICON_TYPES
from UI.simple_name_space import SimpleNamespace
from UI.page  import Page
from UI.label  import Label
from UI.fonts  import fonts
from UI.icon_item import IconItem
from UI.icon_pool import MyIconPool
from UI.keys_def  import CurKeys
from UI.skin_manager import MySkinManager
from UI.lang_manager import MyLangManager
from UI.textarea     import Textarea

class Textbulletinboard(Textarea):
    
    def Draw(self):
        pass

class NOPICOPage(Page):
    _FootMsg =  ["Nav","","","Back",""]
    _TextColor = MySkinManager.GiveColor('Text')
    _DrawOnce = False
    

    def KeyDown(self,event):
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            if self._FootMsg[3] == "Back":
                self.ReturnToUpLevelPage()
                self._Screen.Draw()
                self._Screen.SwapAndShow()
            return   
    
    def Draw(self):
        if self._DrawOnce == False:
            self.ClearCanvas()
            
            self._DrawOnce = True    
    
class PICO8Page(Page):
    _FootMsg =  ["Nav","","","Back",""]
    _MyList = []
    
    _ListFontObj = fonts["varela13"]
    
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



class APIOBJ(object):

    _Page = None
    
    def __init__(self):
        pass
    def Init(self,main_screen):
        pass
    def API(self,main_screen):
        if main_screen !=None:
            
            main_screen._MsgBox.SetText("Starting pico-8")
            main_screen._MsgBox.Draw()
            main_screen.SwapAndShow()
            pygame.time.delay(300)
            

OBJ = APIOBJ()
def Init(main_screen):    
    OBJ.Init(main_screen)
def API(main_screen):
    OBJ.API(main_screen)
