# -*- coding: utf-8 -*- 

import pygame

#UI lib
from UI.constants    import RUNSYS
from UI.keys_def     import CurKeys, IsKeyStartOrA, IsKeyMenuOrB
from UI.confirm_page import ConfirmPage
from UI.lang_manager import MyLangManager
from UI.skin_manager import MySkinManager

class YesCancelConfirmPage(ConfirmPage):
    
    _ConfirmText = MyLangManager.Tr("Awaiting Input")
    _FootMsg = ["Nav","","","Cancel","Yes"]
    _StartOrA_Event = None
    _Key_X_Event = None
    _Key_Y_Event = None

    def KeyDown(self,event):
        
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if IsKeyStartOrA(event.key):
            if self._StartOrA_Event != None:
                if callable( self._StartOrA_Event):
                    self._StartOrA_Event()
                    self.ReturnToUpLevelPage()

        if event.key == CurKeys["X"]:
            if self._Key_X_Event != None:
                if callable( self._Key_X_Event):
                    self._Key_X_Event()
                    self.ReturnToUpLevelPage()

        if event.key == CurKeys["Y"]:
            if self._Key_Y_Event != None:
                if callable( self._Key_Y_Event):
                    self._Key_Y_Event()
                    self.ReturnToUpLevelPage()

