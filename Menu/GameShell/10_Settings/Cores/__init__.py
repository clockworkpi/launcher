# -*- coding: utf-8 -*-

import os
import platform
import pygame
import glob
#import math
import  commands

#from beeprint import pp
from libs.roundrects import aa_round_rect
#import gobject
#from wicd import misc 
## local UI import
from UI.constants import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.util_funcs import midRect,FileExists,IsExecutable,ArmSystem,CmdClean
from UI.keys_def   import CurKeys, IsKeyStartOrA, IsKeyMenuOrB
from UI.scroller   import ListScroller
from UI.icon_pool  import MyIconPool
from UI.icon_item  import IconItem
from UI.confirm_page import ConfirmPage
from UI.multi_icon_item import MultiIconItem
from UI.lang_manager  import MyLangManager
from UI.multilabel import MultiLabel
from UI.info_page_list_item import InfoPageListItem
from UI.info_page_selector  import InfoPageSelector
from UI.skin_manager import MySkinManager


class DeleteCoreConfirmPage(ConfirmPage):
    
    _ConfirmText = MyLangManager.Tr("Awaiting Input")
    _FootMsg = ["Nav","","","Cancel","OK"]
    CallbackA = None
    
    def KeyDown(self,event):
        
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if IsKeyStartOrA(event.key):
            self._Screen._MsgBox.SetText("Applying")
            self._Screen._MsgBox.Draw()
            self._Screen.SwapAndShow()
            
            pygame.time.delay(638)
            
            self.CallbackA()
            
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
    
class CoresPage(Page):
    _FootMsg =  ["Nav","Del","Scan","Back",""]
    _MyList = []
    _ListFontObj = MyLangManager.TrFont("varela13")
    
    _AList = {}

    _Scrolled = 0
    
    _BGwidth = 320
    _BGheight = 240-24-20

    _DrawOnce = False
    _Scroller = None

    _EasingDur = 30
    
    _CORES_PATH = "%s/apps/emulators" % os.path.expanduser('~') 

    _Config =None
    _AllowedExts = [".so",".bin"]
    _HiddenSos   = ["chailove_libretro.so","nxengine_libretro.so"]
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}
        
        if "arm" in platform.machine():
            pass
        
    def GenList(self):

        self._MyList = []
        ## map ini to self._AList
        files_path = glob.glob(self._CORES_PATH+"/*")
        
        start_x  = 10
        start_y  = 0
        counter = 0 
        for i,v in enumerate( files_path):
            if os.path.basename(v) in self._HiddenSos:
                continue
            
            filename, file_extension = os.path.splitext(v)

            alias_file = filename+file_extension + ".alias"
            
            if file_extension in self._AllowedExts:
                li = InfoPageListItem()
                li._Parent = self
                li._PosX   = start_x
                li._PosY   = start_y + counter*InfoPageListItem._Height
                li._Width  = Width-10
                li._Fonts["normal"] = self._ListFontObj
                li._Fonts["small"] = MySkinManager.GiveFont("varela12")
                li._ReadOnly = True
                
                if os.path.isfile(alias_file):
                    fp = open(alias_file, "r")
                    alias = fp.read()
                    alias = alias.strip()
                    label_text = alias.decode("utf8")
                    li.Init( label_text )
                    fp.close()
                else:
                    li.Init( os.path.basename(v) )
                li._Flag = v
                ##li.SetSmallText( v )
                
                self._MyList.append(li)
                counter += 1
    
    def Init(self):
        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._CanvasHWND = self._Screen._CanvasHWND

        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height

        ps = InfoPageSelector()
        ps._PosX = 11
        ps._Parent = self
        ps._Width = self._Width-10
        self._Ps = ps
        self._PsIndex = 0

        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = 2
        self._Scroller._PosY = 2
        self._Scroller.Init()
        
        self._ConfirmBox = DeleteCoreConfirmPage()
        self._ConfirmBox._Screen = self._Screen
        self._ConfirmBox._Name = "Confirm to Delete?"
        self._ConfirmBox._Parent = self
        self._ConfirmBox.Init()
        
    def ReScan(self):
        self.GenList()
        self.RefreshPsIndex()
      
    def ConfirmBoxCallbackA(self):
        if len(self._MyList) == 0:
            return
            
        cur_li = self._MyList[self._PsIndex]
        
        os.system("rm %s" % CmdClean(cur_li._Flag))
        self.GenList()
        self.RefreshPsIndex()
        
    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self._DrawOnce = False    
        self.GenList()
    
    def OnReturnBackCb(self):
        pass
        
    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
        if event.key == CurKeys["X"]: #Scan current
           self.ReScan() 
           self._Screen.Draw()
           self._Screen.SwapAndShow()
                       
        if event.key == CurKeys["Y"]: #del
            if len(self._MyList) == 0:
                return
            
            self._ConfirmBox.CallbackA = self.ConfirmBoxCallbackA
            
            self._Screen.PushPage(self._ConfirmBox)
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

 

    def Draw(self):
        self.ClearCanvas()

        if len(self._MyList) > 0:
            self._Ps.Draw()
            for i in self._MyList:
                i.Draw()
        
            self._Scroller.UpdateSize( len(self._MyList)*InfoPageListItem._Height,
                                   self._PsIndex*InfoPageListItem._Height) 
            self._Scroller.Draw()
        
        


class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = CoresPage()
        self._Page._Screen = main_screen
        self._Page._Name ="Retroarch cores manager"
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
    
        
