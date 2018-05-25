# -*- coding: utf-8 -*- 

import pygame
from pygame.locals import *
from sys import exit
import os
import sys


## local UI import
from UI.delete_confirm_page import DeleteConfirmPage
from UI.icon_pool           import MyIconPool
from UI.keys_def            import CurKeys

from rom_list_page import RomListPage
from fav_list_page import FavListPage

class FavDeleteConfirmPage(DeleteConfirmPage):
    
    def KeyDown(self,event):
        
        if event.key == CurKeys["Menu"] or event.key == CurKeys["A"]:
            
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
                
        
        if event.key == CurKeys["B"]:
            try:
                #self._FileName
                stats = os.stat(self._FileName)
                os.chown(self._FileName, stats.st_uid,stats.st_uid) ## normally uid and gid should be the same 
            except:
                print("error in FavDeleteConfirmPage chown ")

            self.SnapMsg("Deleteing....")
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            self.Reset()
                
            pygame.time.delay(300)
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

            print(self._FileName)


class MyEmulator(object):

    _Icons = {}
    RomListPage = None
    FavListPage = None
    _Emulator = None
    
    _FavGID = 31415
    _FavGname = "cpifav"
    
    def __init__(self):
        self._Icons = {}

    def load_icons(self):
        """
        basepath = os.path.dirname(os.path.realpath(__file__))
        files = os.listdir(basepath+"/icons")
        for i in files:
            if os.path.isfile(basepath+"/"+i) and i.endswith(".png"):
                keyname = i.split(".")[0]
                self._Icons[keyname] = pygame.image.load(basepath+"/"+i).convert_alpha()
        """
        self._Icons["sys"] = MyIconPool._Icons["sys"]
        
        
    def InitDeleteConfirmPage(self,main_screen):
        self.DeleteConfirmPage = DeleteConfirmPage()
        self.DeleteConfirmPage._Screen = main_screen
        self.DeleteConfirmPage._Name   = "Delete Confirm"
        self.DeleteConfirmPage.Init()

        self.FavDeleteConfirmPage = FavDeleteConfirmPage()
        self.FavDeleteConfirmPage._Screen = main_screen
        self.FavDeleteConfirmPage._Name   = "Delete Confirm"
        self.FavDeleteConfirmPage.Init()
        
    def InitFavListPage(self,main_screen):
        self.FavListPage = FavListPage()
        self.FavListPage._Screen = main_screen
        self.FavListPage._Name   = "Favourite Games"
        self.FavListPage._Emulator = self._Emulator
        self.FavListPage._Parent = self
        
        self.FavListPage.Init()
    
    def InitRomListPage(self,main_screen):
        self.RomListPage = RomListPage()
        self.RomListPage._Screen = main_screen
        self.RomListPage._Name   = self._Emulator["TITLE"]
        self.RomListPage._Emulator = self._Emulator
        self.RomListPage._Parent = self
        self.RomListPage.Init()
    
    def Init(self,main_screen):
        self.load_icons()
        self.InitDeleteConfirmPage(main_screen)    
        self.InitRomListPage(main_screen)
        self.InitFavListPage(main_screen)
    
    def API(self,main_screen):
        if main_screen !=None:
            main_screen.PushCurPage()
            main_screen.SetCurPage(self.RomListPage)
            main_screen.Draw()
            main_screen.SwapAndShow()
