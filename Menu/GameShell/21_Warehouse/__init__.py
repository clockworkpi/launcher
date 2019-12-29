# -*- coding: utf-8 -*- 
import os
import pygame
import platform
#import commands
import glob
import json
import gobject
import sqlite3
#from beeprint import pp
from libs.roundrects import aa_round_rect
from shutil import copyfile,rmtree

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
from UI.yes_cancel_confirm_page import YesCancelConfirmPage
from UI.keyboard import Keyboard

from UI.download   import Download

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

class LoadHousePage(Page):
    _FootMsg = ["Nav.","","","Back","Cancel"]
    _Value = 0
    _URL = None
    _ListFontObj = MyLangManager.TrFont("varela18")
    _URLColor  = MySkinManager.GiveColor('URL')
    _TextColor = MySkinManager.GiveColor('Text')
    _Caller=None
    _img = None 
    _Downloader=None
    _DownloaderTimer=-1
    def __init__(self):
        Page.__init__(self)        
        self._Icons = {}
        self._CanvasHWND = None
        
    def Init(self):
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height

        self._CanvasHWND = self._Screen._CanvasHWND
        self._LoadingLabel = Label()
        self._LoadingLabel.SetCanvasHWND(self._CanvasHWND)
        self._LoadingLabel.Init("Loading",self._ListFontObj)
        self._LoadingLabel.SetColor(self._TextColor )
 
    def OnLoadCb(self):
        if self._URL is None:
            return
        self._img = None
        self.ClearCanvas()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
        filename = self._URL.split("/")[-1].strip()
        local_dir = self._URL.split("raw.githubusercontent.com")

        if len(local_dir) >1:
            menu_file = local_dir[1]
            local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )
        
            if FileExists(local_menu_file):
                #load json
                with open(local_menu_file) as json_file:
                    try:
                        local_menu_json = json.load(json_file)
                        self._Caller._MyStack.Push(local_menu_json["list"])
                    except:
                        pass

                    self.Leave()

            else:
                self._Downloader = Download(self._URL,"/tmp",None)
                self._Downloader.start()
                self._DownloaderTimer = gobject.timeout_add(400, self.GObjectUpdateProcessInterval)

     
    def GObjectUpdateProcessInterval(self):
        ret = True
        if self._Screen.CurPage() == self:
                if self._Downloader._stop == True:
                    ret = False
 
                dst_filename = self._Downloader.get_dest()
                if self._Downloader.isFinished():
                    if self._Downloader.isSuccessful():
                        filename = self._URL.split("/")[-1].strip()
                        local_dir = self._URL.split("raw.githubusercontent.com")
                        menu_file = local_dir[1]
                        local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )

                        dl_file = os.path.join("/tmp",filename)
                        if not os.path.exists(os.path.dirname(local_menu_file)):
                            os.makedirs(os.path.dirname(local_menu_file))

                        copyfile(dl_file, local_menu_file)
                        with open(local_menu_file) as json_file:
                            try:
                                local_menu_json = json.load(json_file)
                                self._Caller._MyStack.Push(local_menu_json["list"])
                            except:
                                pass

                        ret = False

                        self.Leave()
                    else:
                        self._Screen._MsgBox.SetText("Fetch house failed")
                        self._Screen._MsgBox.Draw()
                        self._Screen.SwapAndShow()
                        ret = False
                return ret
        else:
            return False
    
    def Leave(self):
        if self._DownloaderTimer != -1:
            gobject.source_remove(self._DownloaderTimer)
        self._DownloaderTimer = -1
            
        if self._Downloader != None:
            try:
                self._Downloader.stop()
            except:
                print("user canceled ")
            
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        self._URL = None

    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
            self.Leave()

    def Draw(self):
        self.ClearCanvas()
        self._LoadingLabel.NewCoord( (Width-self._LoadingLabel._Width)/2,(Height-44)/2)
        self._LoadingLabel.Draw()

        if self._img is not None:
            self._CanvasHWND.blit(self._img,midRect(Width/2,
                                       (Height-44)/2,
                                       pygame.Surface.get_width(self._img),pygame.Surface.get_height(self._img),Width,Height-44))


class ImageDownloadProcessPage(Page):
    _FootMsg = ["Nav.","","","Back",""]
    _Value = 0
    _URL = None
    _ListFontObj = MyLangManager.TrFont("varela13")
    _URLColor  = MySkinManager.GiveColor('URL')
    _TextColor = MySkinManager.GiveColor('Text')
    _img = None 
    _Downloader=None
    _DownloaderTimer=-1 
    def __init__(self):
        Page.__init__(self)        
        self._Icons = {}
        self._CanvasHWND = None
        
    def Init(self):
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height

        self._CanvasHWND = self._Screen._CanvasHWND
        self._LoadingLabel = Label()
        self._LoadingLabel.SetCanvasHWND(self._CanvasHWND)
        self._LoadingLabel.Init("Loading",self._ListFontObj)
        self._LoadingLabel.SetColor(self._TextColor )
 
    def OnLoadCb(self):
        if self._URL is None:
            return
        self._img = None
        self.ClearCanvas()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
        filename = self._URL.split("/")[-1].strip()
        local_dir = self._URL.split("raw.githubusercontent.com")

        if len(local_dir) >1:
            menu_file = local_dir[1]
            local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )
        
            if FileExists(local_menu_file):
                self._img = pygame.image.load(local_menu_file).convert_alpha()
                self._Screen.Draw()
                self._Screen.SwapAndShow()
            else:
                self._Downloader = Download(self._URL,"/tmp",None)
                self._Downloader.start()
                self._DownloaderTimer = gobject.timeout_add(300, self.GObjectUpdateProcessInterval)

     
    def GObjectUpdateProcessInterval(self):
        ret = True
        if self._Screen.CurPage() == self:
                if self._Downloader._stop == True:
                    ret = False
 
                dst_filename = self._Downloader.get_dest()
                if self._Downloader.isFinished():
                    if self._Downloader.isSuccessful():
                        filename = self._URL.split("/")[-1].strip()
                        local_dir = self._URL.split("raw.githubusercontent.com")
                        menu_file = local_dir[1]
                        local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )
                        
                        dl_file = os.path.join("/tmp",filename)
                        if not os.path.exists(os.path.dirname(local_menu_file)):
                            os.makedirs(os.path.dirname(local_menu_file))

                        copyfile(dl_file, local_menu_file)
                        ret = False
 
                #print("dest ",dst_filename)
                if FileExists(dst_filename):
                    try:
                        #print("load and draw")
                        self._img = pygame.image.load(dst_filename).convert_alpha()
                        self._Screen.Draw()
                        self._Screen.SwapAndShow()
                    except Exception as ex:
                        print(ex)

                return ret
        else:
            return False
    
        
    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
            gobject.source_remove(self._DownloaderTimer)
            self._DownloaderTimer = -1
            
            if self._Downloader != None:
                try:
                    self._Downloader.stop()
                except:
                    print("user canceled ")
            
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            self._URL = None

    def Draw(self):
        self.ClearCanvas()
        self._LoadingLabel.NewCoord( (Width-self._LoadingLabel._Width)/2,(Height-44)/2)
        self._LoadingLabel.Draw()

        if self._img is not None:
            self._CanvasHWND.blit(self._img,midRect(Width/2,
                                       (Height-44)/2,
                                       pygame.Surface.get_width(self._img),pygame.Surface.get_height(self._img),Width,Height-44))


class Aria2DownloadProcessPage(Page):
    _FootMsg = ["Nav.","","Pause","Back","Cancel"]
    _DownloaderTimer = -1
    _Value = 0
    _GID = None

    _PngSize = {}

    _FileNameLabel = None
    _SizeLabel     = None

    _URLColor  = MySkinManager.GiveColor('URL')
    _TextColor = MySkinManager.GiveColor('Text')
    
    def __init__(self):
        Page.__init__(self)        
        self._Icons = {}
        self._CanvasHWND = None
        
    def Init(self):
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height

        self._CanvasHWND = self._Screen._CanvasHWND

        bgpng = IconItem()
        bgpng._ImgSurf = MyIconPool.GiveIconSurface("rom_download")
        bgpng._MyType = ICON_TYPES["STAT"]
        bgpng._Parent = self
        bgpng.Adjust(0,0,self._PngSize["bg"][0],self._PngSize["bg"][1],0)
        self._Icons["bg"] = bgpng

        
        self._FileNameLabel = Label()
        self._FileNameLabel.SetCanvasHWND(self._CanvasHWND)
        self._FileNameLabel.Init("", MyLangManager.TrFont("varela12"))

        self._SizeLabel = Label()
        self._SizeLabel.SetCanvasHWND(self._CanvasHWND)
        self._SizeLabel.Init("0/0Kb",MyLangManager.TrFont("varela12"))
        self._SizeLabel.SetColor( self._URLColor )
 
    @property
    def GObjectUpdateProcessInterval(self):
        downloaded = 0
        if self._Screen.CurPage() == self and self._GID is not None:
                self._Value =  config.RPC.tellStatus(self._GID)
            
                downloaded = 0
                total = 0

        if self._Value["status"] == "waiting":
            self._FileNameLabel.SetText("waiting to download...")
        if self._Value["status"] == "paused":
            self._FileNameLabel.SetText("download paused...")
        if self._Value["status"] == "error":
            self._FileNameLabel.SetText("download errors,cancel it please")

        if self._Value["status"] == "active":
            downloaded = self._Value["completedLength"]
            total = self._Value["totalLength"]

            downloaded = downloaded / 1000.0 / 1000.0
            total = total / 1000.0 / 1000.0

        self._SizeLabel.SetText("%.2f" % downloaded+"/"+"%.2f" % total+"Mb")

        print("Progress: %d%%" % (self._Value))
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        return True

    
    def CheckDownload(self,aria2_gid):
        self._GID = aria2_gid 
        self._DownloaderTimer = gobject.timeout_add(234, self.GObjectUpdateProcessInterval)
        
    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
            gobject.source_remove(self._DownloaderTimer)
            self._DownloaderTimer = -1
            
            #if self._Downloader != None:
            #    try:
            #        self._Downloader.stop()
            #    except:
            #        print("user canceled ")
            
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
    def Draw(self):
        self.ClearCanvas()

        self._Icons["bg"].NewCoord(self._Width/2,self._Height/2-20)
        self._Icons["bg"].Draw()
        
        percent = self._Value
        if percent < 10:
            percent = 10

        
        rect_ = midRect(self._Width/2,self._Height/2+33,170,17, Width,Height)
        aa_round_rect(self._CanvasHWND,rect_,MySkinManager.GiveColor('TitleBg'),5,0,MySkinManager.GiveColor('TitleBg'))
        
        rect2 = midRect(self._Width/2,self._Height/2+33,int(170*(percent/100.0)),17, Width,Height)
        rect2.left = rect_.left
        rect2.top  = rect_.top
        aa_round_rect(self._CanvasHWND,rect2,MySkinManager.GiveColor('Front'),5,0,MySkinManager.GiveColor('Front'))

        rect3 = midRect(self._Width/2,self._Height/2+53,self._FileNameLabel._Width, self._FileNameLabel._Height,Width,Height)

        rect4 = midRect(self._Width/2,self._Height/2+70,self._SizeLabel._Width, self._SizeLabel._Height,Width,Height)

        self._FileNameLabel.NewCoord(rect3.left,rect3.top)
        self._SizeLabel.NewCoord(rect4.left, rect4.top)

        self._FileNameLabel.Draw()
        self._SizeLabel.Draw()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class GameStoreListItem(InfoPageListItem):
    _Type = None #source,dir,launcher,pico8 
    _CanvasHWND = None 
    def Init(self,text):

        #self._Fonts["normal"] = fonts["veramono12"]
        
        l = Label()
        l._PosX = 10
        l.SetCanvasHWND(self._Parent._CanvasHWND)

        l.Init(text,self._Fonts["normal"])
        self._Labels["Text"] = l
        
        add_icon = IconItem()
        add_icon._ImgSurf = MyIconPool.GiveIconSurface("add")
        add_icon._CanvasHWND = self._CanvasHWND
        add_icon._Parent = self
        add_icon.Init(0,0,MyIconPool.Width("add"),MyIconPool.Height("add"),0)
 
        ware_icon = IconItem()
        ware_icon._ImgSurf = MyIconPool.GiveIconSurface("ware")
        ware_icon._CanvasHWND = self._CanvasHWND
        ware_icon._Parent = self
        ware_icon.Init(0,0,MyIconPool.Width("ware"),MyIconPool.Height("ware"),0)

        app_icon = IconItem()
        app_icon._ImgSurf = MyIconPool.GiveIconSurface("app")
        app_icon._CanvasHWND = self._CanvasHWND
        app_icon._Parent = self
        app_icon.Init(0,0,MyIconPool.Width("app"),MyIconPool.Height("app"),0)

        appdling_icon = IconItem()
        appdling_icon._ImgSurf = MyIconPool.GiveIconSurface("appdling")
        appdling_icon._CanvasHWND = self._CanvasHWND
        appdling_icon._Parent = self
        appdling_icon.Init(0,0,MyIconPool.Width("appdling"),MyIconPool.Height("appdling"),0)

        blackheart_icon = IconItem()
        blackheart_icon._ImgSurf = MyIconPool.GiveIconSurface("blackheart")
        blackheart_icon._Width = MyIconPool.Width("blackheart")
        blackheart_icon._Height = MyIconPool.Height("blackheart")
        blackheart_icon._CanvasHWND = self._CanvasHWND
        blackheart_icon._Parent = self

        self._Icons["add"] = add_icon
        self._Icons["ware"] = ware_icon
        self._Icons["app"]  = app_icon
        self._Icons["appdling"] = appdling_icon
        self._Icons["blackheart"] = blackheart_icon

    
    def Draw(self):
        if self._ReadOnly == True:
            self._Labels["Text"].SetColor(MySkinManager.GiveColor("ReadOnlyText"))
        else:
            self._Labels["Text"].SetColor(MySkinManager.GiveColor("Text"))

        padding = 17

        if self._Type == None:
            padding = 0
         
        
        if self._Type == "source" or self._Type == "dir":
            self._Icons["ware"].NewCoord( 4, (self._Height - self._Icons["ware"]._Height)/2 )
            self._Icons["ware"].DrawTopLeft()
        
        if self._Type == "launcher" or self._Type == "pico8" or self._Type == "tic80":
            _icon = "app"
            if self._ReadOnly == True:
                _icon = "appdling"
            
            self._Icons[_icon].NewCoord( 4, (self._Height - self._Icons[_icon]._Height)/2)
            self._Icons[_icon].DrawTopLeft()
           
        if self._Type == "add_house":
            self._Icons["add"].NewCoord( 4, (self._Height - self._Icons["add"]._Height)/2)
            self._Icons["add"].DrawTopLeft()


        self._Labels["Text"]._PosX = self._Labels["Text"]._PosX + self._PosX + padding
        self._Labels["Text"]._PosY = self._PosY + (self._Height - self._Labels["Text"]._Height)/2
        self._Labels["Text"].Draw()
        self._Labels["Text"]._PosX = self._Labels["Text"]._PosX - self._PosX - padding

        if "Small" in self._Labels:
            self._Labels["Small"]._PosX = self._Width - self._Labels["Small"]._Width-5
            
            self._Labels["Small"]._PosY = self._PosY + (self._Height - self._Labels["Small"]._Height)/2
            self._Labels["Small"].Draw()
        

        pygame.draw.line(self._Parent._CanvasHWND,MySkinManager.GiveColor('Line'),(self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)
 

class GameStorePage(Page):
    _FootMsg =  ["Nav","Update","Up","Back","Select"]
    _MyList = []
    _ListFont12 = MyLangManager.TrFont("notosanscjk12")
    _ListFont15 = MyLangManager.TrFont("varela15")
   
    _AList = {}

    _Scrolled = 0
    
    _BGwidth = 320
    _BGheight = 240-24-20

    _DrawOnce = False
    _Scroller = None
    _InfoPage = None
    _Downloading = None
    _aria2_db = "aria2tasks.db"
    _warehouse_db = "warehouse.db"
    _GobjTimer = -1

    _Scrolled_cnt = 0

    def __init__(self):
        Page.__init__(self)
        self._Icons = {}
        self._MyStack = RPCStack()
          #title file type
        ## Two level url , only github.com
        
        repos = [
         {"title":"github.com/clockworkpi/warehouse","file":"https://raw.githubusercontent.com/clockworkpi/warehouse/master/index.json","type":"source"}
        ]
        self._MyStack.Push(repos)
 
    def GObjectUpdateProcessInterval(self):
        ret = True
        dirty = False
        for x in self._MyList:
            if x._Type == "launcher" or x._Type == "pico8" or x._Type == "tic80":
                percent = config.RPC.getPercent(x._Value["file"])
                if percent is not None:
                    x.SetSmallText(str(percent)+"%")
                    dirty = True
                else:
                    x.SetSmallText("")

        if self._Screen.CurPage() == self and dirty == True:
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        return ret

    def SyncWarehouse(self):
        try:
            conn = sqlite3.connect(self._warehouse_db)
            conn.row_factory = dict_factory
            c = conn.cursor()
            ret = c.execute("SELECT * FROM warehouse").fetchall()
            conn.close()
            return ret
        except Exception as ex:
            print(ex)
            return None
        return None

    def SyncTasks(self):
        try:
            conn = sqlite3.connect(self._aria2_db)
            conn.row_factory = dict_factory
            c = conn.cursor()
            ret = c.execute("SELECT * FROM tasks").fetchall()
            conn.close()
            return ret
        except Exception as ex:
            print(ex)
            return None
        return None

    def SyncList(self):
        
        self._MyList = []
        
        start_x  = 0
        start_y  = 0
        last_height = 0

        repos = []
        stk = self._MyStack.Last()
        stk_lev = self._MyStack.Length()
        repos.extend(stk)
        add_new_house = [
            {"title":"Add new warehouse...","file":"master/index.json","type":"add_house","status":"complete"}
        ]

        if stk_lev == 1: # on top
            ware_menu= self.SyncWarehouse()
            if ware_menu != None and len(ware_menu) > 0:
                #print(ware_menu)
                repos.extend(ware_menu )

            tasks_menu= self.SyncTasks()
            if tasks_menu != None and len(tasks_menu) > 0:
                #print(tasks_menu)
                repos.extend(tasks_menu )
            
            #print(repos)
            repos.extend(add_new_house)

        for i,u in enumerate( repos ):            
            #print(i,u)
            li = GameStoreListItem()
            li._CanvasHWND = self._CanvasHWND
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + last_height
            li._Width  = Width
            li._Fonts["normal"] = self._ListFont15
            li._Fonts["small"]  = self._ListFont12
            li._Active = False
            li._ReadOnly = True
            li._Value = u
            li._Type = u["type"]
            li.Init( u["title"] )
            
            if stk_lev >1:
                remote_file_url = u["file"]
                menu_file = remote_file_url.split("raw.githubusercontent.com")[1]
                local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )

                if FileExists(local_menu_file):
                    li._ReadOnly = False
                else:
                    li._ReadOnly = True
            elif stk_lev == 1:
                if "status" in u:
                    if u["status"] == "complete":
                        li._ReadOnly = False

                if u["type"]=="source":
                    li._ReadOnly = False

            last_height += li._Height
            
            if li._Type == "launcher" or li._Type == "pico8" or li._Type == "tic80":
                li.SetSmallText("")
            
            self._MyList.append(li)
            
        self.RefreshPsIndex()
            
        
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
        self._Scroller.SetCanvasHWND(self._CanvasHWND)
 
        self._remove_page = YesCancelConfirmPage()
        self._remove_page._Screen = self._Screen
        self._remove_page._StartOrA_Event = self.RemoveGame

        self._remove_page._Name ="Are you sure?"
        self._remove_page.Init()

        self._Keyboard = Keyboard()
        self._Keyboard._Name = "Enter warehouse addr"
        self._Keyboard._FootMsg = ["Nav.","Add","ABC","Backspace","Enter"]
        self._Keyboard._Screen = self._Screen
        self._Keyboard.Init()
        self._Keyboard.SetPassword("github.com/clockworkpi/warehouse")
        self._Keyboard._Caller = self

        self._PreviewPage = ImageDownloadProcessPage()
        self._PreviewPage._Screen = self._Screen
        self._PreviewPage._Name = "Preview"
        self._PreviewPage.Init()

        self._LoadHousePage = LoadHousePage()
        self._LoadHousePage._Screen = self._Screen
        self._LoadHousePage._Name = "Warehouse"
        self._LoadHousePage._Caller = self
        self._LoadHousePage.Init()


    def ResetHouse(self):
        if self._PsIndex > len(self._MyList) -1:
            return
        cur_li = self._MyList[self._PsIndex]
        if cur_li._Value["type"] == "source":
            remote_file_url = cur_li._Value["file"]
            menu_file = remote_file_url.split("raw.githubusercontent.com")[1] #assume master branch
            local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )
            local_menu_file_path = os.path.dirname(local_menu_file)
            print(local_menu_file_path)
            local_jsons = glob.glob(local_menu_file_path+"/**/*.json")
            try:
                if os.path.exists(local_menu_file):
                    os.remove(local_menu_file)
                if os.path.exists(local_menu_file+".aria2"):
                    os.remove(local_menu_file+".aria2")

                for x in local_jsons:
                    os.remove(x)

            except Exception as ex:
                print(ex)

            self._Screen._MsgBox.SetText("Done")
            self._Screen._MsgBox.Draw()
            self._Screen.SwapAndShow()

    def LoadHouse(self):
        if self._PsIndex > len(self._MyList) -1:
            return
        cur_li = self._MyList[self._PsIndex]
        if cur_li._Value["type"] == "source" or cur_li._Value["type"] == "dir":

            self._LoadHousePage._URL = cur_li._Value["file"]
            self._Screen.PushPage(self._LoadHousePage)
            self._Screen.Draw()
            self._Screen.SwapAndShow()


    def PreviewGame(self):
        if self._PsIndex > len(self._MyList) -1:
            return
        cur_li = self._MyList[self._PsIndex]
        if cur_li._Value["type"] == "launcher" or cur_li._Value["type"] == "pico8" or cur_li._Value["type"] == "tic80":
            if "shots" in cur_li._Value:
                print(cur_li._Value["shots"])
                self._PreviewPage._URL = cur_li._Value["shots"]
                self._Screen.PushPage(self._PreviewPage)
                self._Screen.Draw()
                self._Screen.SwapAndShow()


    def RemoveGame(self):
        if self._PsIndex > len(self._MyList) -1:
            return

        cur_li = self._MyList[self._PsIndex]
        #if cur_li._Active == True:
        #    return
        print("Remove cur_li._Value",cur_li._Value)
        
        if cur_li._Value["type"] == "source":
            print("remove a source")
            try:
                conn = sqlite3.connect(self._warehouse_db)
                conn.row_factory = dict_factory
                c = conn.cursor()
                c.execute("DELETE FROM warehouse WHERE file = '%s'" % cur_li._Value["file"] )
                conn.commit()
                conn.close()
            except Exception as ex:
                print(ex)
        elif cur_li._Value["type"] == "launcher" or cur_li._Value["type"] == "pico8" or cur_li._Value["type"] == "tic80":  
            remote_file_url = cur_li._Value["file"]
            menu_file = remote_file_url.split("raw.githubusercontent.com")[1]
            local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )
            local_menu_file_path = os.path.dirname(local_menu_file)
            
            gid,ret = config.RPC.urlDownloading(remote_file_url)
            if ret == True:
                config.RPC.remove(gid)

            try:
                if os.path.exists(local_menu_file):
                    os.remove(local_menu_file)
                if os.path.exists(local_menu_file+".aria2"):
                    os.remove(local_menu_file+".aria2")
                if os.path.exists( os.path.join(local_menu_file_path,cur_li._Value["title"])):
                    rmtree(os.path.join(local_menu_file_path,cur_li._Value["title"]) )
                
            except Exception as ex:
                print(ex)

    def Click(self):
        if self._PsIndex > len(self._MyList) -1:
            return

        cur_li = self._MyList[self._PsIndex]
        #if cur_li._Active == True:
        #    return

        print("cur_li._Value",cur_li._Value)

        if cur_li._Value["type"] == "source" or cur_li._Value["type"] == "dir":
            remote_file_url = cur_li._Value["file"]
            menu_file = remote_file_url.split("raw.githubusercontent.com")[1] #assume master branch
            local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )
            print(local_menu_file)
            if FileExists( local_menu_file ) == False:
                self.LoadHouse()
            else:
            #read the local_menu_file, push into stack,display menu
                self._Downloading = None
                try:
                    with open(local_menu_file) as json_file:
                        local_menu_json = json.load(json_file)
                        print(local_menu_json)
                        self._MyStack.Push(local_menu_json["list"])

                    self.SyncList()
                    self._Screen.Draw()
                    self._Screen.SwapAndShow()
                except Exception as ex:
                    print(ex)
                    self._Screen._MsgBox.SetText("Open house failed ")
                    self._Screen._MsgBox.Draw()
                    self._Screen.SwapAndShow()

        elif cur_li._Value["type"] == "add_house":
            print("show keyboard to add ware house")
            self._Screen.PushCurPage()
            self._Screen.SetCurPage( self._Keyboard )
        else:
            #download the game probably
            remote_file_url = cur_li._Value["file"]
            menu_file = remote_file_url.split("raw.githubusercontent.com")[1]
            local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )

            if FileExists( local_menu_file ) == False:
                gid,ret = config.RPC.urlDownloading(remote_file_url)
                if ret == False:
                    gid = config.RPC.addUri( remote_file_url, options={"out": menu_file})
                    self._Downloading = gid
                    print("stack length ",self._MyStack.Length())
                    """
                    if self._MyStack.Length() > 1:## not on the top list page
                        try:
                            conn = sqlite3.connect(self._aria2_db)
                            c = conn.cursor()
                            c.execute("INSERT INTO tasks(gid,title,file,type,status,fav) VALUES ('"+gid+"','"+cur_li._Value["title"]+"','"+cur_li._Value["file"]+"','"+cur_li._Value["type"]+"','active','0')")

                            conn.commit()
                            conn.close()
                        except Exception as ex:
                            print("SQLITE3 ",ex)
                    """
                else:
                    print(config.RPC.tellStatus(gid,["status","totalLength","completedLength"]))

                    self._Screen._MsgBox.SetText("Getting the game now")
                    self._Screen._MsgBox.Draw()
                    self._Screen.SwapAndShow()

                    pygame.time.delay(800)
                    self._Screen._TitleBar.Redraw()

            else:
                print("file downloaded")# maybe check it if is installed,then execute it
                if cur_li._Value["type"]=="launcher" and cur_li._ReadOnly == False:
                    local_menu_file_path = os.path.dirname(local_menu_file)
                    game_sh = os.path.join( local_menu_file_path, cur_li._Value["title"],cur_li._Value["title"]+".sh")
                    #game_sh = reconstruct_broken_string( game_sh)
                    print("run game: ",game_sh, os.path.exists(  game_sh))
                    self._Screen.RunEXE(game_sh)

                if cur_li._Value["type"]=="pico8" and cur_li._ReadOnly == False:
                    if os.path.exists("/home/cpi/games/PICO-8/pico-8/pico8") == True:
                        game_sh = "/home/cpi/launcher/Menu/GameShell/50_PICO-8/PICO-8.sh"
                        self._Screen.RunEXE(game_sh)
                    else:
                        self._Screen._MsgBox.SetText("Purchase pico8")
                        self._Screen._MsgBox.Draw()
                        self._Screen.SwapAndShow()
                        pygame.time.delay(800)

                if cur_li._Value["type"]=="tic80" and cur_li._ReadOnly == False:
                    game_sh = "/home/cpi/apps/Menu/51_TIC-80/TIC-80.sh"
                    self._Screen.RunEXE(game_sh)

    def OnAria2CompleteCb(self,gid):
        print("OnAria2CompleteCb ", gid)
        self.SyncList()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
 
    def raw_github_com(self,_url):#eg: github.com/clockworkpi/warehouse
        if _url.startswith("github.com")== False:
            return False
        parts = _url.split("/")
        if len(parts) != 3:
            return False
        return "/".join(["https://raw.githubusercontent.com",parts[1],parts[2],"master/index.json"])

    def OnKbdReturnBackCb(self):
        inputed = "".join(self._Keyboard._Textarea._MyWords).strip()
        inputed = inputed.replace("http://","")
        inputed = inputed.replace("https://","")
        
        if inputed.endswith(".git"):
             inputed = inputed[:len(inputed)-4]
        if inputed.endswith("/"):
             inputed = inputed[:len(inputed)-1]
        
        print("last: ",inputed)
        try:
            conn = sqlite3.connect(self._warehouse_db)
            conn.row_factory = dict_factory
            c = conn.cursor()
            ret = c.execute("SELECT * FROM warehouse WHERE title='%s'" % inputed ).fetchone()
            if ret != None:
                self._Screen._MsgBox.SetText("Warehouse existed!")
                self._Screen._MsgBox.Draw()
                self._Screen.SwapAndShow()
            else:
                if "github.com/clockworkpi/warehouse" in inputed:
                    self._Screen._MsgBox.SetText("Warehouse existed!")
                    self._Screen._MsgBox.Draw()
                    self._Screen.SwapAndShow()
                else:
                    valid_url= self.raw_github_com(inputed)
                
                    if valid_url == False:
                        self._Screen._MsgBox.SetText("Warehouse url error!")
                        self._Screen._MsgBox.Draw()
                        self._Screen.SwapAndShow()
                    else:
                        sql_insert = """ INSERT INTO warehouse(title,file,type) VALUES(
                                     '%s',
                                     '%s',
                                     'source');""" % (inputed,valid_url)

                        c.execute(sql_insert)
                        conn.commit()
                        self.SyncList()
                        self._Screen.Draw()
                        self._Screen.SwapAndShow()
            conn.close()
        except Exception as ex:
            print(ex)
     
    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self._DrawOnce = False
        #sync 
        print("OnLoadCb")
        if self._MyStack.Length() == 1:
            self._FootMsg[2] = "Remove"
            self._FootMsg[1] = "Update"
        else:
            self._FootMsg[2] = "Remove"
            self._FootMsg[1] = "Preview"
        
        self._GobjTimer = gobject.timeout_add(500, self.GObjectUpdateProcessInterval)
        
        self.SyncList()
 
    def OnReturnBackCb(self):
        if self._MyStack.Length() == 1:
            self._FootMsg[2] = "Remove"
            self._FootMsg[1] = "Update"
        else:
            self._FootMsg[2] = "Remove"
            self._FootMsg[1] = "Preview"

        self.SyncList()
        self.RestoreScrolled()

        self._Screen.Draw()
        self._Screen.SwapAndShow()
       
        """
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        """

    def ScrollDown(self):
        if len(self._MyList) == 0:
            return
        self._PsIndex += 1
        if self._PsIndex >= len(self._MyList):
            self._PsIndex = len(self._MyList)-1

        cur_li = self._MyList[self._PsIndex]
        if cur_li._PosY+cur_li._Height > self._Height:
            for i in range(0, len(self._MyList)):
                self._MyList[i]._PosY -= self._MyList[i]._Height

            self._Scrolled_cnt -= self._MyList[i]._Height

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

            self._Scrolled_cnt += self._MyList[i]._Height

    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):

            if self._MyStack.Length() > 1:
               self._MyStack.Pop()
               if self._MyStack.Length() == 1:
                   self._FootMsg[2] = "Remove"
                   self._FootMsg[1] = "Update"
               else:
                   self._FootMsg[2] = "Remove"
                   self._FootMsg[1] = "Preview"
                   if self._MyStack.Length() == 2:
                       self._FootMsg[2] = ""
                       self._FootMsg[1] = ""

               self.SyncList()
               self._Screen.Draw()
               self._Screen.SwapAndShow()

            elif self._MyStack.Length() == 1:
                self.ReturnToUpLevelPage()
                self._Screen.Draw()
                self._Screen.SwapAndShow()
                gobject.source_remove(self._GobjTimer)

        if IsKeyStartOrA(event.key):
            self.Click()

            if self._MyStack.Length() == 1:
                self._FootMsg[2] = "Remove"
                self._FootMsg[1] = "Update"
            else:
                self._FootMsg[2] = "Remove"
                self._FootMsg[1] = "Preview"
                if self._MyStack.Length() == 2:
                    self._FootMsg[2] = ""
                    self._FootMsg[1] = ""
                

            self._Screen.Draw()
            self._Screen.SwapAndShow()


        if event.key == CurKeys["X"]:
            #print(self._MyStack.Length() )
            if  self._PsIndex <= len(self._MyList) -1:
                cur_li = self._MyList[self._PsIndex]
                if  cur_li._Type != "dir":
                    if self._MyStack.Length() == 1 and self._PsIndex == 0:
                        pass
                        #predefined source
                    else:
                        self._Screen.PushPage(self._remove_page)
                        self._remove_page._StartOrA_Event = self.RemoveGame
                        self._Screen.Draw()
                        self._Screen.SwapAndShow()
                return 

            self.SyncList()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["Y"]:
            if self._MyStack.Length() == 1:
                self.ResetHouse()
            else:
                self.PreviewGame()
 
        if event.key == CurKeys["Up"]:
            self.ScrollUp()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["Down"]:
            self.ScrollDown()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

    def RestoreScrolled(self):
        for i in range(0, len(self._MyList)):
            self._MyList[i]._PosY += self._Scrolled_cnt

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
        self._Page._Name ="Warehouse"
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
    
