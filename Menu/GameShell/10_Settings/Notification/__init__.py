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
from UI.util_funcs import midRect,FileExists,IsExecutable
from UI.keys_def   import CurKeys, IsKeyStartOrA, IsKeyMenuOrB
from UI.scroller   import ListScroller
from UI.icon_pool  import MyIconPool
from UI.icon_item  import IconItem
from UI.multi_icon_item import MultiIconItem
from UI.lang_manager  import MyLangManager
from UI.multilabel import MultiLabel
from UI.info_page_list_item import InfoPageListItem
from UI.info_page_selector  import InfoPageSelector
from UI.skin_manager import MySkinManager

class NotifyJobListItem(InfoPageListItem):
    
    _CanvasHWND = None
    
    def Init(self,text):

        #self._Fonts["normal"] = fonts["veramono12"]
        self._CanvasHWND = self._Parent._CanvasHWND
        
        l = Label()
        l._PosX = 10
        l.SetCanvasHWND(self._Parent._CanvasHWND)

        l.Init(text,self._Fonts["normal"])
        self._Labels["Text"] = l    
        
        done_icon = IconItem()
        done_icon._ImgSurf = MyIconPool.GiveIconSurface("done")
        done_icon._CanvasHWND = self._Parent._CanvasHWND
        done_icon._Parent = self
        
        self._Icons["done"] = done_icon
    
    def Draw(self):
        if self._ReadOnly == False:
            self._Labels["Text"].SetColor(MySkinManager.GiveColor("ReadOnlyText"))
        else:
            self._Labels["Text"].SetColor(MySkinManager.GiveColor("Text"))

        
        self._Labels["Text"]._PosX = self._Labels["Text"]._PosX + self._PosX
        self._Labels["Text"]._PosY = self._PosY + (self._Height - self._Labels["Text"]._Height)/2
        self._Labels["Text"].Draw()
        self._Labels["Text"]._PosX = self._Labels["Text"]._PosX - self._PosX

        if "Small" in self._Labels:
            self._Labels["Small"]._PosX = self._Width - self._Labels["Small"]._Width-5
            
            self._Labels["Small"]._PosY = self._PosY + (self._Height - self._Labels["Small"]._Height)/2
            self._Labels["Small"].Draw()
        
        if self._ReadOnly:
            self._Icons["done"].NewCoord(self._Width - 25,5)
            self._Icons["done"].Draw()
        
        pygame.draw.line(self._Parent._CanvasHWND,MySkinManager.GiveColor('Line'),(self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)    
    
    
class NotificationPage(Page):
    _FootMsg =  ["Nav","","","Back","Toggle"]
    _MyList = []
    _ListFontObj = MyLangManager.TrFont("varela13")
    
    _AList = {}

    _Scrolled = 0
    
    _BGwidth = 320
    _BGheight = 240-24-20

    _DrawOnce = False
    _Scroller = None

    _EasingDur = 30
    
    _GSNOTIFY_JOBS = "gsnotify/Jobs"
    _GSNOTIFY_SOCKET="/tmp/gsnotify.sock"
    _Config =None
    _AllowedExts = [".sh",".lsp",".lua",".bin",".py",".js"]
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}
        
        if "arm" in platform.machine():
            os.system( "git config --global core.filemode false" )
        
    def GenList(self):

        self._MyList = []
        ## map ini to self._AList
        files_path = glob.glob(self._GSNOTIFY_JOBS+"/*")
        
                
        start_x  = 10
        start_y  = 0
        counter = 0 
        for i,v in enumerate( files_path):
            filename, file_extension = os.path.splitext(v)
            alias_file = filename + ".alias"
            
            if file_extension in self._AllowedExts:
                li = NotifyJobListItem()
                li._Parent = self
                li._PosX   = start_x
                li._PosY   = start_y + counter*InfoPageListItem._Height
                li._Width  = Width-10
                li._Fonts["normal"] = self._ListFontObj
                li._Fonts["small"] = MySkinManager.GiveFont("varela12")
                
                if IsExecutable(v):
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
        
    def Click(self):
        if len(self._MyList) == 0:
            return
        
        cur_li = self._MyList[self._PsIndex]
        #print("Click ",cur_li._Flag)
        if IsExecutable(cur_li._Flag):
            os.system("chmod -x "+cur_li._Flag)
        else:
            os.system("chmod +x "+cur_li._Flag)
        
        self.GenList()
        
        
    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self._DrawOnce = False    
        self.GenList()
    
    def OnReturnBackCb(self):
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
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
            
            self.Click()
            
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
        self._Ps.Draw()

        if len(self._MyList) > 0:
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
        self._Page = NotificationPage()
        self._Page._Screen = main_screen
        self._Page._Name ="Notify"
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
    
        
