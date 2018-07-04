# -*- coding: utf-8 -*- 

import pygame
from pygame.locals import *
from sys import exit
import os
import sys

from datetime import datetime

import base64
from beeprint import pp


Width = 320
Height = 240
bg_color =  pygame.Color(255,255,255)

icon_width  = 80
icon_height = 80
icon_ext = ".sh"


ICON_TYPES={"Emulator":7,"FILE":6,"STAT":5,"NAV":4,"LETTER":3,"FUNC":2,"DIR":1,"EXE":0,"None":-1} # FUNC is like UI widget's function,DIR contains child page,EXE just execute a binary

## H=horizontal  ,V=vertical S=Single Line
#SLeft start from left, single line
#SCenter star from center ,single line
ALIGN = {"HLeft":0,"HCenter":1,"HRight":2,"VMiddle":3,"SLeft":4,"VCenter":5,"SCenter":6}

DT = pygame.time.Clock().tick(30)   # fps in ms,eg:50


GMEVT = pygame.USEREVENT+1
update_titlebar_event = pygame.event.Event(GMEVT, message="titlebar")

RUNEVT = pygame.USEREVENT+2
RUNSYS = pygame.USEREVENT+3


LOWLIGHT = pygame.USEREVENT+4 ## when dim screen backlight

FOOTMSG = pygame.USEREVENT+5 ## when dim screen backlight


