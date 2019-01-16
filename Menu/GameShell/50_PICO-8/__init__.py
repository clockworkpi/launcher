# -*- coding: utf-8 -*- 
import pygame
import validators

from UI.constants import Width,Height,ICON_TYPES,RUNEVT
#from UI.simple_name_space import SimpleNamespace
from UI.page  import Page
from UI.label  import Label
from UI.fonts  import fonts
from UI.icon_item import IconItem
from UI.icon_pool import MyIconPool
from UI.keys_def  import CurKeys
from UI.skin_manager import MySkinManager
from UI.lang_manager import MyLangManager
from UI.text_bulletinboard import Textbulletinboard,Text
from UI.util_funcs import FileExists


class NOPICOPage(Page):
    _FootMsg =  ["Nav","","","Back",""]
    
    def Init(self):
        self._PosX = self._Index*self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height
        
        self._CanvasHWND = self._Screen._CanvasHWND
        
        self._Board = Textbulletinboard()
        
        self._Board._PosX = 4
        self._Board._PosY = 20
        self._Board._Width= self._Width - 4*2
        self._Board._Height = 100
        self._Board._CanvasHWND = self._CanvasHWND
        self._Board.Init()
        
        a = Text("Please Go to \n",None,MyLangManager.TrFont("varela14"),True)
        b = Text("https://www.lexaloffle.com/pico-8.php",MySkinManager.GiveColor("URL"),None,True,True)
        c = Text("buy a pico-8 raspi and put zip into \n/home/cpi/games/PICO-8")
        
        d = a.Words()+b.Words()+c.Words()
        self._Board.SetAndBlitText(d)
        
    def KeyDown(self,event):
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            return   
    
    def Draw(self):
        self.ClearCanvas()
        self._Board.Draw()
  

class PICO8ZipHashErrPage(Page):
    _FootMsg =  ["Nav","","","Cancel","Continue"]
    
    def Init(self):
        self._PosX = self._Index*self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height
        
        self._CanvasHWND = self._Screen._CanvasHWND
        
        self._Board = Textbulletinboard()
        
        self._Board._PosX = 4
        self._Board._PosY = self._Height/2 - 35
        self._Board._Width= self._Width - 4*2
        self._Board._Height = 100
        self._Board._CanvasHWND = self._CanvasHWND
        self._Board._Align = "Center"
        self._Board.Init()
        
        a = Text("Md5sum check error\n",None,MyLangManager.TrFont("varela24"))
        b = Text("continue anyway?\n",None,MyLangManager.TrFont("varela24"))
        
        self._Board.SetAndBlitText(a.Words()+b.Words())
        
    def KeyDown(self,event):
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            return   
    
    def Draw(self):
        self.ClearCanvas()
        self._Board.Draw()


class APIOBJ(object):

    _Page = None
    _pico8 ="/home/cpi/games/PICO-8/pico-8"
    
    def __init__(self):
        pass
        
    def CheckPico8(self):
        if FileExists(self._pico8):
            return True
    
    def Init(self,main_screen):
        self._NOPicoPage = NOPICOPage()
        self._NOPicoPage._Name = "Not Found"
        self._NOPicoPage._Screen = main_screen
        self._NOPicoPage.Init()
        
        self._HashErrPage = PICO8ZipHashErrPage()
        self._HashErrPage._Name = "Md5sum check failed"
        self._HashErrPage._Screen = main_screen
        self._HashErrPage.Init()
                
    def API(self,main_screen):
        if main_screen !=None:
            if self.CheckPico8() == False:
                main_screen._MsgBox.SetText("Starting pico-8")
                main_screen._MsgBox.Draw()
                main_screen.SwapAndShow()
                pygame.time.delay(300)
                cmdpath = "/home/cpi/games/PICO-8/PICO-8.sh"
                pygame.event.post( pygame.event.Event(RUNEVT, message=cmdpath))
            else:
                main_screen.PushPage(self._NOPicoPage)
                #main_screen.PushPage(self._HashErrPage)
                main_screen.Draw()
                main_screen.SwapAndShow()

OBJ = APIOBJ()
def Init(main_screen):    
    OBJ.Init(main_screen)
def API(main_screen):
    OBJ.API(main_screen)
