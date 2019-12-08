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

## local UI import
from UI.constants import Width,Height,ICON_TYPES,RESTARTUI
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.util_funcs import midRect,FileExists,ArmSystem,reconstruct_broken_string
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

class GameConfirmInstallPopupUpPage(Page):
    pass

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
 
    def GObjectUpdateProcessInterval(self):
        if self._Screen.CurPage() == self and self._GID is not None:
                self._Value =  config.RPC.tellStatus(self._GID)
	        
                downloaded = 0
                total = 0
	
		if self._Value["status"] == "waiting":
                    self._FileNameLabel.SetText( "waiting to download..." )
                if self._Value["status"] == "paused":
                    self._FileNameLabel.SetText( "download paused..." )
                if self._Value["status"] == "error":
                    self._FileNameLabel.SetText("download errors,cancel it please")
                
                if self._Value["status"] == "active":
                    downloaded = self._Value["completedLength"]
                    total      = self._Value["totalLength"]

                    downloaded = downloaded/1000.0/1000.0
                    total      = total/1000.0/1000.0
                
                self._SizeLabel.SetText( "%.2f" % downloaded+"/"+ "%.2f" % total +"Mb")
                
                print("Progress: %d%%" % (self._Value))
                self._Screen.Draw()
                self._Screen.SwapAndShow()
                return True
        else:
            return False
    
    def CheckDownload(self,aria2_gid):
        self._GID = aria2_gid 
        self._DownloaderTimer = gobject.timeout_add(123, self.GObjectUpdateProcessInterval)
        
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

class GameStorePage(Page):
    _FootMsg =  ["Nav","Update store","Up","Back","Select"]
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
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}
	self._MyStack = RPCStack()
	#title path type
        repos = [
        {"title":"github.com/cuu/gamestore","file":"https://raw.githubusercontent.com/cuu/gamestore/master/index.json","type":"dir"}
        ]
	self._MyStack.Push(repos)
    
    def SyncSqlite(self):
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
        if stk_lev == 1: # on top
            sqlite3_menu= self.SyncSqlite()
            if sqlite3_menu != None and len(sqlite3_menu) > 0:
                #print(sqlite3_menu)
                repos.extend(sqlite3_menu )

        print(repos)

        for i,u in enumerate( repos ):            
            #print(i,u)
            li = InfoPageListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + last_height
            li._Width  = Width
            li._Fonts["normal"] = self._ListFont15
            li._Active = False
            li._ReadOnly = True
            li._Value = u
            li.Init( u["title"] )

            if stk_lev >1:
                li._ReadOnly = False
            elif stk_lev == 1:
                if "status" in u:
                    if u["status"] == "complete":
                        li._ReadOnly = False
                if i == 0:
                    li._ReadOnly = False

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
 
        self._remove_page = YesCancelConfirmPage()
        self._remove_page._Screen = self._Screen
        self._remove_page._StartOrA_Event = self.RemoveGame

        self._remove_page._Name ="Are you sure?"
        self._remove_page.Init()

    def RemoveGame(self):
        if self._PsIndex > len(self._MyList) -1:
            return

        cur_li = self._MyList[self._PsIndex]
        #if cur_li._Active == True:
        #    return
        print("Remove cur_li._Value",cur_li._Value)
        
        if "gid" in cur_li._Value:
            try:
                gid = cur_li._Value["gid"]
                conn = sqlite3.connect(self._aria2_db)
                conn.row_factory = dict_factory
                c = conn.cursor()
                ret = c.execute("SELECT * FROM tasks WHERE gid='%s'" % gid ).fetchone()
                if ret != None:
                    remote_file_url = ret["file"]
                    menu_file = remote_file_url.split("master")[1]
                    local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )
                    try:
                        if os.path.exists(local_menu_file):
                            os.remove(local_menu_file)
                        if os.path.exists(local_menu_file+".aria2"):
                            os.remove(local_menu_file+".aria2")
                    except Exception as ex:
                        print(ex)


                c.execute("DELETE FROM tasks WHERE gid = '%s'" % gid )
                conn.commit()
                conn.close()
            except Exception as ex:
                print(ex)
        
      
    def Click(self):
        if self._PsIndex > len(self._MyList) -1:
            return
        
        cur_li = self._MyList[self._PsIndex]
        #if cur_li._Active == True:
        #    return

        print("cur_li._Value",cur_li._Value)
	
	if cur_li._Value["type"] == "dir":
	    remote_file_url = cur_li._Value["file"]
	    menu_file = remote_file_url.split("master")[1] #assume master branch
	    local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )
            print(local_menu_file)
            if FileExists( local_menu_file ) == False:
                print(local_menu_file, "non-existed")
                gid,ret = config.RPC.urlDownloading(remote_file_url)
		if  ret == False:
	            gid = config.RPC.addUri( remote_file_url, options={"out": menu_file})
		    self._Downloading = remote_file_url
                    
                    self._Screen._MsgBox.SetText("Loading")
                    self._Screen._MsgBox.Draw()
                    self._Screen.SwapAndShow()

                else:
                    print(gid," url is downloading")
                    self._Screen._MsgBox.SetText("Loading")
                    self._Screen._MsgBox.Draw() 
                    self._Screen.SwapAndShow()

	    else:
                #read the local_menu_file, push into stack,display menu
		self._Downloading = None
		with open(local_menu_file) as json_file:
		    local_menu_json = json.load(json_file)
                    print(local_menu_json)
 		    self._MyStack.Push(local_menu_json["list"])
		
		    self.SyncList()
                    self._Screen.Draw()
                    self._Screen.SwapAndShow()                    
		
	else:
	    #download the game probably
	    remote_file_url = cur_li._Value["file"]
            menu_file = remote_file_url.split("master")[1]
            local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )
            
	    if FileExists( local_menu_file ) == False:
                gid,ret = config.RPC.urlDownloading(remote_file_url)
                if ret == False:
                    gid = config.RPC.addUri( remote_file_url, options={"out": menu_file})
		    self._Downloading = remote_file_url
                    print("stack length ",self._MyStack.Length())
                    if self._MyStack.Length() > 1:## not on the top list page
                        try:
                            conn = sqlite3.connect("aria2tasks.db")
                            c = conn.cursor()
                            c.execute("INSERT INTO tasks(gid,title,file,type,status,fav) VALUES ('"+gid+"','"+cur_li._Value["title"]+"','"+cur_li._Value["file"]+"','"+cur_li._Value["type"]+"','active','0')")

                            conn.commit()
                            conn.close()
                        except Exception as ex:
                            print("SQLITE3 ",ex)
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
                    game_sh = os.path.join( "%s/apps/Menu/21_Indie Games/" % os.path.expanduser('~'),cur_li._Value["title"],cur_li._Value["title"]+".sh")
                    #game_sh = reconstruct_broken_string( game_sh)
                    print("run game: ",game_sh, os.path.exists(  game_sh))
                    self._Screen.RunEXE(game_sh)
                
            
    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self._DrawOnce = False
        #sync 
        print("OnLoadCb")
        if self._MyStack.Length() == 1:
            self._FootMsg[2] = "Remove"
            self._FootMsg[1] = "Update store"
        else:
            self._FootMsg[2] = "Up"
            self._FootMsg[1] = ""

        self.SyncList()
 
    def OnReturnBackCb(self):

        if self._MyStack.Length() == 1:
            self._FootMsg[2] = "Remove"
            self._FootMsg[1] = "Update store"
        else:
            self._FootMsg[2] = "Up"
            self._FootMsg[1] = ""

        self.SyncList()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
       
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

            if self._MyStack.Length() == 1:
                self._FootMsg[2] = "Remove"
                self._FootMsg[1] = "Update store"
            else:
                self._FootMsg[2] = "Up"
                self._FootMsg[1] = ""

            self._Screen.Draw()
            self._Screen.SwapAndShow()


        if event.key == CurKeys["X"]:
            #print(self._MyStack.Length() )
            if self._MyStack.Length() == 1 and self._PsIndex > 0:
                self._Screen.PushPage(self._remove_page)
                self._remove_page._StartOrA_Event = self.RemoveGame
                self._Screen.Draw()
                self._Screen.SwapAndShow()
                return 

            if self._MyStack.Length() > 1:
               self._MyStack.Pop()
               if self._MyStack.Length() == 1:
                   self._FootMsg[2] = "Remove"
                   self._FootMsg[1] = "Update store"
               else:
                   self._FootMsg[2] = "Up"
                   self._FootMsg[1] = ""

            self.SyncList()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["Y"]:
            if self._MyStack.Length() == 1:
                self._Screen._MsgBox.SetText("Done")
                self._Screen._MsgBox.Draw()
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
    
