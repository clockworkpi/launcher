# -*- coding: utf-8 -*-
import os
import pygame
import config
import ConfigParser
from skin_manager import MySkinManager
from util_funcs  import FileExists

class CaseConfigParser(ConfigParser.SafeConfigParser):
    def optionxform(self, optionstr):
        return optionstr

class LangManager(object):
    """
    """
    
    _Langs = {}
    _Config = None
    _ConfigFileName = "00_English.ini" ## double % to escape 
    _CJKMode = False
    
    def __init__(self):
        self.Init()
    
    def Init(self):
        if not self._Langs:
            self.SetLangs()
    
    def UpdateLang(self):
        self._Langs = {}
        self.SetLangs()
    
    def IsCJKMode(self):## in MultiLabel, latins seped by white spaces,CJK no needs for that
        latins = ["English"]
        self._CJKMode = True
        
        for i in latins:
            if i in self._ConfigFileName:
                self._CJKMode= False
                break
        
        return self._CJKMode
        
    def SetLangs(self):
        self._Config = CaseConfigParser()
        #print("SetLangs")
        fname = ".lang"
        
        try:
            with open(fname, "r") as f:
                self._ConfigFileName = f.read()
                self._ConfigFileName = self._ConfigFileName.strip("\r\n ")
                #print(self._ConfigFileName)
        except:
            os.system("touch .lang")
            print("read lang failed")
            None
        
        
        if self._ConfigFileName == "" or FileExists("langs/"+self._ConfigFileName) == False:
            #print("miss file")
            self._ConfigFileName = "00_English.ini"
        else:
            pass
            #print("has file",self._ConfigFileName)
            
        
        try:
            self._Config.read("langs/"+self._ConfigFileName)
        except Exception, e:
            print("read lang ini error %s" % str(e))
            return
        else:
            if "Langs" in self._Config.sections():
                lang_opts = self._Config.options("Langs")
                for i in lang_opts:
                    try:
                        self._Langs[i] = self._Config.get("Langs", i)
                    except Exception, e:
                        print("error %s" % str(e))
                        continue
    
    def Tr(self,english_key_str):
        #print("english_key_str", english_key_str)
        if english_key_str in self._Langs:
            #print( self._Langs[english_key_str]  )
            return self._Langs[english_key_str].decode("utf8")
        else:
            return english_key_str
    
    def TrFont(self,orig_font_str):
        try:
            font_size_number = int(filter(str.isdigit, orig_font_str))
        except TypeError:
            font_size_number = int(filter(unicode.isdigit, orig_font_str))
        if font_size_number > 120:
            raise Exception('font string format error')
            
        if "English.ini" in self._ConfigFileName:
            return MySkinManager.GiveFont(orig_font_str)
        else:
            if font_size_number > 28:
            #    raise Exception('cjk font string format error '+ str(font_size_number))
                return  MySkinManager.GiveFont(orig_font_str)
            else:
                return MySkinManager.GiveFont("notosanscjk%d" % font_size_number)

##global MyLangManager Handler
MyLangManager = None

def InitMyLangManager():
    global MyLangManager
    if MyLangManager == None:
        MyLangManager = LangManager()
    

InitMyLangManager()
