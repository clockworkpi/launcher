# -*- coding: utf-8 -*- 

import pygame
from pygame.locals import *
from sys import exit
import os
import sys

from datetime import datetime

import base64
from beeprint import pp

from util_funcs  import midRect,SkinMap
from fonts       import fonts

BlankPng = SkinMap("gameshell/blank.png")  ## 80x80
## use blank circle as bg, Two alpha As Icon Label
#Upper and Lower
class UntitledIcon(object):
    _PosX = 0
    _PosY = 0
    _Width = 80
    _Height = 80
    
    _Words = ["G","s"]
    _FontObj= fonts["varela40"]
    
    _BG     = None  ## initial surface 

    _Color  = pygame.Color(83,83,83)

    
    def __init__(self):
        self._Words = ["G","s"]

    def Init(self):
        self._BG = pygame.image.load(BlankPng).convert_alpha()


    def SetWords(self,TwoWords):
        if len(TwoWords) == 1:
            self._Words[0] = TwoWords[0].upper()

        if len(TwoWords) == 2:
            self._Words[0] = TwoWords[0].upper()
            self._Words[1] = TwoWords[1].lower()

        self._Text = self._FontObj.render("".join(self._Words),True,self._Color)
        
    def Draw(self):
        if self._BG != None:
            w_ = self._Text.get_width()
            h_ = self._Text.get_height()
            
            self._BG.blit(self._Text,midRect(self._Width/2,self._Height/2,w_,h_,self._Width,self._Height))

    def Surface(self):
        self.Draw()

        return self._BG

    
