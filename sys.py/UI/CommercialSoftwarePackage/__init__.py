# -*- coding: utf-8 -*- 

"""
Package  /home/cpi/games/xxx/yyy.zip ,only support in zip 

com_pkg_info /home/cpi/launcher/Menu/GameShell/xxxx/compkginfo.json
use https://jsonlint.com/ to validate first in case syntax err

```
{
"NotFoundMsg":["Please Go to \n|None|varela14|True",
"https://www.lexaloffle.com/pico-8.php|URL|None|True|True",
"buy a pico-8 raspi and put zip into \n/home/cpi/games/PICO-8"]

"MD5":{"pico-8_0.1.11g_raspi.zip":"a3f2995cf117499f880bd964d6a0e1f2","pico-8_0.1.11g_amd64.zip":"6726141c784afd4a41be6b7414c1b932"}
}

```

"""

import pygame
#import validators
import os
import commands
from UI.constants import Width,Height,ICON_TYPES,RUNEVT,RESTARTUI
#from UI.simple_name_space import SimpleNamespace
from UI.page  import Page
from UI.label  import Label
from UI.icon_item import IconItem
from UI.icon_pool import MyIconPool
from UI.keys_def  import CurKeys,IsKeyMenuOrB,IsKeyStartOrA
from UI.skin_manager import MySkinManager
from UI.lang_manager import MyLangManager
from UI.text_bulletinboard import Textbulletinboard,Text
from UI.util_funcs import FileExists


class NotFoundPage(Page):
    _FootMsg =  ["Nav","","","Back",""]
    _BG = "pico8_notfound"
    _Leader = None
    _Padding = pygame.Rect(0,12,0,6)    
    def Init(self):
        self._PosX = self._Index*self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height
        
        self._CanvasHWND = self._Screen._CanvasHWND

        self._BGpng = IconItem()
        self._BGpng._ImgSurf = MyIconPool.GiveIconSurface(self._BG)
        self._BGpng._MyType = ICON_TYPES["STAT"]
        self._BGpng._Parent = self
        #print( MyIconPool.Width(self._BG),MyIconPool.Height(self._BG) )
        self._BGpng.Adjust(0,0,MyIconPool.Width(self._BG),MyIconPool.Height(self._BG),0)
                
        self._Board = Textbulletinboard()
        
        self._Board._PosX = 4
        self._Board._PosY = 100
        self._Board._Width= self._Width - 4*2
        self._Board._Height = 200
        self._Board._CanvasHWND = self._CanvasHWND
        self._Board._Align = "Center"
        self._Board._RowPitch =28
        self._Board.Init()
        
        if self._Leader!= None and self._Leader._ComPkgInfo != None:
            if "NotFoundMsg" in self._Leader._ComPkgInfo:                
                d = []
                for i, v in enumerate(self._Leader._ComPkgInfo["NotFoundMsg"]):
                    Color = None
                    Font = None
                    Bold = False
                    Und  = False
                    Txt = ""
                    parts = v.split("|")
                    if len(parts) > 0:
                        Txt = parts[0]
                        
                    if len(parts) == 2:
                        if parts[1] != "None":
                            Color = MySkinManager.GiveColor(parts[1])
                    elif len(parts) == 3:
                        if parts[1] != "None":
                            Color = MySkinManager.GiveColor(parts[1])
                        if parts[2] != "None":
                            Font = MyLangManager.TrFont(parts[2])
                    elif len(parts) == 4:
                        if parts[1] != "None":
                            Color = MySkinManager.GiveColor(parts[1])
                        if parts[2] != "None":
                            Font = MyLangManager.TrFont(parts[2])
                        if parts[3] == "True":
                            Bold = True
                    elif len(parts) == 5:
                        if parts[1] != "None":
                            Color = MySkinManager.GiveColor(parts[1])
                        if parts[2] != "None":
                            Font = MyLangManager.TrFont(parts[2])
                        if parts[3] == "True":
                            Bold = True                        
                        if parts[4] == "True":
                            Und = True
                    
                    a = Text(Txt,Color,Font,Bold,Und)
                    d = d + a.Words()
        
                self._Board.SetAndBlitText(d)
        
    def KeyDown(self,event):
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            return   
    
    def Draw(self):
        self.ClearCanvas()
        if self._BGpng != None:
            self._BGpng.NewCoord((self._Width-self._BGpng._Width)/2,self._Padding.y )
            self._BGpng.DrawTopLeft()
            self._Board._PosY = self._BGpng._Height+self._Padding.y+self._Padding.h
        else:
            self._Board._PosY = self._Padding.y
        
        self._Board.Draw()
  

class HashErrPage(Page):
    _FootMsg =  ["Nav","","","Cancel","Continue"]
    _BG ="pico8_md5_err"
    
    _Leader = None
    _Padding = pygame.Rect(0,12,0,6)
    
    def Init(self):
        self._PosX = self._Index*self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height
        
        self._CanvasHWND = self._Screen._CanvasHWND
        
        self._BGpng = IconItem()
        self._BGpng._ImgSurf = MyIconPool.GiveIconSurface(self._BG)
        self._BGpng._MyType = ICON_TYPES["STAT"]
        self._BGpng._Parent = self
        self._BGpng.Adjust(0,0,MyIconPool.Width(self._BG),MyIconPool.Height(self._BG),0)
        
        self._Board = Textbulletinboard()
        
        self._Board._PosX = 4
        self._Board._PosY = self._Height/2 - 30
        self._Board._Width= self._Width - 4*2
        self._Board._Height = 100
        self._Board._CanvasHWND = self._CanvasHWND
        self._Board._RowPitch =28
        self._Board._Align = "Center"
        self._Board.Init()

        if self._Leader!= None and self._Leader._ComPkgInfo != None:
            if "HashErrMsg" in self._Leader._ComPkgInfo:                
                d = []
                for i, v in enumerate(self._Leader._ComPkgInfo["HashErrMsg"]):
                    Color = None
                    Font = None
                    Bold = False
                    Und  = False
                    Txt = ""
                    parts = v.split("|")
                    if len(parts) > 0:
                        Txt = parts[0]
                        
                    if len(parts) == 2:
                        if parts[1] != "None":
                            Color = MySkinManager.GiveColor(parts[1])
                    elif len(parts) == 3:
                        if parts[1] != "None":
                            Color = MySkinManager.GiveColor(parts[1])
                        if parts[2] != "None":
                            Font = MyLangManager.TrFont(parts[2])
                    elif len(parts) == 4:
                        if parts[1] != "None":
                            Color = MySkinManager.GiveColor(parts[1])
                        if parts[2] != "None":
                            Font = MyLangManager.TrFont(parts[2])
                        if parts[3] == "True":
                            Bold = True
                    elif len(parts) == 5:
                        if parts[1] != "None":
                            Color = MySkinManager.GiveColor(parts[1])
                        if parts[2] != "None":
                            Font = MyLangManager.TrFont(parts[2])
                        if parts[3] == "True":
                            Bold = True                        
                        if parts[4] == "True":
                            Und = True
                    
                    a = Text(Txt,Color,Font,Bold,Und)
                    d = d + a.Words()
        
                self._Board.SetAndBlitText(d)
        
            else:
                a = Text("MD5 check Failed!\n",None,MyLangManager.TrFont("varela16"))
                b = Text("Do you want to continue?",None,MyLangManager.TrFont("varela16"))
                self._Board.SetAndBlitText(a.Words()+b.Words())
        
    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            return   
            
        if IsKeyStartOrA(event.key):
            self._Leader.InstallPackage(self._Screen)
            return
        
    def OnLoadCb(self):
        pass
    
    def Draw(self):
        self.ClearCanvas()
        if self._BGpng != None:        
            self._BGpng.NewCoord((self._Width-self._BGpng._Width)/2,self._Padding.y)
            self._BGpng.DrawTopLeft()
            self._Board._PosY = self._BGpng._Height+self._Padding.y+self._Padding.h
        else:
            self._Board._PosY = self._Padding.y
            
        self._Board.Draw()


class MyCommercialSoftwarePackage(object):
    _ComPkgInfo = None
    _Done  = ""
    _InvokeDir = ""
    
    def __init__(self):
        pass
    
    def CheckPackage(self,main_screen):##detect zip files
        ret = False
        json_config = self._ComPkgInfo
        if not json_config:
            return ret
        
        cur_dir = os.getcwd()
        
        if FileExists(json_config["GameDir"]):
            os.chdir(json_config["GameDir"])
        else:
            os.system( "mkdir %s" % json_config["GameDir"] )
        
        if "MD5" in json_config:
            for i,v in enumerate(json_config["MD5"]):
                if FileExists(v):
                    ret = True
                    break
        
        os.chdir(cur_dir)
        return ret
                    
    def InstallPackage(self,main_screen):
        main_screen._MsgBox.SetText("Installing the package")
        main_screen._MsgBox.Draw()
        main_screen.SwapAndShow()
        json_config = self._ComPkgInfo
        cur_dir = os.getcwd()
        
        os.chdir(json_config["GameDir"])
        for i,v in enumerate(json_config["MD5"]):
            os.system("unzip -o %s" %v) ## auto overwrite 
        
        if "Post-Up" in json_config:
            if FileExists(self._InvokeDir):
                os.chdir(self._InvokeDir)
            
            os.system(json_config["Post-Up"])
        
        
        os.chdir(cur_dir)
        pygame.time.delay(1000)
        
        main_screen._MsgBox.SetText("Package Installed")
        main_screen._MsgBox.Draw()
        main_screen.SwapAndShow()
        pygame.time.delay(500)
        
        pygame.event.post( pygame.event.Event(RESTARTUI, message=""))
        
    def VerifyPackage(self,main_screen):
        ## do unzip and check md5sum once
        
        main_screen._MsgBox.SetText("Verify the package")
        main_screen._MsgBox.Draw()
        main_screen.SwapAndShow()
        pygame.time.delay(400)
        
        Checked = False
        
        json_config = self._ComPkgInfo
        if json_config == None:
            return
        
        if "MD5" in json_config:
            for i,v in enumerate(json_config["MD5"]):
                #print(i,v)
                if FileExists( os.path.join(json_config["GameDir"], v  )):
                    print( os.path.join(json_config["GameDir"],v  ))
                    out = commands.getstatusoutput("md5sum %s" % os.path.join(json_config["GameDir"],v))
                    ret = out[1]
                    ret = ret.split(" ")
                    print(ret)
                    if ret[0] == json_config["MD5"][v]:
                        print("md5 is ok")
                        Checked = True
                    
                    return Checked
        
        return Checked
    
    def Init(self,main_screen):
        self._Page1 = NotFoundPage()
        self._Page1._Name = "Not Found"
        self._Page1._Screen = main_screen
        self._Page1._Leader = self
        self._Page1.Init()
        
        self._Page2 = HashErrPage()
        self._Page2._Name = "Md5sum check failed"
        self._Page2._Screen = main_screen
        self._Page2._Leader = self
        self._Page2.Init()
    
    
    def API(self,main_screen):
        if main_screen !=None:
            if self._Done != "":
                main_screen._MsgBox.SetText("Starting")
                main_screen._MsgBox.Draw()
                main_screen.SwapAndShow()
                pygame.time.delay(300)
                ####
                
                pygame.event.post( pygame.event.Event(RUNEVT, message=self._Done))
                ####
            else:
                #print(self._ComPkgInfo)
                #if FileExists( os.path.join(self._ComPkgInfo["GameDir"],self._ComPkgInfo["InstallDir"] )) == False:
                if self.CheckPackage(main_screen) == False:
                    main_screen.PushPage(self._Page1)
                    main_screen.Draw()
                    main_screen.SwapAndShow()
                else:
                    if self.VerifyPackage(main_screen) == False:
                        main_screen.PushPage(self._Page2)
                        main_screen.Draw()
                        main_screen.SwapAndShow()
                    else:
                        self.InstallPackage(main_screen)
                
