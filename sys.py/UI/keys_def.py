# -*- coding: utf-8 -*- 

import pygame
from pygame.locals import *
from sys import exit
import os
import sys


from config import CurKeySet

GameShell = {}
"""
GameShell["Up"]   = pygame.K_w
GameShell["Down"] = pygame.K_s
GameShell["Left"] = pygame.K_a
GameShell["Right"]= pygame.K_d
"""
GameShell["Up"]   = pygame.K_UP
GameShell["Down"] = pygame.K_DOWN
GameShell["Left"] = pygame.K_LEFT
GameShell["Right"]= pygame.K_RIGHT

GameShell["Menu"] = pygame.K_ESCAPE
GameShell["X"]    = pygame.K_u
GameShell["Y"]    = pygame.K_i
GameShell["A"]    = pygame.K_j
GameShell["B"]    = pygame.K_k

GameShell["Vol-"] = pygame.K_SPACE
GameShell["Vol+"] = pygame.K_RETURN
GameShell["Space"] = pygame.K_SPACE

GameShell["Enter"] = pygame.K_k
GameShell["Start"] = pygame.K_RETURN


PC = {}

PC["Up"]    = pygame.K_UP
PC["Down"]  = pygame.K_DOWN
PC["Left"]  = pygame.K_LEFT
PC["Right"] = pygame.K_RIGHT
PC["Menu"]  = pygame.K_ESCAPE
PC["X"]     = pygame.K_x
PC["Y"]     = pygame.K_y
PC["A"]     = pygame.K_a
PC["B"]     = pygame.K_b
PC["Vol-"]  = pygame.K_SPACE
PC["Vol+"]  = pygame.K_RETURN
PC["Enter"] = pygame.K_RETURN
PC["Space"] = pygame.K_SPACE
PC["Start"] = pygame.K_s

if CurKeySet == "PC":
    CurKeys = PC
else:
    CurKeys = GameShell
