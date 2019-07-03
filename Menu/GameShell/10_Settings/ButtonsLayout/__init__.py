# -*- coding: utf-8 -*-

import pygame
import commands
import shutil
import os

from libs.roundrects import aa_round_rect
from UI.constants import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys, GetButtonsLayoutMode, SetButtonsLayoutMode, IsKeyStartOrA, IsKeyMenuOrB
from UI.scroller   import ListScroller
from UI.icon_pool  import MyIconPool
from UI.icon_item  import IconItem
from UI.multi_icon_item import MultiIconItem
from UI.multilabel import MultiLabel
from UI.confirm_page import ConfirmPage

class UpdateConfirmPage(ConfirmPage):
    _ConfirmText = "Apply to RetroArch?"
    _RetroArchConf = "/home/cpi/.config/retroarch/retroarch.cfg"
    _LayoutMode = "Unknown"

    def ModifyRetroArchConf(self,keys):

        try:
            with open(self._RetroArchConf, mode="r") as f:
                confarr = f.readlines()
        except:
            return "retroarch.cfg cannot open."

        bka = bkb = bkx = bky = False
        try:
            for i, ln in enumerate(confarr):
                lnk = ln.split("=")[0].strip()
                if lnk == "input_player1_a":
                    confarr[i] = "input_player1_a = \"" + keys[0] + "\"\n"
                    bka = True
                if lnk == "input_player1_b":
                    confarr[i] = "input_player1_b = \"" + keys[1] + "\"\n"
                    bkb = True
                if lnk == "input_player1_x":
                    confarr[i] = "input_player1_x = \"" + keys[2] + "\"\n"
                    bkx = True
                if lnk == "input_player1_y":
                    confarr[i] = "input_player1_y = \"" + keys[3] + "\"\n"
                    bky = True
        except:
            return "retroarch.cfg cannot parse."

        if bka and bkb and bkx and bky:
            None
        else:
            return "retroarch.cfg validation error."

        try:
            with open(self._RetroArchConf, mode="w") as f:
                confarr = f.writelines(confarr)
        except:
            return "retroarch.cfg cannot write."

        return "Completed! Your RA keymap: " + self._LayoutMode.upper()

    def KeyDown(self,event):

        def finalizeWithDialog(msg):
            self._Screen._MsgBox.SetText(msg)
            self._Screen._MsgBox.Draw()
            self._Screen.SwapAndShow()
            return

        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if IsKeyStartOrA(event.key):

            if self._LayoutMode == "xbox":
                keymap = ["j","k","u","i"]
            elif self._LayoutMode == "snes":
                keymap = ["k","j","i","u"]
            else:
                finalizeWithDialog("Internal error.")
                return
            print("mode: " + self._LayoutMode)

            if not os.path.isfile(self._RetroArchConf):
                finalizeWithDialog("retroarch.cfg was not found.")
                return

            try:
                shutil.copyfile(self._RetroArchConf, self._RetroArchConf + ".blbak")
            except:
                finalizeWithDialog("Cannot create .blbak")
                return

            finalizeWithDialog(self.ModifyRetroArchConf(keymap))
            return

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

class ButtonsLayoutPage(Page):
    _FootMsg =  ["Nav.","","UpdateRetroArch","Back","Toggle"]
    _MyList = []

    _AList = {}

    _Scrolled = 0

    _BGwidth = 320
    _BGheight = 240-24-20

    _DrawOnce = False
    _Scroller = None
    _ConfirmPage = None

    _EasingDur = 30

    _dialog_index = 0

    def __init__(self):
        Page.__init__(self)
        self._Icons = {}

    def GenList(self):

        self._MyList = []



    def Init(self):
        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._HWND = self._Screen._CanvasHWND
                self._CanvasHWND = pygame.Surface( (self._Screen._Width,self._BGheight) )

        self._PosX = self._Index*self._Screen._Width
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height

        DialogBoxs = MultiIconItem()
        DialogBoxs._ImgSurf = MyIconPool.GiveIconSurface("buttonslayout")
        DialogBoxs._MyType = ICON_TYPES["STAT"]
        DialogBoxs._Parent = self
        DialogBoxs._IconWidth = 300
        DialogBoxs._IconHeight = 150
        DialogBoxs.Adjust(0,0,134,372,0)
        self._Icons["DialogBoxs"] = DialogBoxs

        self.GenList()
        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = self._Width - 10
        self._Scroller._PosY = 2
        self._Scroller.Init()
        self._Scroller.SetCanvasHWND(self._HWND)

        self._ConfirmPage = UpdateConfirmPage()
        self._ConfirmPage._LayoutMode = GetButtonsLayoutMode()
        self._ConfirmPage._Screen = self._Screen
        self._ConfirmPage._Name  = "Overwrite RA conf"
        self._ConfirmPage._Parent = self
        self._ConfirmPage.Init()


    def ScrollDown(self):
        dis = 10
        if abs(self._Scrolled) <  (self._BGheight - self._Height)/2 + 0:
            self._PosY -= dis
            self._Scrolled -= dis

    def ScrollUp(self):
        dis = 10
        if self._PosY < 0:
            self._PosY += dis
            self._Scrolled += dis

    def ToggleMode(self):

        if GetButtonsLayoutMode() == "xbox":
            SetButtonsLayoutMode("snes")

            self._dialog_index = 1
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        else:
            SetButtonsLayoutMode("xbox")

            self._dialog_index = 0
            self._Screen.Draw()
            self._Screen.SwapAndShow()

    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self._DrawOnce = False

        self._dialog_index = 0 if GetButtonsLayoutMode() == "xbox" else 1

    def OnReturnBackCb(self):
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()

    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if IsKeyStartOrA(event.key):
            self.ToggleMode()

        if event.key == CurKeys["X"]:
            self._ConfirmPage._LayoutMode = GetButtonsLayoutMode()
            self._Screen.PushPage(self._ConfirmPage)
            self._Screen.Draw()
            self._Screen.SwapAndShow()

    def Draw(self):
        self.ClearCanvas()

        self._Icons["DialogBoxs"].NewCoord(0,30)
        self._Icons["DialogBoxs"]._IconIndex = self._dialog_index
        self._Icons["DialogBoxs"].DrawTopLeft()

        if self._HWND != None:
            self._HWND.fill((255,255,255))
            self._HWND.blit(self._CanvasHWND,(self._PosX,self._PosY,self._Width, self._Height ) )

class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = ButtonsLayoutPage()
        self._Page._Screen = main_screen
        self._Page._Name ="Buttons Layout"
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

