# -*- coding: utf-8 -*- 
import os
import pygame

from libs.roundrects import aa_round_rect

## local UI import
from UI.constants import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.fonts  import fonts
from UI.icon_item import IconItem
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys
from UI.multi_icon_item import MultiIconItem
from UI.icon_pool           import MyIconPool
from UI.scroller   import ListScroller

from list_item  import ListItem


import myvars


class MusicLibStack:
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
            return "/"
        else:
            return self.stack[ idx ]
    
    def Length(self):
        return len(self.stack)

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



class MusicLibListPage(Page):

    _Icons = {}
    _Selector=None
    _FootMsg = ["Nav","Scan","","Back","Add to Playlist"]
    _MyList = []
    _SwapMyList = []
    _ListFont = fonts["notosanscjk15"]
    _MyStack = None

    _Scroller = None
    
    _BGpng = None
    _BGwidth = 56
    _BGheight = 70
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}
        self._CanvasHWND = None
        self._MyList = []
        self._SwapMyList = []
        self._MyStack = MusicLibStack()
        
    def SyncList(self,path):
        if myvars.Poller == None:
            return
        
        alist = myvars.Poller.listfiles(path)
        if alist == False:
            print("listfiles return false")
            return 

        self._MyList = []
        self._SwapMyList = []
        
        start_x  = 0
        start_y  = 0
        hasparent = 0
        if self._MyStack.Length() > 0:
            hasparent = 1
            li = ListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y
            li._Width  = Width
            li._Fonts["normal"] = self._ListFont
            li._MyType = ICON_TYPES["DIR"]
            li._Parent = self
            li.Init("[..]")
            self._MyList.append(li)
        
        for i,v in enumerate(sorted(alist)):
            li = ListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + (i+hasparent)*ListItem._Height
            li._Width  = Width
            li._Fonts["normal"] = self._ListFont
            li._MyType  = ICON_TYPES["FILE"]
            li._Parent  = self
            
            if "directory" in v:
                li._MyType = ICON_TYPES["DIR"]
                dir_base_name = os.path.basename(v["directory"])
                li.Init(  dir_base_name )
                li._Path = v["directory"] 
            elif "file" in v:
                bname = os.path.basename(v["file"])
                li.Init( bname  )
                li._Path = v["file"]
                
            else:
                li.Init("NoName")
            
            self._MyList.append(li)

        for i in self._MyList:
            self._SwapMyList.append(i)
        
    def Init(self):
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height

        self._CanvasHWND = self._Screen._CanvasHWND

        ps = ListPageSelector()
        ps._Parent = self
        self._Ps = ps
        self._PsIndex = 0

        self.SyncList("/")

        icon_for_list = MultiIconItem()
        icon_for_list._ImgSurf = MyIconPool._Icons["sys"]
        icon_for_list._MyType = ICON_TYPES["STAT"]
        icon_for_list._Parent = self
        
        icon_for_list.Adjust(0,0,18,18,0)        
        self._Icons["sys"] = icon_for_list


        self._BGpng = IconItem()
        self._BGpng._ImgSurf = MyIconPool._Icons["empty"]
        self._BGpng._MyType = ICON_TYPES["STAT"]
        self._BGpng._Parent = self
        self._BGpng.AddLabel("Please upload data over Wi-Fi", fonts["varela22"])
        self._BGpng.SetLableColor(pygame.Color(204,204,204))
        self._BGpng.Adjust(0,0,self._BGwidth,self._BGheight,0)


        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = self._Width - 10
        self._Scroller._PosY = 2
        self._Scroller.Init()
        

    def ScrollUp(self,Step=1):
        if len(self._MyList) == 0:
            return
        tmp = self._PsIndex
        self._PsIndex -= Step
        
        if self._PsIndex < 0:
            self._PsIndex = 0
        dy = tmp-self._PsIndex 
        cur_li = self._MyList[self._PsIndex]
        if cur_li._PosY < 0:
            for i in range(0, len(self._MyList)):
                self._MyList[i]._PosY += self._MyList[i]._Height*dy
        

    def ScrollDown(self,Step=1):
        if len(self._MyList) == 0:
            return
        tmp = self._PsIndex
        self._PsIndex +=Step
        if self._PsIndex >= len(self._MyList):
            self._PsIndex = len(self._MyList) -1
        dy = self._PsIndex - tmp
        cur_li = self._MyList[self._PsIndex]
        if cur_li._PosY +cur_li._Height > self._Height:
            for i in range(0,len(self._MyList)):
                self._MyList[i]._PosY -= self._MyList[i]._Height*dy

    def Click(self):
        if len(self._MyList) == 0:
            return
        
        cur_li = self._MyList[self._PsIndex]

        if cur_li._MyType == ICON_TYPES["DIR"]:
            if cur_li._Path == "[..]":
                self._MyStack.Pop()
                self.SyncList( self._MyStack.Last() )
                self._PsIndex = 0
            else:
                self._MyStack.Push( self._MyList[self._PsIndex]._Path )
                self.SyncList( self._MyStack.Last() )
                self._PsIndex = 0
                
        if cur_li._MyType == ICON_TYPES["FILE"]: ## add to playlist only
            myvars.Poller.addfile(cur_li._Path)
            myvars.PlayListPage.SyncList()            
            print("add" , cur_li._Path)
            
        self._Screen.Draw()
        self._Screen.SwapAndShow()

    def Rescan(self):
        self.SyncList("/")
        self._PsIndex = 0
        
    def KeyDown(self,event):
        
        if event.key == CurKeys["Menu"] or event.key == CurKeys["Left"] or event.key == CurKeys["A"]:
            
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
        
        """
        if event.key == CurKeys["Right"]:
            self.ScrollDown(Step=5)
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
        if event.key == CurKeys["Left"]:
            self.ScrollUp(Step=5)
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        """
        
        if event.key == CurKeys["X"]:
            self.Rescan()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
                                     
        if event.key == CurKeys["Enter"]:
            self.Click()
            
    def Draw(self):
        self.ClearCanvas()


        """
        start_x = 0
        start_y = 0
        counter = 0
        
        self._MyList = []
        
        for i,v in enumerate(self._SwapMyList):
            if myvars.PlayListPage.InPlayList(v._Path):
                v._Active = True
            else:
                v._Active = False

            if v._Active == False:
                v.NewCoord(start_x, start_y+counter* ListItem._Height)
                counter+=1
                self._MyList.append(v)
        """

        if len(self._MyList) == 0:
            self._BGpng.NewCoord(self._Width/2,self._Height/2)
            self._BGpng.Draw()
            return
        
        else:
            if len(self._MyList) * ListItem._Height > self._Height:
                self._Ps._Width = self._Width - 11
            
                self._Ps.Draw()
                for i in self._MyList:
                    if myvars.PlayListPage.InPlayList(i._Path):
                        i._Active = True
                    else:
                        i._Active = False

                    if i._PosY > self._Height + self._Height/2:
                        break

                    if i._PosY < 0:
                        continue
                    
                    i.Draw()
                    
                self._Scroller.UpdateSize( len(self._MyList)*ListItem._Height, self._PsIndex*ListItem._Height)
                self._Scroller.Draw()
            else:
                self._Ps._Width = self._Width
                self._Ps.Draw()
                for i in self._MyList:
                    if myvars.PlayListPage.InPlayList(i._Path):
                        i._Active = True
                    else:
                        i._Active = False

                    if i._PosY > self._Height + self._Height/2:
                        break

                    if i._PosY < 0:
                        continue
                        
                    i.Draw()    
