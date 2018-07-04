# -*- coding: utf-8 -*- 

import pygame
#import math
#mport subprocess

#from beeprint import pp
from libs.roundrects import aa_round_rect
#import gobject
#from wicd import misc 
## local UI import
from UI.constants import Width,Height,ICON_TYPES,POWEROPT
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.fonts  import fonts
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys
from UI.scroller   import ListScroller
from UI.icon_pool  import MyIconPool
from UI.icon_item  import IconItem
from UI.multilabel import MultiLabel

import config

class ListPageSelector(PageSelector):
    _BackgroundColor = pygame.Color(131,199,219)

    def __init__(self):
        self._PosX = 0
        self._PosY = 0
        self._Height = 0
        self._Width  = Width

    def AnimateDraw(self,x2,y2):
        pass

    def Draw(self):
        idx = self._Parent._PsIndex
        
        if idx < len(self._Parent._MyList):
            x = self._Parent._MyList[idx]._PosX+2
            y = self._Parent._MyList[idx]._PosY+1
            h = self._Parent._MyList[idx]._Height -3
        
            self._PosX = x
            self._PosY = y
            self._Height = h
            
            aa_round_rect(self._Parent._CanvasHWND,  
                          (x,y,self._Width-4,h),self._BackgroundColor,4,0,self._BackgroundColor)


class PageListItem(object):
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
    
    def __init__(self):
        self._Labels = {}
        self._Icons  = {}
        self._Fonts  = {}

    def SetSmallText(self,text):
        
        l = Label()
        l._PosX = 40
        l.SetCanvasHWND(self._Parent._CanvasHWND)
        l.Init(text,self._Fonts["small"])
        self._Labels["Small"] = l
    
    def Init(self,text):

        l = Label()
        l._PosX = 10
        l.SetCanvasHWND(self._Parent._CanvasHWND)

        l.Init(text,self._Fonts["normal"])
        self._Labels["Text"] = l
        
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
        
        pygame.draw.line(self._Parent._CanvasHWND,(169,169,169),(self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)        
    

class InfoPage(Page):
    _FootMsg =  ["Nav.","","","Back",""]
    _MyList = []
    _ListFontObj = fonts["varela15"]    
    _AList = {}

    _Time1 = 40
    _Time2 = 120
    _Time3 = 300

    def ConvertSecToMin(self, secs):
        sec_str = ""
        min_str = ""
        if secs > 60:
            m = int(secs/60)
            s = secs % 60
            if m > 1:
                min_str =  "%d minutes " % m
            else:
                min_str =  "%d minute " % m
            
            if s == 1:
                sec_str = "%d second" % s
            elif s > 1:
                sec_str = "%d seconds" % s
        elif secs > 0:
            if secs > 1:
                sec_str = "%d seconds" % secs
            else:
                sec_str = "%d second" % secs
        
        elif secs == 0:
            sec_str = "Never"
        
        return min_str + sec_str

    def RefreshList(self):
        ## after GenList ,reuse
        self._AList["time1"]["value"] = self.ConvertSecToMin(self._Time1)
        self._AList["time2"]["value"] = self.ConvertSecToMin(self._Time2)
        self._AList["time3"]["value"] = self.ConvertSecToMin(self._Time3)

        for i,v in enumerate( self._AList ):
            self._MyList[i].SetSmallText(  self._AList[v]["value"] )
        
    def GenList(self):

        time1 = {}
        time1["key"] = "time1"
        if self._Time1 == 0:
            time1["value"] = "Never"
        else:
            time1["value"] = "%d secs" % self._Time1
        time1["label"] = "Screen dimming"
        
        time2 = {}
        time2["key"] = "time2"
        if self._Time2 == 0:
            time2["value"] = "Never"
        else:
            time2["value"] = "%d secs" % self._Time2
            
        time2["label"] = "Screen OFF"

        time3 = {}
        time3["key"] = "time3"
        
        if self._Time3 == 0:
            time3["value"] = "Never"
        else:
            time3["value"] = "%d secs" % self._Time3
        time3["label"] = "Power OFF"
        
        self._AList["time1"] = time1
        self._AList["time2"] = time2
        self._AList["time3"] = time3
        
        self._MyList = []
        
        start_x  = 0
        start_y  = 0
        
        for i,v in enumerate( self._AList):
            print(v)
            li = PageListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + i*PageListItem._Height
            li._Width  = Width
            li._Fonts["normal"] = self._ListFontObj
            li._Fonts["small"] = fonts["varela12"]
            
            if self._AList[v]["label"] != "":
                li.Init(  self._AList[v]["label"] )
            else:
                li.Init( self._AList[v]["key"] )

            li._Flag = self._AList[v]["key"]

            li.SetSmallText( self._AList[v]["value"] )
            
            self._MyList.append(li)
            
    def Init(self):
        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._CanvasHWND = self._Screen._CanvasHWND

        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height

        ps = ListPageSelector()
        ps._Parent = self
        self._Ps = ps
        self._PsIndex = 0
        
        self.GenList()

        
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

    def Click(self):
        cur_li = self._MyList[self._PsIndex]
        print(cur_li._Flag)        

        
    def OnLoadCb(self):
        self.RefreshList()

    def OnReturnBackCb(self):
        pass
        """
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        """
    
    def KeyDown(self,event):
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            self.ReturnToUpLevelPage()
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

        for i in self._MyList:
            i.Draw()

class PowerOptionsPage(Page):
    _FootMsg =  ["Nav.","","Detail","Back","Select"]
    _MyList = []
    _ListFont = fonts["notosanscjk15"]
    
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

        
        supersaving = {}
        supersaving["key"] = "super"
        supersaving["label"] = "Power saving"
        supersaving["value"] = "supersaving"

        powersaving = {}
        powersaving["key"] = "saving"
        powersaving["label"] = "Balanced"
        powersaving["value"] = "powersaving"

        balance_saving = {}
        balance_saving["key"] = "balance"
        balance_saving["label"] = "Performance"
        balance_saving["value"] = "balance_saving"
        
        
        self._AList["supersaving"] = supersaving
        self._AList["powersaving"] = powersaving
        self._AList["balance_saving"] = balance_saving
        
        for i,u in enumerate( ["supersaving","powersaving","balance_saving"] ):
            if u not in self._AList:
                continue
            
            v = self._AList[u]
            
            li = PageListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + last_height
            li._Width  = Width
            li._Fonts["normal"] = self._ListFont
            li._Active = False
            li._Value = self._AList[u]["value"]
            
            if self._AList[u]["label"] != "":
                li.Init(  self._AList[u]["label"] )
            else:
                li.Init( self._AList[u]["key"] )
            
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
        done._ImgSurf = MyIconPool._Icons["done"]
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

        self._InfoPage = InfoPage()
        self._InfoPage._Screen = self._Screen
        self._InfoPage._Name   = "Power option detail"
        self._InfoPage.Init()
        
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
        if cur_li._Active == True:
            return
        
        for i in self._MyList:
            i._Active = False

        cur_li._Active = True
        print(cur_li._Value)
        with open(".powerlevel","w") as f:
            f.write(cur_li._Value)

        config.PowerLevel = cur_li._Value

        self._Screen._MsgBox.SetText("Applying...")
        self._Screen._MsgBox.Draw()
        self._Screen.SwapAndShow()

        pygame.event.post( pygame.event.Event(POWEROPT, message=""))
        
        pygame.time.delay(1000)
        
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self._DrawOnce = False
        with open(".powerlevel", "r") as f:
            powerlevel = f.read()

        powerlevel = powerlevel.strip()

        if powerlevel == "":
            powerlevel = "balance_saving"

        for i in self._MyList:
            if i._Value == powerlevel:
                i._Active = True
        
    def OnReturnBackCb(self):
        pass
        """
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        """
    def KeyDown(self,event):
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["B"]:
            self.Click()
            
        if event.key == CurKeys["Up"]:
            self.ScrollUp()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        if event.key == CurKeys["Down"]:
            self.ScrollDown()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["Y"]:
            cur_li = self._MyList[self._PsIndex]
            time1 = config.PowerLevels[cur_li._Value][0]
            time2 = config.PowerLevels[cur_li._Value][1]
            time3 = config.PowerLevels[cur_li._Value][2]
            
            self._InfoPage._Time1 = time1
            self._InfoPage._Time2 = time2
            self._InfoPage._Time3 = time3
            
            self._Screen.PushPage(self._InfoPage)
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
            self._HWND.fill((255,255,255))
            
            self._HWND.blit(self._CanvasHWND,(self._PosX,self._PosY,self._Width, self._Height ) )
            
        
        


class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = PowerOptionsPage()
        self._Page._Screen = main_screen
        self._Page._Name ="Power Options"
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
    
        
