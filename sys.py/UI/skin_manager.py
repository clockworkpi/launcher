# -*- coding: utf-8 -*-

import pygame
import config
import ConfigParser

class CaseConfigParser(ConfigParser.SafeConfigParser):
    def optionxform(self, optionstr):
        return optionstr

class SkinManager(object):
    """
    _HighColor = pygame.Color(51,166,255) # #33a6ff
    _TextColor = pygame.Color(83,83,83) # #535353
    _FrontColor = pygame.Color(131,199,219) ## light blue,#83c7db
    _URLColor  = pygame.Color(51,166,255) ## blue more #33a6ff
    _LineColor = pygame.Color(169,169,169)  # #a9a9a9
    _TitleBgColor = pygame.Color(228,228,228)  # #e4e4e4
    _ActiveColor = pygame.Color(175,90,0) ## light brown  #af5a00
    """
    
    _Colors = {}
    _Config = None
    
    def __init__(self):
        pass

    def ConvertToRGB(self,hexstr):
        
        h = hexstr.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
    
    def Init(self):
        
        Colors = {}
        Colors["High"] = pygame.Color(51,166,255) 
        Colors["Text"] = pygame.Color(83,83,83)
        Colors["Front"] =  pygame.Color(131,199,219)
        Colors["URL"]   = pygame.Color(51,166,255)
        Colors["Line"]  =  pygame.Color(169,169,169)
        Colors["TitleBg"] = pygame.Color(228,228,228)
        Colors["Active"]  =  pygame.Color(175,90,0)
        Colors["White"]  = pygame.Color(255,255,255)
        
        self._Colors = Colors
        
        self._Config = CaseConfigParser()
        
        fname = "../skin/"+config.SKIN+"/config.cfg"
        
        try:
            self._Config.read(fname)
        except Exception,e:
            print("read skin config.cfg error %s" % str(e))
            return
        else:
            if "Colors" in self._Config.sections():
                colour_opts = self._Config.options("Colors")
#                print(colour_opts)
                for i in self._Colors:
                    if i in colour_opts:
                        try:
                            self._Colors[i] = self.ConvertToRGB(self._Config.get("Colors",i))
                        except Exception,e:
                            print("error in ConvertToRGB %s" % str(e))
                            continue

    
    def GiveColor(self,name):
        if name in self._Colors:
            return self._Colors[name]
        else:
            return  pygame.Color(255,0,0)
    
