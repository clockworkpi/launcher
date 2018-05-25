# -*- coding: utf-8 -*- 
import os
import pygame

import gobject
import validators


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
from UI.download   import Download

from libs.DBUS     import is_wifi_connected_now

import config

class DownloadProcessPage(Page):
    _FootMsg = ["Nav.","","","Back",""]
    _Downloader = None
    _DownloaderTimer = -1
    _Value = 0

    _URL = ""
    _DST_DIR = ""

    _PngSize = {}

    _FileNameLabel = None
    _SizeLabel     = None

    _URLColor  = pygame.Color(51,166,255)
    _TextColor = pygame.Color(83,83,83)
    
    def __init__(self):
        Page.__init__(self)        
        self._Icons = {}
        self._CanvasHWND = None
        
    def Init(self):
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height

        self._CanvasHWND = self._Screen._CanvasHWND

        self._PngSize["bg"] = (48,79)
        self._PngSize["needwifi_bg"] = (253,132)
        
        bgpng = IconItem()
        bgpng._ImgSurf = MyIconPool._Icons["rom_download"]
        bgpng._MyType = ICON_TYPES["STAT"]
        bgpng._Parent = self
        bgpng.Adjust(0,0,self._PngSize["bg"][0],self._PngSize["bg"][1],0)
        self._Icons["bg"] = bgpng

        needwifi_bg = IconItem()
        needwifi_bg._ImgSurf = MyIconPool._Icons["needwifi_bg"]
        needwifi_bg._MyType = ICON_TYPES["STAT"]
        needwifi_bg._Parent = self
        needwifi_bg.Adjust(0,0,self._PngSize["needwifi_bg"][0],self._PngSize["needwifi_bg"][1],0)

        self._Icons["needwifi_bg"] = needwifi_bg

        
        self._FileNameLabel = Label()
        self._FileNameLabel.SetCanvasHWND(self._CanvasHWND)
        self._FileNameLabel.Init("", fonts["varela12"])

        self._SizeLabel = Label()
        self._SizeLabel.SetCanvasHWND(self._CanvasHWND)
        self._SizeLabel.Init("0/0Kb",fonts["varela12"])
        self._SizeLabel.SetColor( self._URLColor )

        
    def OnExitCb(self,event):
        print("DownloadProcessPage OnExitCb")
        if self._Downloader == None:
            return        
        try:
            self._Downloader.stop()
        except:
            pass
        return
    
    def GObjectUpdateProcessInterval(self):
        if self._Screen.CurPage() == self:
            if self._Downloader.isFinished():
                if self._Downloader.isSuccessful():
                    print("Success!")
                    # Do something with obj.get_dest()
                    filename = os.path.basename(self._Downloader.get_dest())
                    cur_dir = os.getcwd()
                    
                    if filename.endswith(".zip"):
                        os.chdir(self._DST_DIR)
                        os.system( "unzip " + filename )
                    
                    elif filename.endswith(".zsync"):
                        os.chdir(self._DST_DIR)
                        os.system( "rm -rf " + filename)
                        
                    elif filename.endswith(".tar.xz"):                    
                        os.chdir(self._DST_DIR)
                        os.system( "tar xf " + filename)
                        os.system( "rm -rf " + filename)
                    
                    os.chdir(cur_dir)    
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
                    
                    self._Screen._MsgBox.SetText("Download failed")
                    self._Screen._MsgBox.Draw()
                    self._Screen.SwapAndShow()
                    return False
            else:
                self._Value =  self._Downloader.get_progress()

                filename = os.path.basename(self._Downloader.get_dest())
                self._FileNameLabel.SetText( filename )

                downloaded = self._Downloader.progress["downloaded"]
                total      = self._Downloader.progress["total"]

                downloaded = downloaded/1000.0/1000.0
                total      = total/1000.0/1000.0
                
                self._SizeLabel.SetText( "%.2f" % downloaded+"/"+ "%.2f" % total +"Mb")
                
                print("Progress: %d%%" % (self._Value))
                self._Screen.Draw()
                self._Screen.SwapAndShow()
                return True
        else:
            return False
    
    def StartDownload(self,url,dst_dir):
        if is_wifi_connected_now() == False:
            return
        
        if validators.url(url) and os.path.isdir(dst_dir):
            self._URL = url
            self._DST_DIR = dst_dir
        else:
            self._Screen._MsgBox.SetText("Invaid")
            self._Screen._MsgBox.Draw()
            self._Screen.SwapAndShow()            
            print("url or dst dir error")
            return
        
        self._Downloader = Download(url,dst_dir,None)
        self._Downloader.start()
        
        self._DownloaderTimer = gobject.timeout_add(100, self.GObjectUpdateProcessInterval)
        
    def KeyDown(self,event):
        if event.key == CurKeys["Menu"] or event.key == CurKeys["A"]:
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
            
    def Draw(self):
        self.ClearCanvas()

        if is_wifi_connected_now() == False:
            self._Icons["needwifi_bg"].NewCoord(self._Width/2, self._Height/2)
            self._Icons["needwifi_bg"].Draw()
            return
        
        self._Icons["bg"].NewCoord(self._Width/2,self._Height/2-20)
        self._Icons["bg"].Draw()
        
        percent = self._Value
        if percent < 10:
            percent = 10

        
        rect_ = midRect(self._Width/2,self._Height/2+33,170,17, Width,Height)
        aa_round_rect(self._CanvasHWND,rect_, (238,238,238),5,0,(238,238,238))
        
        rect2 = midRect(self._Width/2,self._Height/2+33,int(170*(percent/100.0)),17, Width,Height)
        rect2.left = rect_.left
        rect2.top  = rect_.top
        aa_round_rect(self._CanvasHWND,rect2, (126,206,244),5,0,(126,206,244))

        rect3 = midRect(self._Width/2,self._Height/2+53,self._FileNameLabel._Width, self._FileNameLabel._Height,Width,Height)

        rect4 = midRect(self._Width/2,self._Height/2+70,self._SizeLabel._Width, self._SizeLabel._Height,Width,Height)

        self._FileNameLabel.NewCoord(rect3.left,rect3.top)
        self._SizeLabel.NewCoord(rect4.left, rect4.top)

        self._FileNameLabel.Draw()
        self._SizeLabel.Draw()
        
        
