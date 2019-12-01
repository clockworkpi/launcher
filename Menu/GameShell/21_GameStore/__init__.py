# -*- coding: utf-8 -*- 
import os
import pygame
import platform
#import commands
import glob
#from beeprint import pp
from libs.roundrects import aa_round_rect

## local UI import
from UI.constants import Width,Height,ICON_TYPES,RESTARTUI
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.util_funcs import midRect,FileExists,ArmSystem
from UI.keys_def   import CurKeys, IsKeyStartOrA, IsKeyMenuOrB
from UI.scroller   import ListScroller
from UI.icon_pool  import MyIconPool
from UI.icon_item  import IconItem
from UI.multilabel import MultiLabel
from UI.skin_manager import MySkinManager
from UI.lang_manager import MyLangManager
from UI.info_page_list_item import InfoPageListItem
from UI.info_page_selector  import InfoPageSelector


import config

class RPCStack:
    def __init__(self):
        self.stack = list()

    def Push(self,data):
        if data not in self.stack:
            self.stack.append(data)
            return True
        return False

    def Pop(self):
        if len(self.stack)<=0:
            return None,False
        return self.stack.pop(),True

    def Last(self):
        idx = len(self.stack) -1
        if idx < 0:
            return None
        else:
            return self.stack[ idx ]
    
    def Length(self):
        return len(self.stack)

class GameStorePage(Page):
    _FootMsg =  ["Nav","","","Back","Select"]
    _MyList = []
    _ListFont = MyLangManager.TrFont("notosanscjk12")
    
    _AList = {}

    _Scrolled = 0
    
    _BGwidth = 320
    _BGheight = 240-24-20

    _DrawOnce = False
    _Scroller = None
    _InfoPage = None
    _Downloading = None

    def __init__(self):
        Page.__init__(self)
        self._Icons = {}
	self._MyStack = RPCStack()
	#title path type
        repos = [
        ["github.com/cuu/gamestore","https://raw.githubusercontent.com/cuu/gamestore/master/index.json","dir"]
        ]
	self._MyStack.Push(repos)

    def SyncList(self):
        
        self._MyList = []
        
        start_x  = 0
        start_y  = 0
        last_height = 0

        repos = self._MyStack.Last()

        for i,u in enumerate( repos ):            
            #print(i,u)
            li = InfoPageListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + last_height
            li._Width  = Width
            li._Fonts["normal"] = self._ListFont
            li._Active = False
            li._Value = u[1]
	    li._Type  = u[2]
            li.Init( u[0] )
            
            last_height += li._Height
            
            self._MyList.append(li)

        self._MyStack.Push(repos)
        
    def Init(self):
        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._HWND = self._Screen._CanvasHWND
                self._CanvasHWND = pygame.Surface( (self._Screen._Width,self._BGheight) )

        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height

        done = IconItem()
        done._ImgSurf = MyIconPool.GiveIconSurface("done")
        done._MyType = ICON_TYPES["STAT"]
        done._Parent = self
        self._Icons["done"] = done

        ps = InfoPageSelector()
        ps._Parent = self
        self._Ps = ps
        self._PsIndex = 0

        self.SyncList()

        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = self._Width - 10
        self._Scroller._PosY = 2
        self._Scroller.Init()
        self._Scroller.SetCanvasHWND(self._HWND)   
        
    def Click(self):
        if len(self._MyList) == 0:
            return
        
        cur_li = self._MyList[self._PsIndex]
        if cur_li._Active == True:
            return

        print(cur_li._Value)
	
	if cur_li._Type == "dir":
	    menu_file = cur_li._Value.split("master")[1]
	    local_menu_file = "%s/aria2Download%s" % (os.path.expanduser('~'),menu_file )
            if FileExists( local_menu_file ) == False:
		if config.RPC.urlDownloading(cur_li._Value) == False:
	            config.RPC.addUri(cur_li._Value, options={"out": menu_file})
		    self._Downloading = cur_li._Value
	    else:
                #read the local_menu_file, push into stack,display menu
		self._Downloading = None
		
		
	else:
	    #download the game probably
            
    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self._DrawOnce = False
        #sync  
        
    def OnReturnBackCb(self):
        pass
        """
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        """
    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if IsKeyStartOrA(event.key):
            self.Click()
            
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
        if len(self._MyList) == 0:
            return
        
        else:
            if len(self._MyList) * self._MyList[0]._Height > self._Height:
                self._Ps._Width = self._Width - 11
                self._Ps.Draw()
                for i in self._MyList:
                    if i._PosY > self._Height + self._Height/2:
                        break
                    if i._PosY < 0:
                        continue
                    i.Draw()
                self._Scroller.UpdateSize( len(self._MyList)*self._MyList[0]._Height, self._PsIndex*self._MyList[0]._Height)
                self._Scroller.Draw()
                
            else:
                self._Ps._Width = self._Width
                self._Ps.Draw()
                for i in self._MyList:
                    if i._PosY > self._Height + self._Height/2:
                        break
                    if i._PosY < 0:
                        continue
                    i.Draw()                

        if self._HWND != None:
            self._HWND.fill(MySkinManager.GiveColor("White"))
            
            self._HWND.blit(self._CanvasHWND,(self._PosX,self._PosY,self._Width, self._Height ) )

class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = GameStorePage()
        self._Page._Screen = main_screen
        self._Page._Name ="Download games"
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
    
