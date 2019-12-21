# -*- coding: utf-8 -*-

import pygame
import config
import ConfigParser

from util_funcs  import FileExists

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
    _Fonts = {}
    DefaultSkin = "../skin/default"

    def __init__(self):
        self.Init()
    
    def configExists(self):
        if FileExists(config.SKIN+"/config.ini"):
            self._Config = CaseConfigParser()
            fname = config.SKIN+"/config.ini"        
            try:
                return self._Config.read(fname)
            except Exception, e:
                print("skin config.ini read error %s" % str(e))
                return
        else:
            print("no skin config.ini file to read")
            return

    def ConvertToRGB(self,hexstr):
        h = hexstr.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
    
    def Init(self):
        if not SkinManager._Colors:
            self.SetColors()
        if not SkinManager._Fonts:
            self.SetFonts()
    
    def SetFonts(self):          
        if not pygame.font.get_init():
            pygame.font.init()
        
        skinpath = config.SKIN+"/truetype"
        fonts_path = {}
        fonts_path["varela"]   = "%s/VarelaRound-Regular.ttf" % skinpath
        fonts_path["veramono"] = "%s/VeraMono.ttf" % skinpath
        fonts_path["noto"]     = "%s/NotoSansMono-Regular.ttf" % skinpath
        fonts_path["notocjk"]     = "%s/NotoSansCJK-Regular.ttf" % skinpath
        
        if self.configExists():
            if "Font_Paths" in self._Config.sections():
                font_opts = self._Config.options("Font_Paths")
                for i in fonts_path:
                    if i in font_opts:
                        try:
                            fonts_path[i] = skinpath+"/"+self._Config.get("Font_Paths", i)+".ttf"
                        except Exception, e:
                            print("error in Font_Paths %s" % str(e))
                            continue
        
        for i in range(10,29):
          self._Fonts["varela%d"%i] = pygame.font.Font(fonts_path["varela"],i)
          
        self._Fonts["varela34"] = pygame.font.Font(fonts_path["varela"],34)
        self._Fonts["varela40"] = pygame.font.Font(fonts_path["varela"],40)
        self._Fonts["varela120"] = pygame.font.Font(fonts_path["varela"],120)
        
        for i in range(10,26):
            self._Fonts["veramono%d"%i] = pygame.font.Font(fonts_path["veramono"],i)
        
        for i in range(10,28):
            self._Fonts["notosansmono%d"%i] = pygame.font.Font(fonts_path["noto"],i)

        for i in range(10,28):
            self._Fonts["notosanscjk%d"%i] = pygame.font.Font(fonts_path["notocjk"],i)
    
        self._Fonts["arial"] = pygame.font.SysFont("arial",16)
        
    def SetColors(self):
        Colors = {}
        Colors["High"] = pygame.Color(51, 166, 255)
        Colors["Text"] = pygame.Color(83, 83, 83)
        Colors["ReadOnlyText"] = pygame.Color(130,130,130)
        Colors["Front"] = pygame.Color(131, 199, 219)
        Colors["URL"] = pygame.Color(51, 166, 255)
        Colors["Line"] = pygame.Color(169, 169, 169)
        Colors["TitleBg"] = pygame.Color(228, 228, 228)
        Colors["Active"] = pygame.Color(175, 90, 0)
        Colors["Disabled"] = pygame.Color(204, 204, 204)
        Colors["White"] = pygame.Color(255, 255, 255)
        Colors["Black"] = pygame.Color(0, 0, 0)

        if self.configExists():
            if "Colors" in self._Config.sections():
                colour_opts = self._Config.options("Colors")
                for i in Colors:
                    if i in colour_opts:
                        try:
                            Colors[i] = self.ConvertToRGB(
                                self._Config.get("Colors", i))
                        except Exception, e:
                            print("error in ConvertToRGB %s" % str(e))
                            continue
        
        SkinManager._Colors = Colors
    
    def GiveFont(self,name):
        return SkinManager._Fonts[name]
        
    def GiveColor(self,name):
        if name in SkinManager._Colors:
            return SkinManager._Colors[name]
        else:
            return  pygame.Color(255,0,0)
    
    def GiveIcon(self,orig_file_or_dir): ## return is string,not Surface
        #doing a wrapper for items under /home/cpi/apps/Menu/*, to be like Menu/GameShell/*
        if orig_file_or_dir.startswith("/home/cpi/apps/Menu"):
            orig_file_or_dir = orig_file_or_dir.replace("/home/cpi/apps/Menu/","../Menu/GameShell/")
    
        if orig_file_or_dir.startswith(".."):
            ret  = orig_file_or_dir.replace("..",config.SKIN)
            if FileExists(ret) == False:
                ret = orig_file_or_dir.replace("..",self.DefaultSkin)
        else:
            ret = config.SKIN+"/sys.py/"+orig_file_or_dir
            if FileExists(ret) == False:
                ret = self.DefaultSkin+"/sys.py/"+orig_file_or_dir
    
        if FileExists( ret ):
            return ret
        else:  ## if not existed both in default or custom skin ,return where it is
            return orig_file_or_dir
            
    def GiveWallpaper(self,png_name):
        #first SKIN/wallpapers/xxxx.png
        #second ../skin/default/wallpapers/xxxx.png
        #finnal gameshell/wallpaper/xxxx.png
        #loading.png,seeyou.png,updating.png,gameover.png,desktopbg.png
        wlp = "/wallpaper/"
        if FileExists(config.SKIN+wlp+png_name):
            return config.SKIN+wlp+png_name
        elif FileExists(self.DefaultSkin+wlp+png_name):
            return self.DefaultSkin+wlp+png_name
        else:
            return "gameshell/wallpaper/"+png_name
            
        
            
##global MySkinManager Handler
MySkinManager = None

def InitMySkinManager():
    global MySkinManager
    if MySkinManager == None:
        MySkinManager = SkinManager()
    

InitMySkinManager()
