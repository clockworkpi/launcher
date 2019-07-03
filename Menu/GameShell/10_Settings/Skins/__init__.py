# -*- coding: utf-8 -*- 
import os
import pygame
#import commands
import glob
#from beeprint import pp
from libs.roundrects import aa_round_rect

## local UI import
from UI.constants import Width,Height,ICON_TYPES,RESTARTUI
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.util_funcs import midRect,FileExists
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

class ListPageSelector(InfoPageSelector):
    def Draw(self):
        idx = self._Parent._PsIndex
        
        if idx < len(self._Parent._MyList):
            x = self._Parent._MyList[idx]._PosX+2 ## ++
            y = self._Parent._MyList[idx]._PosY+1
            h = self._Parent._MyList[idx]._Height -3
        
            self._PosX = x
            self._PosY = y
            self._Height = h
            
            aa_round_rect(self._Parent._CanvasHWND,  
                          (x,y,self._Width-4,h),self._BackgroundColor,4,0,self._BackgroundColor)


class PageListItem(InfoPageListItem):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 30

    _Labels = {}
    _Icons  = {}
    _Fonts  = {}

    _LinkObj = None

    _Active  = False
    _Value = ""
    
    def Draw(self):
        
        self._Labels["Text"]._PosY = self._PosY+ (self._Height-  self._Labels["Text"]._Height)/2
        
        if self._Active == True:
            self._Parent._Icons["done"].NewCoord( self._Parent._Width-30,self._PosY+5)
            self._Parent._Icons["done"].Draw()
            
        self._Labels["Text"].Draw(self._Active)
            
        if "Small" in self._Labels:
            self._Labels["Small"]._PosX = self._Width - self._Labels["Small"]._Width -10
            self._Labels["Small"]._PosY = self._PosY + (self._Height-  self._Labels["Small"]._Height)/2
            self._Labels["Small"].Draw()
        
        pygame.draw.line(self._Parent._CanvasHWND,MySkinManager.GiveColor('Line'),(self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)        
    
class SkinsPage(Page):
    _FootMsg =  ["Nav","","Scan","Back","Select"]
    _MyList = []
    _ListFont = MyLangManager.TrFont("notosanscjk15")
    
    _AList = {}

    _Scrolled = 0
    
    _BGwidth = 320
    _BGheight = 240-24-20

    _DrawOnce = False
    _Scroller = None
    _InfoPage = None
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}

    def GenList(self):
        self._MyList = []
        
        start_x  = 0
        start_y  = 0
        last_height = 0


        skins = [["../skin/default","Default"]]
        files_path = glob.glob("/home/cpi/skins/*")
        
        for i ,v in enumerate(files_path):
            if os.path.isdir(v):
                bname = os.path.basename(v)
                print(v,bname)
                skins.append([v,bname])
        
        for i,u in enumerate( skins ):            
            #print(i,u)
            li = PageListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + last_height
            li._Width  = Width
            li._Fonts["normal"] = self._ListFont
            li._Active = False
            li._Value = u[0]
            li.Init( u[1] )
            
            last_height += li._Height
            
            self._MyList.append(li)
            
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

        ps = ListPageSelector()
        ps._Parent = self
        self._Ps = ps
        self._PsIndex = 0

        self.GenList()

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
        
        for i in self._MyList:
            i._Active = False
            
        cur_li._Active = True
        self._Screen._MsgBox.SetText("Applying")
        self._Screen._MsgBox.Draw()
        self._Screen.SwapAndShow()
            
        if "../skin/default" in cur_li._Value:
            os.system("rm %s/.gameshell_skin" % os.path.expanduser('~') )
        else:
            os.system("echo %s > %s/.gameshell_skin" % (cur_li._Value,os.path.expanduser('~') ))
        
        pygame.time.delay(700)
        pygame.event.post( pygame.event.Event(RESTARTUI, message=""))
        
    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self._DrawOnce = False
                        
        for i in self._MyList:
            i._Active = False
        
        for i in self._MyList:
            if config.SKIN in i._Value:
                i._Active = True
        
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
        
        if event.key == CurKeys["X"]:
            self.GenList()
            
            for i in self._MyList:
                i._Active = False
        
            for i in self._MyList:
                if config.SKIN in i._Value:
                    i._Active = True
                
            self._Screen.Draw()
            self._Screen.SwapAndShow()            
    
    def Draw(self):

        self.ClearCanvas()
        if len(self._MyList) == 0:
            return
        
        else:
            if len(self._MyList) * PageListItem._Height > self._Height:
                self._Ps._Width = self._Width - 11
                self._Ps.Draw()
                for i in self._MyList:
                    if i._PosY > self._Height + self._Height/2:
                        break
                    if i._PosY < 0:
                        continue
                    i.Draw()
                self._Scroller.UpdateSize( len(self._MyList)*PageListItem._Height, self._PsIndex*PageListItem._Height)
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
        self._Page = SkinsPage()
        self._Page._Screen = main_screen
        self._Page._Name ="Skin selection"
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
    
        
