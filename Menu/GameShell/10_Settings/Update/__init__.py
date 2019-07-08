# -*- coding: utf-8 -*- 

import pygame
import os
import requests
import validators
import gobject


## local UI import
from UI.page  import Page
from UI.constants import ICON_TYPES,Width,Height,RUNEVT,RUNSH
from UI.icon_item import IconItem
from UI.icon_pool import MyIconPool
from UI.label  import Label
from UI.util_funcs import midRect,CmdClean,get_git_revision_short_hash
from UI.keys_def import CurKeys, IsKeyStartOrA, IsKeyMenuOrB
from UI.confirm_page import ConfirmPage
from UI.download     import Download
from UI.download_process_page import DownloadProcessPage
from UI.skin_manager import MySkinManager
from UI.lang_manager import MyLangManager

from UI.info_page_list_item import InfoPageListItem

from libs.roundrects import aa_round_rect
from libs.DBUS       import is_wifi_connected_now

import config

LauncherLoc = "/home/cpi/launcher"

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
                        cmdpath = "tar zxf " + CmdClean(filename) + " -C /home/cpi/ ;rm -rf "+ filename
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
                    
                    self._Screen._MsgBox.SetText("DownloadFailed")
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
        global LauncherLoc
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
        if IsKeyStartOrA(event.key):
            if self._GIT == True:
                cmdpath = "%s/update.sh %s" % (LauncherLoc,self._Version)
                pygame.event.post( pygame.event.Event(RUNSH, message=cmdpath))
                return
            
            if self._DownloadPage == None:
                self._DownloadPage = UpdateDownloadPage()
                self._DownloadPage._Screen = self._Screen
                self._DownloadPage._Name   = "Downloading"
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


class UpdatePage(Page):
    _Icons = {}
    _FootMsg = ["Nav","","Check Update","Back",""]

    _ListFontObj = MyLangManager.TrFont("varela15")    
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
            li._Fonts["small"] = MySkinManager.GiveFont("varela12")
            
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
        global LauncherLoc
        self._Screen._MsgBox.SetText("CheckingUpdate")
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
                            self._ConfirmPage.SnapMsg(MyLangManager.Tr("ConfirmUpdateToFQ") % json_["version"] )
                            self._Screen.SwapAndShow()
                            
                    elif "gitversion" in json_: ### just use git to  run update
                        cur_dir = os.getcwd()
                        os.chdir(LauncherLoc)
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
                            self._ConfirmPage.SnapMsg(MyLangManager.Tr("UpdateToFQ") % json_["gitversion"] )
                            self._Screen.SwapAndShow()
                        else:
                            self._Screen.Draw()
                            self._Screen._MsgBox.SetText("LauncherIsUpToDate")
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
        if IsKeyMenuOrB(event.key):
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
                    self._Screen._MsgBox.SetText("CheckingUpdateFailed")
                    self._Screen._MsgBox.Draw()
                    self._Screen.SwapAndShow()
            else:
                self._Screen.Draw()
                self._Screen._MsgBox.SetText("CheckWifiConnection")
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
        self._UpdatePage._Name = "Update Launcher"
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
    
        
