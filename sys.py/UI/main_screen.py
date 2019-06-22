# -*- coding: utf-8 -*- 

import pygame
from pygame.locals import *
from sys import exit
import os
import sys
import json
from operator import itemgetter

from libs import easing
from datetime import datetime

from beeprint import pp

## local package import
from constants   import ICON_TYPES,icon_ext,icon_width,icon_height,RUNEVT
from icon_item   import IconItem
from page        import Page,PageStack
from title_bar   import TitleBar
from foot_bar    import FootBar
from constants   import Width,Height
from util_funcs  import midRect,FileExists,ReplaceSuffix,ReadTheFileContent,CmdClean,MakeExecutable
from keys_def    import CurKeys
from label       import Label
from untitled_icon import UntitledIcon
from Emulator    import MyEmulator
from CommercialSoftwarePackage import MyCommercialSoftwarePackage

from skin_manager import MySkinManager
from lang_manager import MyLangManager
from widget       import Widget

from counter_screen import CounterScreen

class MessageBox(Label):
    _Parent = None
    
    def __init__(self):
        pass
    
    def Init(self,text,font_obj,color=MySkinManager.GiveColor('Text')):
        self._Color = color
        self._FontObj = font_obj
        self._Text = text

        self._Width = 0
        self._Height = 0
        self._CanvasHWND = pygame.Surface( ( int(self._Parent._Width),int(self._Parent._Height)))
        self._HWND       = self._Parent._CanvasHWND

    def SetText(self,text):
        self._Text = MyLangManager.Tr(text)

    def PreDraw(self):
        self._Width = 0
        self._Height = 0
        self._CanvasHWND.fill(MySkinManager.GiveColor('White'))
        
        words = self._Text.split(' ')
        space = self._FontObj.size(' ')[0]
        max_width = self._Parent._Width-40
        x ,y = (0,0)
        row_total_width = 0
        lines = 0

        for word in words:
            word_surface = self._FontObj.render(word, True, self._Color)
            word_width = word_surface.get_width()
            word_height = word_surface.get_height()
            row_total_width += word_width
            if lines == 0:
                lines += word_height
            if row_total_width+space  >= max_width:
                x = 0  # Reset the x.
                y += word_height  # Start on new row.
                row_total_width = word_width
                
                lines += word_height
                
            self._CanvasHWND.blit(word_surface, (x, y))
            
            if len(words) == 1: # single line 
                x += word_width
            else:
                x += word_width + space
            
            if x > self._Width:
                self._Width = x

            if lines >= (self._Parent._Height - 40):
                break
        
        self._Height = lines
        
    def DrawWith(self, x_,y_, withborder):
        
        self.PreDraw()

        x_ = x_ - self._Width/2
        y_ = y_ - self._Height/2
        
        padding = 5
       
        pygame.draw.rect(self._HWND,MySkinManager.GiveColor('White'),(x_-padding,y_-padding, self._Width+padding*2,self._Height+padding*2))        
    
        if self._HWND != None:
            rect = pygame.Rect(x_,y_,self._Width,self._Height)
            self._HWND.blit(self._CanvasHWND,rect,(0,0,self._Width,self._Height))
            #self._HWND.blit(self._CanvasHWND,rect)

        if withborder == True:
            pygame.draw.rect(self._HWND,MySkinManager.GiveColor('Black'),(x_-padding,y_-padding, self._Width+padding*2,self._Height+padding*2),1)
        
    def Draw(self):        
        x = (self._Parent._Width)/2
        y = (self._Parent._Height)/2
        
        self.DrawWith(x,y,True)
        

python_package_flag = "__init__.py"
emulator_flag       = "action.config"
commercialsoftware_flag = "compkginfo.json" 

##Abstract object for manage Pages ,not the pygame's physic screen
class MainScreen(Widget):
    _Pages = []
    _PageMax = 0
    _PageIndex = 0
    _PosY  = TitleBar._BarHeight+1
    _Width = Width 
    _Height = Height -FootBar._BarHeight -TitleBar._BarHeight
    _MyPageStack = None
    _CurrentPage = None # pointer to the current displaying Page Class
    _CanvasHWND  = None
    _HWND        = None
    _TitleBar    = None
    _FootBar     = None
    _MsgBox      = None
    _MsgBoxFont  = MyLangManager.TrFont("veramono20")
    _IconFont    = MyLangManager.TrFont("varela15")
    _SkinManager = None

    _Closed      = False
    _CounterScreen = None
    
    _LastKey = -1
    _LastKeyDown = -1
    
    def __init__(self):
        self._Pages = []
        self._MyPageStack = PageStack()

    def Init(self):
        self._CanvasHWND = pygame.Surface((self._Width,self._Height))
        self._MsgBox= MessageBox()
        self._MsgBox._Parent= self
        self._MsgBox.Init(" ", self._MsgBoxFont)

        self._SkinManager = MySkinManager
    
        self._CounterScreen = CounterScreen()
        self._CounterScreen._HWND = self._HWND
        
        self._CounterScreen.Init()

        
    def FartherPages(self):
        self._PageMax = len(self._Pages)
        for i in range(0,self._PageMax):
            self._Pages[i]._Index = i
            self._Pages[i]._CanvasHWND = self._CanvasHWND
            self._Pages[i]._IconNumbers = len(self._Pages[i]._Icons)
            self._Pages[i]._Screen = self
            self._Pages[i].Adjust()
            
            if self._Pages[i]._IconNumbers > 1:
                self._Pages[i]._PsIndex = 1
                self._Pages[i]._IconIndex = self._Pages[i]._PsIndex
            
                
        self._CurrentPage = self._Pages[self._PageIndex]
        self._CurrentPage._OnShow = True

    def GetMyRightSidePage(self):
        ret = self._PageIndex +1
        if ret > (self._PageMax -1):
            ret = self._PageMax -1
        return ret
    
    def PageMoveLeft(self):
        self._Pages[self._PageIndex]._OnShow = False
        if self._PageIndex < (self._PageMax - 1):
            my_right_side_page  = self.GetMyRightSidePage()
            for i in range(0,self._PageMax):
                if i!= self._PageIndex and i != my_right_side_page:
                    self._Pages[i].MoveLeft(Width)

            self._Pages[self._PageIndex].EasingLeft(Width)

            if self._PageIndex != my_right_side_page:
                self._Pages[my_right_side_page].EasingLeft(Width)

            self._Pages[self._PageIndex].ResetPageSelector()
            
        self._PageIndex+=1
        if self._PageIndex > (self._PageMax -1):
            self._PageIndex = (self._PageMax -1)

        self._Pages[self._PageIndex]._OnShow = True
        self._CurrentPage = self._Pages[self._PageIndex]

    def GetMyLeftSidePage(self):
        ret = self._PageIndex -1
        if ret < 0:
            ret = 0
        return ret

    def PageMoveRight(self):
        self._Pages[self._PageIndex]._OnShow = False
        if self._PageIndex > 0:
            my_left_side_page = self.GetMyLeftSidePage()
            for i in range(0,self._PageMax):
                if i!= self._PageIndex and i!= my_left_side_page:
                    pass
                #self._Pages[i].MoveRight(Width)

            self._Pages[self._PageIndex].EasingRight(Width)

            if self._PageIndex != my_left_side_page:
                self._Pages[my_left_side_page].EasingRight(Width)

            self._Pages[self._PageIndex].ResetPageSelector()

        self._PageIndex-=1
        if self._PageIndex < 0:
            self._PageIndex = 0

        self._Pages[self._PageIndex]._OnShow = True
        self._CurrentPage = self._Pages[self._PageIndex]


    def EasingAllPageLeft(self):
        current_time = 0.0
        start_posx = 0.0
        current_posx = start_posx
        final_posx   = float(Width)
        posx_init    = 0
        dur          = 30
        last_posx    = 0.0
        all_last_posx = []
        if self._PageIndex >= (self._PageMax - 1):
            return
        for i in range(0,Width*dur):
            current_posx = easing.SineIn(current_time,start_posx,final_posx-start_posx,float(dur))
            if current_posx >= final_posx:
                current_posx = final_posx

            dx  = current_posx - last_posx
            all_last_posx.append(int(dx))
            current_time+=1
            last_posx = current_posx
            if current_posx >= final_posx:
                break

        c = 0
        for i in all_last_posx:
            c+=i
        if c < final_posx - start_posx:
            all_last_posx.append( final_posx - c )

        for i in all_last_posx:
            self.ClearCanvas()
            for j in self._Pages:
                j._PosX -= i
                j.DrawIcons()
                j._Screen.SwapAndShow()
                
        
        self._Pages[self._PageIndex]._OnShow = False

        self._PageIndex+=1
        if self._PageIndex > (self._PageMax -1):
            self._PageIndex = (self._PageMax -1)

        self._Pages[self._PageIndex]._OnShow = True
        self._CurrentPage = self._Pages[self._PageIndex]
        
    def EasingAllPageRight(self):
        current_time = 0.0
        start_posx = 0.0
        current_posx = start_posx
        final_posx   = float(Width)
        posx_init    = 0
        dur          = 30
        last_posx    = 0.0
        all_last_posx = []
        if self._PageIndex <= 0:
            return
        for i in range(0,Width*dur):
            current_posx = easing.SineIn(current_time,start_posx,final_posx-start_posx,float(dur))
            if current_posx >= final_posx:
                current_posx = final_posx

            dx  = current_posx - last_posx
            all_last_posx.append(int(dx))
            current_time+=1
            last_posx = current_posx
            if current_posx >= final_posx:
                break

        c = 0
        for i in all_last_posx:
            c+=i
        if c < final_posx - start_posx:
            all_last_posx.append( final_posx - c )

        for i in all_last_posx:
            self.ClearCanvas()
            for j in reversed(self._Pages):
                j._PosX += i
                j.DrawIcons()
                j._Screen.SwapAndShow()
                
        
        self._Pages[self._PageIndex]._OnShow = False
        
        self._PageIndex-=1
        if self._PageIndex < 0:
            self._PageIndex = 0

        self._Pages[self._PageIndex]._OnShow = True
        self._CurrentPage = self._Pages[self._PageIndex]

    def CurPage(self):
        return self._CurrentPage
    
    def PushCurPage(self):
        self._MyPageStack.Push(self._CurrentPage)
        
    def SetCurPage(self,page):
        self._CurrentPage = page
        on_load_cb = getattr(self._CurrentPage,"OnLoadCb",None)
        if on_load_cb != None:
            if callable( on_load_cb ):
                self._CurrentPage.OnLoadCb()

    def PushPage(self,page):
        self.PushCurPage()
        self.SetCurPage(page)
        
    def AppendPage(self,Page):
        self._Pages.append(Page)

    def ClearCanvas(self):
        self._CanvasHWND.fill(self._SkinManager.GiveColor('White'))
        
    def SwapAndShow(self):
        if self._Closed == True:
            return
        if self._HWND != None:
            self._HWND.blit(self._CanvasHWND,(self._PosX,self._PosY,self._Width,self._Height))
            pygame.display.update()
            
    def ExtraName(self,name):
        ## extra name like 1_xxx to be => xxx, 
        parts = name.split("_")
        if len(parts) > 1:
            return parts[1]
        elif len(parts) == 1:
            return parts[0]
        else:
            return name

    def IsExecPackage(self,dirname):
        files = os.listdir(dirname)
        bname = os.path.basename(dirname)
        bname = self.ExtraName(bname)
        for i in sorted(files):
            if i == bname+".sh":
                return True
        return False
    
    def IsEmulatorPackage(self,dirname):
        files = os.listdir(dirname)
        for i in sorted(files):
            if i.endswith(emulator_flag):
                return True
        return False
        
    def IsCommercialPackage(self,dirname):
        files = os.listdir(dirname)
        for i in sorted(files):
            if i.endswith(commercialsoftware_flag):
                return True
        return False
            
    def IsPythonPackage(self,dirname):
        files = os.listdir(dirname)
        for i in sorted(files):
            if i.endswith(python_package_flag):
                return True
        return False
    
    def ReunionPagesIcons(self): #This is for combining /home/cpi/apps/Menu and ~/launcher/Menu/GameShell 
        for p in self._Pages:
            tmp = []
            for i,x in enumerate(p._Icons):
                tup = ('',0)
                if hasattr(x, '_FileName'):
                    if str.find(x._FileName,"_") < 0:
                        tup = ("98_"+x._FileName,i) # prefer to maintain PowerOFF in last position if the filename has no order labels
                    else:
                        tup = (x._FileName, i)
                else:
                    tup = ("",i)
                
                tmp.append(tup)
            tmp = sorted(tmp, key=itemgetter(0))
            
            retro_games_idx = []
            retro_games_dir = "20_Retro Games"
            for i,x in enumerate(tmp):
                if retro_games_dir in x[0]:
                    retro_games_idx.append(x[1])
            
            if len(retro_games_idx) > 1:
                for i in range(1,len(retro_games_idx)):
                    p._Icons[retro_games_idx[0]]._LinkPage._Icons.extend( p._Icons[retro_games_idx[i]]._LinkPage._Icons) ### assumes the folder of ~/apps/Menu/20_Retro Games is legalzip","sfc"],
                
            
                tmp_swap = []
                for i, x in enumerate(tmp):
                    if retro_games_dir not in x[0]:
                        tmp_swap.append(x)
                    if retro_games_dir in x[0] and i == retro_games_idx[0]:
                        tmp_swap.append(x)
                
                tmp = tmp_swap
            
            #print(tmp)
            new_icons = []
            for x in tmp:
                new_icons.append( p._Icons[ x[1] ] )
            p._Icons = new_icons
    
    
    def ReadTheDirIntoPages(self,_dir,pglevel,cur_page):
        global commercialsoftware_flag
        
        if FileExists(_dir) == False and os.path.isdir(_dir) == False:
            return
        
        files = os.listdir(_dir)
        for i in sorted(files):
            if os.path.isdir(_dir+"/"+i): # TOPLEVEL only is dir
                if pglevel == 0:
                    page = Page()
                    page._Name = self.ExtraName(i)
                    page._Icons = []
                    self._Pages.append(page)
                    self.ReadTheDirIntoPages(_dir+"/"+i, pglevel+1 ,self._Pages[ len(self._Pages) -1])
                else: ## On CurPage now
                    i2 = self.ExtraName(i)
                    iconitem = IconItem()
                    iconitem._FileName = i
                    iconitem._CmdPath = ""
                    iconitem.AddLabel(MyLangManager.Tr(i2),self._IconFont)
                    if FileExists( _dir+"/"+i+"/"+i2+".png"): ### 20_Prog/Prog.png , cut 20_ 
                        iconitem._ImageName = _dir+"/"+i+"/"+i2+".png"
                    elif FileExists( MySkinManager.GiveIcon(_dir+"/"+i2+".png") ):
                        iconitem._ImageName = MySkinManager.GiveIcon(_dir+"/"+i2+".png")
                    else:
                        untitled = UntitledIcon()
                        untitled.Init()
                        if len(i2) > 1:
                            untitled.SetWords(i2[:2])
                        elif len(i2) == 1:
                            untitled.SetWords([i2[0],i2[0]])
                        else:
                            untitled.SetWords(["G","s"])
                    
                        iconitem._ImgSurf = untitled.Surface()
                        iconitem._ImageName = ""
                        
                    if self.IsPythonPackage(_dir+"/"+i):
                        iconitem._MyType  = ICON_TYPES["FUNC"]
                        sys.path.append(_dir)
                        iconitem._CmdPath = __import__(i)
                        init_cb  = getattr(iconitem._CmdPath,"Init",None)
                        if init_cb != None:
                            if callable(init_cb):
                                iconitem._CmdPath.Init(self)
                                cur_page._Icons.append(iconitem)

                    elif self.IsEmulatorPackage(_dir+"/"+i):
                        obj = {}
                        obj["ROM"] = ""
                        obj["ROM_SO"] =""
                        obj["EXT"]    = []
                        obj["EXCLUDE"] = []
                        obj["FILETYPE"] = "file"
                        obj["LAUNCHER"] = ""
                        obj["TITLE"]    = "Game"
                        obj["SO_URL"]   = ""
                        obj["RETRO_CONFIG"] = "" ## 
                        try:
                            f = open(_dir+"/"+i+"/"+emulator_flag)
                        except IOError:
                            print("action config open failed")
                            return
                        else:
                            with f:
                                content = f.readlines()
                                content = [x.strip() for x in content] 
                        for c in content:
                            pis = c.split("=")
                            if len(pis) > 1:
                                if "EXT" in pis[0]:
                                    obj[pis[0]] = pis[1].split(",")
                                elif "EXCLUDE" in pis[0]:
                                    obj[pis[0]] = pis[1].split(",")
                                else:
                                    obj[pis[0]] = pis[1]

                        if FileExists(_dir+"/"+i+"/retroarch-local.cfg"):
                            obj["RETRO_CONFIG"] = CmdClean(os.path.abspath( _dir+"/"+i+"/retroarch-local.cfg" ))
                            print("a local retroarch cfg:", obj["RETRO_CONFIG"])
                            
                        em = MyEmulator()
                        em._Emulator = obj
                        
                        em.Init(self)
                        iconitem._CmdPath = em
                        iconitem._MyType  = ICON_TYPES["Emulator"]
                        cur_page._Icons.append(iconitem)

                    elif self.IsCommercialPackage( os.path.join(_dir,i)):
                        data = None
                        em = MyCommercialSoftwarePackage()
                        if FileExists( _dir+"/"+i+"/.done"):
                            print(_dir+"/"+i+"/.done")
                            em._Done = os.path.realpath(_dir+"/"+i+"/"+i2+".sh")
                        else:
                            with open(os.path.join(_dir,i) +"/"+commercialsoftware_flag) as f:
                                data = json.load(f)
                            em._ComPkgInfo = data
                            em._Done = ""
                        
                        em._InvokeDir = os.path.realpath( os.path.join(_dir,i))
                        em.Init(self)
                        
                        iconitem._CmdPath = em
                        iconitem._MyType  = ICON_TYPES["Commercial"]
                        cur_page._Icons.append(iconitem)
                        
                    elif self.IsExecPackage(_dir+"/"+i): ## ExecPackage is the last one to check
                        iconitem._MyType  = ICON_TYPES["EXE"]                        
                        iconitem._CmdPath = os.path.realpath(_dir+"/"+i+"/"+i2+".sh")
                        MakeExecutable(iconitem._CmdPath)
                        cur_page._Icons.append(iconitem)                    
                    else:                            
                        iconitem._MyType  = ICON_TYPES["DIR"]
                        iconitem._LinkPage = Page()
                        iconitem._LinkPage._Name = i2
                        cur_page._Icons.append(iconitem)
                        self.ReadTheDirIntoPages(_dir+"/"+i,pglevel+1,iconitem._LinkPage)
                        
            elif os.path.isfile(_dir+"/"+i) and pglevel > 0:
                if i.lower().endswith(icon_ext):
                    i2 = self.ExtraName(i)
                    
                    #cmd      =  ReadTheFileContent(_dir+"/"+i)
                    iconitem = IconItem()
                    iconitem._FileName = i
                    iconitem._CmdPath = os.path.realpath(_dir+"/"+i)
                    MakeExecutable(iconitem._CmdPath)
                    iconitem._MyType  = ICON_TYPES["EXE"]
                    if FileExists( MySkinManager.GiveIcon( _dir+"/"+ReplaceSuffix(i2,"png"))):
                        iconitem._ImageName = MySkinManager.GiveIcon(_dir+"/"+ReplaceSuffix(i2,"png"))
                    else:
                        untitled = UntitledIcon()
                        untitled.Init()
                        if len(i2) > 1:
                            untitled.SetWords(i2[:2])
                        elif len(i2) == 1:
                            untitled.SetWords([i2[0],i2[0]])                            
                        else:
                            untitled.SetWords(["G","s"])
                        
                        iconitem._ImgSurf = untitled.Surface()
                        
                        iconitem._ImageName = ""
                        
                    iconitem.AddLabel(MyLangManager.Tr(i2.split(".")[0]),self._IconFont)
                    iconitem._LinkPage = None
                    cur_page._Icons.append(iconitem)

    def RunEXE(self,cmdpath):
        self.DrawRun()
        self.SwapAndShow()
        pygame.time.delay(1000)
        cmdpath = cmdpath.strip()
        cmdpath = CmdClean(cmdpath)
        pygame.event.post( pygame.event.Event(RUNEVT, message=cmdpath))

    def OnExitCb(self,event):
        ## leave rest to Pages
        on_exit_cb = getattr(self._CurrentPage,"OnExitCb",None)
        if on_exit_cb != None:
            if callable( on_exit_cb ):
                self._CurrentPage.OnExitCb(event)
        return

    def KeyDown(self,event):
        """
        if event.key == pygame.K_PAGEUP:
            self.EasingAllPageLeft()
            #self.SwapAndShow()
        if event.key == pygame.K_PAGEDOWN:
            self.EasingAllPageRight()
            #self.SwapAndShow()
        """
        
        if event.key == pygame.K_t:
            self.DrawRun()
            self.SwapAndShow()
        
        """
        if event.key == CurKeys["Space"]:
            self._CounterScreen.Draw()
            self._CounterScreen.SwapAndShow()
            self._CounterScreen.StartCounter()
        """ 
        ## leave rest to Pages
        current_page_key_down_cb = getattr(self._CurrentPage,"KeyDown",None)
        if current_page_key_down_cb != None:
            if callable( current_page_key_down_cb ):
                self._CurrentPage.KeyDown(event)
                
        self._LastKey = event.key
        
    def DrawRun(self):
        self._MsgBox.SetText(MyLangManager.Tr("Launching"))
        self._MsgBox.Draw()
    
    def Draw(self):
        if self._Closed == True:
            return
        
        self._CurrentPage.Draw()
        #if self._HWND != None:
        #    self._HWND.blit(self._CanvasHWND,(self._PosX,self._PosY,self._Width,self._Height))
        if self._TitleBar != None:
            self._TitleBar.Draw(self._CurrentPage._Name)
        if self._FootBar  != None:
            if hasattr(self._CurrentPage,"_FootMsg"):
                self._FootBar.SetLabelTexts(self._CurrentPage._FootMsg)
                self._FootBar.Draw()

