# -*- coding: utf-8 -*- 

import os
import pygame

import glob
import shutil
import gobject
import validators
#from pySmartDL import SmartDL


from libs.roundrects import aa_round_rect

## local UI import
from UI.constants import Width,Height,ICON_TYPES,RUNEVT
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.icon_item import IconItem
from UI.fonts  import fonts
from UI.util_funcs import midRect,CmdClean,FileExists
from UI.keys_def   import CurKeys
from UI.multi_icon_item import MultiIconItem
from UI.icon_pool  import MyIconPool
from UI.scroller   import ListScroller

from rom_so_confirm_page import RomSoConfirmPage

from UI.Emulator.list_item  import ListItem
import config
    
class RomStack:
    _Emulator = None
    
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
        if idx < 0:## empty stack,return root path
            return self._Emulator["ROM"]
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
        self._Width  = Width-12

    def AnimateDraw(self,x2,y2):
        pass

    def Draw(self):
        idx = self._Parent._PsIndex
        if idx > (len(self._Parent._MyList)-1):
            idx = len(self._Parent._MyList)
            if idx > 0:
                idx -=1
            elif idx == 0:##nothing in _MyList
                return

        self._Parent._PsIndex = idx ## sync PsIndex
        
        x = self._Parent._MyList[idx]._PosX+2
        y = self._Parent._MyList[idx]._PosY+1
        h = self._Parent._MyList[idx]._Height -3
        
        self._PosX = x
        self._PosY = y
        self._Height = h

        aa_round_rect(self._Parent._CanvasHWND,  
                    (x,y,self._Width-4,h),self._BackgroundColor,4,0,self._BackgroundColor)



class RomListPage(Page):

    _Icons = {}
    _Selector=None
    _FootMsg = ["Nav","Scan","Del","Add Fav","Run"]
    _MyList = []
    _ListFont = fonts["notosanscjk15"]
    _MyStack = None
    _Emulator = None
    _Parent   = None

    _Scroller = None
    
    _Scrolled = 0

    _BGwidth = 56
    _BGheight = 70

    _RomSoConfirmDownloadPage = None
    
    
    def __init__(self):
        Page.__init__(self)
        
        self._Icons = {}
        self._CanvasHWND = None
        self._MyList = []
        self._MyStack = RomStack()
        self._Emulator = {}
        
    def GeneratePathList(self,path):
        if os.path.isdir(path) == False:
            return False


        files_path = glob.glob(path+"/*")
        
        ret = []

        for i ,v in enumerate(files_path):
            dirmap = {}
            if os.path.isdir(v) and self._Emulator["FILETYPE"] == "dir": ## like DOSBOX
                gameshell_bat = self._Emulator["EXT"][0]
                
                stats = os.stat(v)
                if stats.st_gid == self._Parent._FavGID: ##skip fav roms
                    continue
                
                if FileExists(v+"/"+gameshell_bat):
                    dirmap["gamedir"] = v.decode("utf8")
                    ret.append(dirmap)
            if os.path.isfile(v) and self._Emulator["FILETYPE"] == "file":
                stats = os.stat(v)
                if stats.st_gid == self._Parent._FavGID: ##skip fav roms
                    continue
                
                bname = os.path.basename(v)  ### filter extension
                if len(bname)> 1:
                    pieces  = bname.split(".")
                    if len(pieces) > 1:
                        if pieces[ len(pieces)-1   ].lower() in self._Emulator["EXT"]:
                            dirmap["file"] = v
                            ret.append(dirmap)
#            else:
#                print("not file or dir")

        
        return ret

    def SyncList(self,path):
        
        alist = self.GeneratePathList(path)
        
        if alist == False:
            print("listfiles return false")
            return
                
        self._MyList = []
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

            li._Parent = self
            
            if "directory" in v:
                li._MyType = ICON_TYPES["DIR"]
                li.Init(v["directory"])
            elif "file" in v:
                li.Init(v["file"])
            elif "gamedir" in v:
                li.Init(v["gamedir"])
            else:
                li.Init("NoName")

            
            self._MyList.append(li)

        
    def Init(self):
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height

        self._CanvasHWND = self._Screen._CanvasHWND

        ps = ListPageSelector()
        ps._Parent = self
        self._Ps = ps
        self._PsIndex = 0

        self.SyncList(self._Emulator["ROM"])

        ### will also mkdir of the ***ROM self
        try: 
            os.makedirs(self._Emulator["ROM"]+"/.Trash")
        except OSError:
            if not os.path.isdir(self._Emulator["ROM"]+"/.Trash"):
                raise
            

        try: 
            os.makedirs(self._Emulator["ROM"]+"/.Fav")
        except OSError:
            if not os.path.isdir(self._Emulator["ROM"]+"/.Fav"):
                raise

        self._MyStack._Emulator = self._Emulator

        icon_for_list = MultiIconItem()
        icon_for_list._ImgSurf = self._Parent._Icons["sys"]
        icon_for_list._MyType = ICON_TYPES["STAT"]
        icon_for_list._Parent = self
        
        icon_for_list.Adjust(0,0,18,18,0)
        
        self._Icons["sys"] = icon_for_list


        bgpng = IconItem()
        bgpng._ImgSurf = MyIconPool._Icons["empty"]
        bgpng._MyType = ICON_TYPES["STAT"]
        bgpng._Parent = self
        bgpng.AddLabel("Please upload data over Wi-Fi", fonts["varela22"])
        bgpng.SetLableColor(pygame.Color(204,204,204))
        bgpng.Adjust(0,0,self._BGwidth,self._BGheight,0)

        self._Icons["bg"] = bgpng

        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = self._Width - 10
        self._Scroller._PosY = 2
        self._Scroller.Init()

        rom_so_confirm_page = RomSoConfirmPage()
        rom_so_confirm_page._Screen = self._Screen
        rom_so_confirm_page._Name = "Download Confirm"
        rom_so_confirm_page._Parent = self
        rom_so_confirm_page.Init()

        self._RomSoConfirmDownloadPage = rom_so_confirm_page
        
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
            self._Scrolled +=1

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
            self._Scrolled -= 1
            
    def SyncScroll(self):
        ## 
        if self._Scrolled == 0:
            return

        if self._PsIndex < len(self._MyList):
            cur_li = self._MyList[self._PsIndex]
            if self._Scrolled > 0:
                if cur_li._PosY < 0:
                    for i in range(0, len(self._MyList)):
                        self._MyList[i]._PosY += self._Scrolled * self._MyList[i]._Height
            elif self._Scrolled < 0:
                if cur_li._PosY +cur_li._Height > self._Height:
                    for i in range(0,len(self._MyList)):
                        self._MyList[i]._PosY += self._Scrolled * self._MyList[i]._Height
                
    def Click(self):
        if len(self._MyList) == 0:
            return

        if self._PsIndex > len(self._MyList) - 1:
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
            self._Screen._MsgBox.SetText("Launching...")
            self._Screen._MsgBox.Draw()
            self._Screen.SwapAndShow()

            if self._Emulator["FILETYPE"] == "dir":
                path = cur_li._Path +"/"+self._Emulator["EXT"][0]
            else:
                path = cur_li._Path
            
            print("Run  ",path)

            # check ROM_SO exists
            if FileExists(self._Emulator["ROM_SO"]):
                if self._Emulator["FILETYPE"] == "dir":
                    escaped_path = CmdClean(path)
                else:
                    escaped_path = CmdClean(path)
                
                custom_config = ""
                if self._Emulator["RETRO_CONFIG"] != "" and len(self._Emulator["RETRO_CONFIG"]) > 5:
                    custom_config = " -c " + self._Emulator["RETRO_CONFIG"]
                
                cmdpath = " ".join( (self._Emulator["LAUNCHER"],self._Emulator["ROM_SO"], custom_config, escaped_path))
                pygame.event.post( pygame.event.Event(RUNEVT, message=cmdpath))
                return
            else:
                
                self._Screen.PushPage(self._RomSoConfirmDownloadPage)
                self._Screen.Draw()
                self._Screen.SwapAndShow()
    
        self._Screen.Draw()
        self._Screen.SwapAndShow()

    def ReScan(self):
        if self._MyStack.Length() == 0:
            self.SyncList(self._Emulator["ROM"])
        else:
            self.SyncList( self._MyStack.Last() )

        
        idx = self._PsIndex
        if idx > (len(self._MyList)-1):
            idx = len(self._MyList)
            if idx > 0:
                idx -=1
            elif idx == 0:##nothing in _MyList
                pass
        
        self._PsIndex = idx ## sync PsIndex

        self.SyncScroll()

    def OnReturnBackCb(self):
        self.ReScan()        
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
    def KeyDown(self,event):

        if event.key == CurKeys["Menu"] : 
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["Right"]:
            self._Screen.PushCurPage()
            self._Screen.SetCurPage(self._Parent.FavListPage)
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

        if event.key == CurKeys["Enter"]:
            self.Click()

        if event.key == CurKeys["A"]:
            if len(self._MyList) == 0:
                return
            
            cur_li = self._MyList[self._PsIndex]
            if cur_li.IsFile():
                # remove any dup first
                
                try:
                    os.system("chgrp " + self._Parent._FavGname +" "+ CmdClean(cur_li._Path))
                except:
                    pass
                
                self._Screen._MsgBox.SetText("Adding to Favourite list")
                self._Screen._MsgBox.Draw()
                self._Screen.SwapAndShow()
                
                pygame.time.delay(600)
                self.ReScan()                    
                self._Screen.Draw()
                self._Screen.SwapAndShow()
                
        if event.key == CurKeys["X"]: #Scan current
           self.ReScan() 
           self._Screen.Draw()
           self._Screen.SwapAndShow()
           
        if event.key == CurKeys["Y"]: #del
            if len(self._MyList) == 0:
                return
            
            cur_li = self._MyList[self._PsIndex]
            if cur_li.IsFile():
                
                self._Parent.DeleteConfirmPage.SetFileName(cur_li._Path)
                self._Parent.DeleteConfirmPage.SetTrashDir(self._Emulator["ROM"]+"/.Trash")
            
                self._Screen.PushCurPage()
                self._Screen.SetCurPage(self._Parent.DeleteConfirmPage)
                self._Screen.Draw()
                self._Screen.SwapAndShow()
            
    def Draw(self):
        self.ClearCanvas()
        if len(self._MyList) == 0:
            self._Icons["bg"].NewCoord(self._Width/2,self._Height/2)
            self._Icons["bg"].Draw()
        else:
            if len(self._MyList) * ListItem._Height > self._Height:
                self._Ps._Width = self._Width - 10
                self._Ps.Draw()
                
                for i in self._MyList:
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
                    i.Draw()
