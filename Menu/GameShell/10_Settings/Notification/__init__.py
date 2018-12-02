# -*- coding: utf-8 -*-

import ConfigParser
import socket

import pygame
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
from UI.fonts  import fonts
from UI.util_funcs import midRect,FileExists
from UI.keys_def   import CurKeys
from UI.scroller   import ListScroller
from UI.icon_pool  import MyIconPool
from UI.icon_item  import IconItem
from UI.multi_icon_item import MultiIconItem
from UI.lang_manager  import MyLangManager
from UI.multilabel import MultiLabel
from UI.info_page_list_item import InfoPageListItem
from UI.info_page_selector  import InfoPageSelector


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

    _GSNOTIFY_CFG="gsnotify/gsnotify.cfg"
    _GSNOTIFY_SOCKET="/tmp/gsnotify.sock"
    _Config =None
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}

    def ReadConfig(self,fname):
        if FileExists(fname):
            if self._Config == None:
                self._Config = ConfigParser.ConfigParser()
                self._Config.optionxform = str
            
            self._Config.read(fname)
        else:
            print(fname, "not found")
        
    def GenList(self):
        if self._Config == None:
            return

        self._AList = {}
        self._MyList = []
        ## map ini to self._AList
        for i,v in enumerate(self._Config.items("Settings")):
            self._AList[v[0]] = v[1]  ## {'BGCOLOR': '#eab934', 'Enabled': 'False',...}

                
        start_x  = 10
        start_y  = 0
        
        for i,v in enumerate( self._AList):
            li = InfoPageListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + i*InfoPageListItem._Height
            li._Width  = Width-10
            li._Fonts["normal"] = self._ListFontObj
            li._Fonts["small"] = fonts["varela12"]
            
            li.Init( v )
            li._Flag = v
            li.SetSmallText( self._AList[v] )
            if v != "Enabled":
                li._ReadOnly=True
                
            self._MyList.append(li)
    
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

        self.ReadConfig(self._GSNOTIFY_CFG)
        
        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = 2
        self._Scroller._PosY = 2
        self._Scroller.Init()
        
    def ScrollDown(self):
        if len(self._MyList) == 0:
            return
        self._PsIndex +=1
        if self._PsIndex >= len(self._MyList):
            self._PsIndex = len(self._MyList) -1

        cur_li = self._MyList[self._PsIndex]
        if cur_li._PosY +cur_li._Height > self._Height:
            for i in range(0,len(self._MyList)):
                self._MyList[i]._PosY -= self._MyList[i]._Height
        
    def ScrollUp(self):
        if len(self._MyList) == 0:
            return
        self._PsIndex -= 1
        if self._PsIndex < 0:
            self._PsIndex = 0
        cur_li = self._MyList[self._PsIndex]
        if cur_li._PosY < 0:
            for i in range(0, len(self._MyList)):
                self._MyList[i]._PosY += self._MyList[i]._Height

    def Click(self):
        if len(self._MyList) == 0:
            return
        
        cur_li = self._MyList[self._PsIndex]
        print("Click ",cur_li._Flag)

    def SendMsgToUnixSocket(self,msg):
        if FileExists(self._GSNOTIFY_SOCKET) == False:
            print(self._GSNOTIFY_SOCKET," not existed")
            return

        try:
	    s = socket.socket(socket.AF_UNIX)
	    s.settimeout(1) # 1 second timeout
	    s.connect(self._GSNOTIFY_SOCKET)
	    s.send(msg)
            data = s.recv(1024)
            print("received: {}".format(data))
	    s.close()
        except Exception as err:
            print(err) ## print error ,but ignore it 
        
        
    def ToggleEnable(self):
        print("ToggleEnable")
        if self._Config == None:
            return

        e = self._Config.get("Settings","Enabled")
        
        if e == "False":
            self.SendMsgToUnixSocket("Enable")
        else:
            self.SendMsgToUnixSocket("Disable")

        
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
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["B"]:
            self.ToggleEnable()
            self._Screen._MsgBox.SetText("Applying")
            self._Screen._MsgBox.Draw()
            self._Screen.SwapAndShow()
            pygame.time.delay(1000)
            self.ReadConfig(self._GSNOTIFY_CFG)
            self.GenList()
            
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
    
        
