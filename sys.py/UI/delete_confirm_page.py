# -*- coding: utf-8 -*- 

import pygame
import os
import shutil


#UI lib
from constants import Width,Height,ICON_TYPES
from page   import Page,PageSelector
from label  import Label
from fonts  import fonts
from util_funcs import midRect
from keys_def   import CurKeys
from confirm_page import ConfirmPage

class DeleteConfirmPage(ConfirmPage):

    _FileName     = ""
    _TrashDir     = ""
    _ConfirmText = "Confirm delete?"
    
    def SetTrashDir(self,d):
        self._TrashDir = d
        
        if os.path.isdir(self._TrashDir) == False:
            raise IOError("Trash not existed")
        
    def SetFileName(self,fn):
        self._FileName = fn
        
    def KeyDown(self,event):
        
        if event.key == CurKeys["Menu"] or event.key == CurKeys["A"]:
            
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
                
        
        if event.key == CurKeys["B"]:
            try:
                os.remove(self._TrashDir+"/"+os.path.basename(self._FileName))
            except:
                pass

            try:
                shutil.move(self._FileName, self._TrashDir)
            except shutil.Error as e:
                if "already exists" in str(e):
                        self._Screen._MsgBox.SetText("Already existed")
                else:
                    self._Screen._MsgBox.SetText("Error ")
                
                self._Screen._MsgBox.Draw()
                self._Screen.SwapAndShow()
            else:    
                #self._Screen._MsgBox.SetText("Deleteing..")
                #self._Screen._MsgBox.Draw()
                #self._Screen.SwapAndShow()
                self.SnapMsg("Deleteing....")
                self._Screen.Draw()
                self._Screen.SwapAndShow()
                self.Reset()
                
                pygame.time.delay(300)
                self.ReturnToUpLevelPage()
                self._Screen.Draw()
                self._Screen.SwapAndShow()

            print(self._FileName)

    
