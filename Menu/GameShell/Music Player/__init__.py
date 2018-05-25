# -*- coding: utf-8 -*- 

import pygame
from pygame.locals import *
from sys import exit
import os
import sys

from datetime import datetime

import base64
from beeprint import pp


## local UI import
import pages
import myvars
from icons import preload

def Init(main_screen):
    pages.InitPoller()

    preload.load_icons()
    pages.InitListPage(main_screen)
    pages.InitMusicLibPage(main_screen)
    pages.InitSpectrumPage(main_screen)
    
def API(main_screen):
    
    if main_screen !=None:
        main_screen.PushCurPage()
        main_screen.SetCurPage(myvars.PlayListPage)
        main_screen.Draw()
        main_screen.SwapAndShow()


