# -*- coding: utf-8 -*- 

import pygame
from pygame.locals import *
from sys import exit
import os
import sys

import config

if not pygame.font.get_init():
    pygame.font.init()


skinpath = "../skin/"+config.SKIN+"/truetype"
fonts_path = {}

fonts_path["varela"]   = "%s/VarelaRound-Regular.ttf" % skinpath
fonts_path["veramono"] = "%s/VeraMono.ttf" % skinpath
fonts_path["noto"]     = "%s/NotoSansMono-Regular.ttf" % skinpath
fonts_path["notocjk"]     = "%s/NotoSansCJK-Regular.ttf" % skinpath

fonts = {}
fonts["varela12"] = pygame.font.Font(fonts_path["varela"],12)
fonts["varela13"] = pygame.font.Font(fonts_path["varela"],13)
fonts["varela14"] = pygame.font.Font(fonts_path["varela"],14)
fonts["varela15"] = pygame.font.Font(fonts_path["varela"],15)

fonts["varela16"] = pygame.font.Font(fonts_path["varela"],16)
fonts["varela18"] = pygame.font.Font(fonts_path["varela"],18)
fonts["varela20"] = pygame.font.Font(fonts_path["varela"],20)
fonts["varela22"] = pygame.font.Font(fonts_path["varela"],22)
fonts["varela23"] = pygame.font.Font(fonts_path["varela"],23)
fonts["varela24"] = pygame.font.Font(fonts_path["varela"],24)
fonts["varela25"] = pygame.font.Font(fonts_path["varela"],25)
fonts["varela26"] = pygame.font.Font(fonts_path["varela"],26)
fonts["varela27"] = pygame.font.Font(fonts_path["varela"],27)
fonts["varela28"] = pygame.font.Font(fonts_path["varela"],28)
fonts["varela34"] = pygame.font.Font(fonts_path["varela"],34)
fonts["varela40"] = pygame.font.Font(fonts_path["varela"],40)
fonts["varela120"] = pygame.font.Font(fonts_path["varela"],120)

fonts["veramono25"] = pygame.font.Font(fonts_path["veramono"],25)
fonts["veramono24"] = pygame.font.Font(fonts_path["veramono"],24)
fonts["veramono23"] = pygame.font.Font(fonts_path["veramono"],23)
fonts["veramono22"] = pygame.font.Font(fonts_path["veramono"],22)
fonts["veramono21"] = pygame.font.Font(fonts_path["veramono"],21)
fonts["veramono20"] = pygame.font.Font(fonts_path["veramono"],20)
fonts["veramono18"] = pygame.font.Font(fonts_path["veramono"],18)
fonts["veramono16"] = pygame.font.Font(fonts_path["veramono"],16)
fonts["veramono15"] = pygame.font.Font(fonts_path["veramono"],15)
fonts["veramono14"] = pygame.font.Font(fonts_path["veramono"],14)
fonts["veramono13"] = pygame.font.Font(fonts_path["veramono"],13)
fonts["veramono12"] = pygame.font.Font(fonts_path["veramono"],12)
fonts["veramono11"] = pygame.font.Font(fonts_path["veramono"],11)
fonts["veramono10"] = pygame.font.Font(fonts_path["veramono"],10)

for i in range(10,18):
    fonts["notosansmono"+str(i)] = pygame.font.Font(fonts_path["noto"],i)

for i in range(10,18):
    fonts["notosanscjk"+str(i)] = pygame.font.Font(fonts_path["notocjk"],i)
    
fonts["arial"] = pygame.font.SysFont("arial",16)

