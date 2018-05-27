
# -*- coding: utf-8 -*- 

import os
import pygame

import glob
import shutil
import gobject
import validators
#from pySmartDL import SmartDL

from libs.roundrects import aa_round_rect

from UI.confirm_page import ConfirmPage
from UI.download_process_page import DownloadProcessPage
from UI.keys_def   import CurKeys
from UI.fonts  import fonts
from UI.multilabel import MultiLabel

import config

class RomSoConfirmPage(ConfirmPage):
    _ListFont = fonts["veramono18"]

    _ConfirmText = "Do you want to setup this game engine automatically?"

    _MyDownloadPage = None
    
    def CheckBattery(self):
        try:
            f = open(config.Battery)
        except IOError:
            print( "RomSoConfirmPage open %s failed" % config.Battery)
            return 6
        else:
            with f:
                bat_uevent = {}
                content = f.readlines()
                content = [x.strip() for x in content]
                for i in content:
                    pis = i.split("=")
                    if len(pis) > 1:
                        bat_uevent[pis[0]] = pis[1]

                if "POWER_SUPPLY_CAPACITY" in bat_uevent:
                    cur_cap = int(bat_uevent["POWER_SUPPLY_CAPACITY"])
                else:
                    cur_cap = 0
                
                return cur_cap
                    
        return 0

    def Init(self):
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height

        self._CanvasHWND = self._Screen._CanvasHWND

        li = MultiLabel()
        li.SetCanvasHWND(self._CanvasHWND)
        li._Width = 160
        li.Init(self._ConfirmText,self._ListFont)
        
        li._PosX = (self._Width - li._Width)/2
        li._PosY = (self._Height - li._Height)/2

        self._BGPosX = li._PosX-20
        self._BGPosY = li._PosY-20
        self._BGWidth = li._Width+40
        self._BGHeight = li._Height+40
        
        self._MyList.append(li)
        
    def SnapMsg(self,msg):
        self._MyList[0].SetText(msg)
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        self._MyList[0].SetText(self._ConfirmText)

    def OnReturnBackCb(self):
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
    
    def KeyDown(self,event):    
        if event.key == CurKeys["Menu"] or event.key == CurKeys["A"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["B"]:
            if self.CheckBattery() < 5:
                self.SnapMsg("Battery must over 5%")
            else:
                if self._MyDownloadPage == None:
                    self._MyDownloadPage = DownloadProcessPage()
                    self._MyDownloadPage._Screen = self._Screen
                    self._MyDownloadPage._Name = "Downloading..."
                    self._MyDownloadPage.Init()
                
                self._Screen.PushPage(self._MyDownloadPage)
                self._Screen.Draw()
                self._Screen.SwapAndShow()

                if config.CurKeySet == "PC":
                    so_url = self._Parent._Emulator["SO_URL"] ## [rom/fav]_list_page is _Parent
                    so_url = so_url.replace("armhf","x86_64")
                    print(so_url)
                    self._MyDownloadPage.StartDownload(so_url,os.path.dirname(self._Parent._Emulator["ROM_SO"]))
                else:
                    self._MyDownloadPage.StartDownload(self._Parent._Emulator["SO_URL"],
                                                       os.path.dirname(self._Parent._Emulator["ROM_SO"]))
            

    def Draw(self):
        self.ClearCanvas()
        self.DrawBG()
        for i in self._MyList:
            i.Draw()
