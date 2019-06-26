# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from sys import exit
import os
import sys

import config
from config import CurKeySet ## read only

def GetButtonsLayoutMode():
    lm = "xbox"
    try:
        with open(".buttonslayout", "r") as f:
            lm = f.read()
    except:
        None
    if lm not in ["xbox","snes"]:
        lm = "xbox"
    return lm

def SetButtonsLayoutMode(mode):
    SetXYABButtons(mode)
    with open(".buttonslayout", "w") as f:
        f.write(mode)
    config.ButtonsLayout = mode

def SetXYABButtons(mode):
    if mode == "snes":
        GameShell["Y"] = pygame.K_u
        GameShell["X"] = pygame.K_i
        GameShell["B"] = pygame.K_j
        GameShell["A"] = pygame.K_k
    else:
        GameShell["X"] = pygame.K_u
        GameShell["Y"] = pygame.K_i
        GameShell["A"] = pygame.K_j
        GameShell["B"] = pygame.K_k


GameShell = {}
GameShell["Up"]   = pygame.K_UP
GameShell["Down"] = pygame.K_DOWN
GameShell["Left"] = pygame.K_LEFT
GameShell["Right"]= pygame.K_RIGHT

GameShell["Menu"] = pygame.K_ESCAPE

SetXYABButtons(GetButtonsLayoutMode())

GameShell["Select"] = pygame.K_SPACE
GameShell["Start"] = pygame.K_RETURN

GameShell["LK1"] = pygame.K_h
GameShell["LK5"] = pygame.K_l

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
PC["Select"] = pygame.K_SPACE
PC["Start"] = pygame.K_s

PC["LK1"] = pygame.K_h
PC["LK5"] = pygame.K_l

if CurKeySet == "PC":
    CurKeys = PC
else:
    CurKeys = GameShell


def IsKeyStartOrA(key):
    return key == CurKeys["Start"] or key == CurKeys["A"]

def IsKeyMenuOrB(key):
    return key == CurKeys["Menu"] or key == CurKeys["B"]
