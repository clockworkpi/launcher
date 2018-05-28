# -*- coding: utf-8 -*- 

import pygame
import os
import requests
import validators
import gobject


## local UI import
from UI.page  import Page
from UI.constants import ICON_TYPES,Width,Height,RUNEVT
from UI.icon_item import IconItem
from UI.icon_pool import MyIconPool
from UI.label  import Label
from UI.fonts  import fonts
from UI.util_funcs import midRect,CmdClean,get_git_revision_short_hash
from UI.keys_def import CurKeys
from UI.confirm_page import ConfirmPage
from UI.download     import Download
from UI.download_process_page import DownloadProcessPage

from libs.roundrects import aa_round_rect
from libs.DBUS       import is_wifi_connected_now

import config

class UpdateDownloadPage(DownloadProcessPage):
    _MD5 = ""

    def GObjectUpdateProcessInterval(self):
        if self._Screen.CurPage() == self:
            if self._Downloader.isFinished():
                if self._Downloader.isSuccessful():
                    print("Success!")
                    # Do something with obj.get_dest()
                    filename = self._Downloader.get_dest()
                    
                    if filename.endswith(".tar.gz"):                    
                        #/home/cpi/apps/[launcher]
                        cmdpath = "tar zxf " + CmdClean(filename) + " -C /home/cpi/apps ;rm -rf "+ filename
                        pygame.event.post( pygame.event.Event(RUNEVT, message=cmdpath))
                        
                    self.ReturnToUpLevelPage()
                    self._Screen.Draw()
                    self._Screen.SwapAndShow()
                    
                else:
                    print("Download failed with the following exceptions:")
                    for e in self._Downloader.get_errors():
                        print(unicode(e))

                    try:
                        self._Downloader.stop()
                    except:
                        pass

                    filename = self._Downloader.get_dest()
                    print(filename)
                    os.system("rm -rf %s" % CmdClean(filename))
                    
                    self._Screen._MsgBox.SetText("Download failed")
                    self._Screen._MsgBox.Draw()
                    self._Screen.SwapAndShow()
                    return False
            else:
                self._Value =  self._Downloader.get_progress()
                print("Progress: %d%%" % (self._Value))
                self._Screen.Draw()
                self._Screen.SwapAndShow()
                return True
        else:
            return False
    
    def StartDownload(self,url,dst_dir):
        if validators.url(url) and os.path.isdir(dst_dir):
            self._URL = url
            self._DST_DIR = dst_dir
        else:
            self._Screen._MsgBox.SetText("Invaid")
            self._Screen._MsgBox.Draw()
            self._Screen.SwapAndShow()            
            return
        
        self._Downloader = Download(url,dst_dir,None)
        if self._MD5 != None:
            if len(self._MD5) == 32:
                self._Downloader.add_hash_verification('md5' ,self._MD5) ## hashlib provide algorithms

        self._Downloader.start()
        
        self._DownloaderTimer = gobject.timeout_add(100, self.GObjectUpdateProcessInterval)

    

class UpdateConfirmPage(ConfirmPage):
    _ConfirmText = "Confirm Update ?"
    
    _DownloadPage = None

    _URL = ""
    _MD5 = ""
    _Version = ""
    _GIT = False
    
    def KeyDown(self,event):
        if event.key == CurKeys["Menu"] or event.key == CurKeys["A"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
        if event.key == CurKeys["B"]:
            if self._GIT == True:
                cmdpath = "feh --bg-center /home/cpi/apps/launcher/sys.py/gameshell/wallpaper/updating.png; cd /home/cpi/apps/launcher ;git pull; git reset --hard %s ; feh --bg-center /home/cpi/apps/launcher/sys.py/gameshell/wallpaper/loading.png " % self._Version
                pygame.event.post( pygame.event.Event(RUNEVT, message=cmdpath))
                self._GIT = False
                return
            
            if self._DownloadPage == None:
                self._DownloadPage = UpdateDownloadPage()
                self._DownloadPage._Screen = self._Screen
                self._DownloadPage._Name   = "Downloading..."                
                self._DownloadPage.Init()

            self._DownloadPage._MD5 = self._MD5
            self._Screen.PushPage(self._DownloadPage)
            self._Screen.Draw()
            self._Screen.SwapAndShow()

            if self._URL != None and validators.url(self._URL):
                self._DownloadPage.StartDownload(self._URL, "/tmp")
            else:
                print "error url  %s " % self._URL
            

    def OnReturnBackCb(self):
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
            
    def Draw(self):
        self.ClearCanvas()
        self.DrawBG()
        for i in self._MyList:
            i.Draw()
        
        self.Reset()


class InfoPageListItem(object):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 30

    _Labels = {}
    _Icons  = {}
    _Fonts  = {}

    _LinkObj = None
    
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

        #self._Fonts["normal"] = fonts["veramono12"]
        
        l = Label()
        l._PosX = 10
        l.SetCanvasHWND(self._Parent._CanvasHWND)

        l.Init(text,self._Fonts["normal"])
        self._Labels["Text"] = l

    def Draw(self):
        
        self._Labels["Text"]._PosY = self._PosY + (self._Height - self._Labels["Text"]._Height)/2
        self._Labels["Text"].Draw()

        if "Small" in self._Labels:
            self._Labels["Small"]._PosX = self._Width - self._Labels["Small"]._Width-5
            
            self._Labels["Small"]._PosY = self._PosY + (self._Height - self._Labels["Small"]._Height)/2
            self._Labels["Small"].Draw()
        
        pygame.draw.line(self._Parent._CanvasHWND,(169,169,169),(self._PosX,self._PosY+self._Height-1),(self._PosX+self._Width,self._PosY+self._Height-1),1)
        

class UpdatePage(Page):
    _Icons = {}
    _FootMsg = ["Nav.","Check Update","","Back",""]

    _ListFontObj = fonts["varela15"]    
    _ConfirmPage = None
    _AList    = {}
    _MyList   = []
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}    

    def GenList(self):
        
        start_x  = 0
        start_y  = 0
        
        for i,v in enumerate( self._AList):
            li = InfoPageListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + i*InfoPageListItem._Height
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
        self._CanvasHWND = self._Screen._CanvasHWND
        self._Width =  self._Screen._Width
        self._Height = self._Screen._Height

        self._ConfirmPage = UpdateConfirmPage()
        self._ConfirmPage._Screen = self._Screen
        self._ConfirmPage._Name  = "Update Confirm"
        self._ConfirmPage._Parent = self
        self._ConfirmPage.Init()

        it = {}
        it["key"] = "version"
        it["label"] = "Version"
        it["value"] = config.VERSION
        self._AList["version"] = it
        
        self.GenList()
        
    def CheckUpdate(self):
        self._Screen._MsgBox.SetText("Checking update...")
        self._Screen._MsgBox.Draw()
        self._Screen.SwapAndShow()

        try:
            r = requests.get(config.UPDATE_URL, verify=False, timeout=8)
        except:
            print("requests get error")
            return
        else:
            if r.status_code == requests.codes.ok:
                try:
                    json_ = r.json()

                    if "version" in json_ and "updatepath" in json_ and "md5sum" in json_:
                        if config.VERSION != json_["version"]:
                            
                            self._ConfirmPage._URL = json_["updatepath"]
                            self._ConfirmPage._MD5 = json_["md5sum"]
                            self._ConfirmPage._GIT = False
                            
                            self._Screen.PushPage(self._ConfirmPage)
                            
                            self._Screen.Draw()
                            self._ConfirmPage.SnapMsg("Confirm Update to %s ?" % json_["version"] )
                            self._Screen.SwapAndShow()
                            
                    elif "gitversion" in json_: ### just use git to  run update
                        cur_dir = os.getcwd()
                        os.chdir("/home/cpi/apps/launcher")
                        current_git_version = get_git_revision_short_hash()
                        current_git_version = current_git_version.strip("\n")
                        current_git_version = current_git_version.strip("\t")
                        os.chdir(cur_dir)
                        if current_git_version != json_["gitversion"]:
                            self._ConfirmPage._URL = None
                            self._ConfirmPage._MD5 = None
                            self._ConfirmPage._GIT = True
                            self._ConfirmPage._Version = json_["gitversion"]
                            
                            self._Screen.PushPage(self._ConfirmPage)
                            
                            self._Screen.Draw()
                            self._ConfirmPage.SnapMsg("Update to %s ?" % json_["gitversion"] )
                            self._Screen.SwapAndShow()
                        else:
                            self._Screen.Draw()
                            self._Screen._MsgBox.SetText("Launcher is up to date")
                            self._Screen._MsgBox.Draw()
                            self._Screen.SwapAndShow()
                            pygame.time.delay(765)
                            
                    return True
                except Exception, e:
                    print("r.json() error %s" % str(e))
                
            else:
                print(" requests get error %d ", r.status_code)
                    

        return False
    
    def OnLoadCb(self):
        pass

    def KeyDown(self,event):
        if event.key == CurKeys["Menu"] or event.key == CurKeys["A"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["X"]:
            if is_wifi_connected_now():
                if self.CheckUpdate() == True:
                    self._Screen.Draw()
                    self._Screen.SwapAndShow()
                else:
                    self._Screen.Draw()
                    self._Screen._MsgBox.SetText("Checking update failed")
                    self._Screen._MsgBox.Draw()
                    self._Screen.SwapAndShow()
            else:
                self._Screen.Draw()
                self._Screen._MsgBox.SetText("Please Check your Wi-Fi connection")
                self._Screen._MsgBox.Draw()
                self._Screen.SwapAndShow()

    def Draw(self):
        self.ClearCanvas()
#        self._Ps.Draw()

        for i in self._MyList:
            i.Draw()
        
    
class APIOBJ(object):

    _UpdatePage = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._UpdatePage = UpdatePage()

        self._UpdatePage._Screen = main_screen
        self._UpdatePage._Name ="Update"
        self._UpdatePage.Init()
        
    def API(self,main_screen):
        if main_screen !=None:
            main_screen.PushPage(self._UpdatePage)
            main_screen.Draw()
            main_screen.SwapAndShow()
    


OBJ = APIOBJ()
def Init(main_screen):    
    OBJ.Init(main_screen)
def API(main_screen):
    OBJ.API(main_screen)
    
        
