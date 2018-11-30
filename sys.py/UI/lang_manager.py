# -*- coding: utf-8 -*-

import pygame
import config
import ConfigParser

class CaseConfigParser(ConfigParser.SafeConfigParser):
    def optionxform(self, optionstr):
        return optionstr

class LangManager(object):
    """
    """
    
    _Langs = {}
    _EngLangs = {} ##default Language dict,must be correct
    _Config = None
    _ConfigFileName = "English.ini"
    
    def __init__(self):
        self.Init()
    
    def Init(self):
        if not LangManager._Colors:
            self.SetLangs()

    def SetLangs(self):
        Langs = {}

        SkinManager._Colors = Colors

        self._Config = CaseConfigParser()

        fname = ".lang"
        
        
        
        try:
            self._Config.read(fname)
        except Exception, e:
            print("read skin config.cfg error %s" % str(e))
            return
        else:
            if "Colors" in self._Config.sections():
                colour_opts = self._Config.options("Colors")
#                print(colour_opts)
                for i in SkinManager._Colors:
                    if i in colour_opts:
                        try:
                            SkinManager._Colors[i] = self.ConvertToRGB(
                                self._Config.get("Colors", i))
                        except Exception, e:
                            print("error in ConvertToRGB %s" % str(e))
                            continue
    
    def Tr(self,english_key_str):
        if english_key_str in SkinManager._Langs:
            return SkinManager._Langs[english_key_str]
        else:
            return SkinManager._EngLangs[english_key_str] ##default from english dict
    

##global MyLangManager Handler
MyLangManager = None

def InitMyLangManager():
    global MySkinManager
    if MyLangManager == None:
        MyLangManager = LangManager()
    

InitMyLangManager()
