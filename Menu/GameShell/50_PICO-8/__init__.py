# -*- coding: utf-8 -*- 
import pygame
import validators

from UI.constants import Width,Height,ICON_TYPES,RUNEVT
#from UI.simple_name_space import SimpleNamespace
from UI.page  import Page
from UI.label  import Label
from UI.fonts  import fonts
from UI.icon_item import IconItem
from UI.icon_pool import MyIconPool
from UI.keys_def  import CurKeys
from UI.skin_manager import MySkinManager
from UI.lang_manager import MyLangManager
from UI.textarea     import Textarea
from UI.widget     import Widget

from UI.util_funcs import FileExists

from libs.roundrects import aa_round_rect

class Word:
    _T = ""
    _Color = MySkinManager.GiveColor('Text') ## default text color
    _FontObj = MyLangManager.TrFont("varela12") ##default font
    _Size = 12
    _Bold = False
    _UndLine = False
    def SetColor(self,color):
        self._Color = color
    
    def GetColor(self):
        return self._Color
    
    def SetFont(self,fnt):
        self._FontObj = fnt
    
    def SetBold(self,bd):
        self._Bold = bd
    
    def SetUnderLine(self,bd):
        self._UndLine = bd
    
    def __init__(self,v=""):
        self._T = v 
    
    def __str__(self):
        return self._T

    def __unicode__(self):
        return self._T.encode("utf-8")

    def __add__(self,a):
        return self._T + a 
        
    def __repr__(self):
        return self._T
    
    def __len__(self):
        return len(self._T)

    def __eq__(self, other):
        return self._T == other
    
    def FnHeight(self):
        return self._FontObj.get_height()
    
    def Render(self):
        self._FontObj.set_bold(self._Bold)
        self._FontObj.set_underline(self._UndLine)
        
        sur = self._FontObj.render(self._T,True,self._Color)
        
        self._FontObj.set_bold(False)
        self._FontObj.set_underline(False)       
        return sur

class Text:
    _Words = []
    def __init__(self,content="",color=None,fnt=None,Bold=False,Und=False):
        self._Words = [ Word(x) for x in list(content) ]
        if color != None:
            self.SetColor(color)
        if fnt != None:
            self.SetFont(fnt)
        
        if Bold == True:
            self.SetBold(True)
        if Und == True:
            self.SetUnderLine(True)
        
    def SetColor(self,color):
        if len(self._Words) > 0:
            for i,x in enumerate(self._Words):
                self._Words[i].SetColor(color)
    
    def SetBold(self,bd):
        if len(self._Words) > 0:
            for i,x in enumerate(self._Words):
                self._Words[i].SetBold(bd)
                
    def SetUnderLine(self,bd):
        if len(self._Words) > 0:
            for i,x in enumerate(self._Words):
                self._Words[i].SetUnderLine(bd)
                    
    def SetFont(self,fnt):
        if len(self._Words) > 0:
            for i,x in enumerate(self._Words):
                self._Words[i].SetFont(fnt)
                
    def __add__(self,a):
        return self._Words+a.Words()
    
    def Words(self):
        return self._Words

class Textbulletinboard(Textarea):
    _TextLimit   = 200
    _BackgroundColor = MySkinManager.GiveColor("White")
    _Align = "Left" ## Left or Center
    
    def SetAndBlitText(self,words):# words => []
        
        if self._TextFull != True:            
            self._MyWords = words
            #self.BlitText()
            self._TextIndex = len(self._MyWords)
        else:
            print("is Full %s" % "".join(str(self._MyWords)))
               
    def BuildBlitText(self):
        blit_rows = [[]]
        w = 0
        xmargin = 5
        endmargin = 15
        x = self._PosX+xmargin
        linenumber = 0
        cursor_row = 0

        for i, v in enumerate(self._MyWords):
            if str(v) == "\n":
                w = 0
                x = self._PosX+xmargin
                linenumber+=1
                blit_rows.append([])               
            else:
                t = v.Render()
                t_width = t.get_width()
                w += t_width
                del(t)
            
                blit_rows[linenumber].append(v)

                if i == self._TextIndex - 1:
                    cursor_row = linenumber

                if w + t_width >= self._Width-endmargin:
                    x = self._PosX+xmargin
                    w = 0
                    linenumber += 1
                    blit_rows.append([])
        
        
        self._BlitWords = blit_rows
        self._BlitIndex = self._TextIndex
        
    def BlitText(self):
        # build up blitwords
        self.BuildBlitText()
        xmargin = 5
        endmargin = 5
        start_x = self._PosX+xmargin ##start_point_x
        start_y = self._PosY ## start_point_y       
        x = self._PosX+xmargin ##start_point_x
        y = self._PosY ## start_point_y
        
        self._TextFull = len(self._MyWords) > self._TextLimit
        last_height = 0
        
        for row_idx, row in enumerate(self._BlitWords):
                            
            if len(row) == 0:
                y = y + 16
                w = 0
                continue
                
            else:
                total_row_width = 0
                for i,v in enumerate(row):
                    t = v.Render()
                    total_row_width += t.get_width() 
                    if total_row_width > self._Width-endmargin:
                        total_row_width = self._Width
                        start_x = self._PosX + xmargin
                        break
                    else:
                        if self._Align == "Center":
                            start_x = (self._Width - total_row_width)/2                            
        
            last_height = 0
            total_row_width = 0
            x = start_x
            for i,v in enumerate(row):
                t = v.Render()
                total_row_width += t.get_width()
                
                if last_height < v.FnHeight():
                    last_height = v.FnHeight()
                    
                if total_row_width > self._Width-endmargin:
                    x = start_x
                    y = y + last_height 
                    total_row_width = 0
            
                self._CanvasHWND.blit(t, (x,y))
                x += t.get_width()
            
            y = y + last_height              
            
    def Draw(self):
        #aa_round_rect(self._CanvasHWND, (4,24.5+6,312,60),self._BackgroundColor,4,0,self._BackgroundColor)

        aa_round_rect(self._CanvasHWND,  
                    (self._PosX,self._PosY,self._Width,self._Height),self._BackgroundColor,4,0,self._BackgroundColor)
        
        self.BlitText()    
        

class NOPICOPage(Page):
    _FootMsg =  ["Nav","","","Back",""]
    
    def Init(self):
        self._PosX = self._Index*self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height
        
        self._CanvasHWND = self._Screen._CanvasHWND
        
        self._Board = Textbulletinboard()
        
        self._Board._PosX = 4
        self._Board._PosY = 20
        self._Board._Width= self._Width - 4*2
        self._Board._Height = 100
        self._Board._CanvasHWND = self._CanvasHWND
        self._Board.Init()
        
        a = Text("Please Go to \n",None,MyLangManager.TrFont("varela14"),True)
        b = Text("https://www.lexaloffle.com/pico-8.php",MySkinManager.GiveColor("URL"),None,True,True)
        c = Text("buy a pico-8 raspi")
        
        d = a.Words()+b.Words()+c.Words()
        self._Board.SetAndBlitText(d)
        
    def KeyDown(self,event):
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            return   
    
    def Draw(self):
        self.ClearCanvas()
        self._Board.Draw()
  

class PICO8ZipHashErrPage(Page):
    _FootMsg =  ["Nav","","","Cancel","Continue"]
    
    def Init(self):
        self._PosX = self._Index*self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height
        
        self._CanvasHWND = self._Screen._CanvasHWND
        
        self._Board = Textbulletinboard()
        
        self._Board._PosX = 4
        self._Board._PosY = self._Height/2 - 35
        self._Board._Width= self._Width - 4*2
        self._Board._Height = 100
        self._Board._CanvasHWND = self._CanvasHWND
        self._Board._Align = "Center"
        self._Board.Init()
        
        a = Text("Zip md5sum error\n",None,MyLangManager.TrFont("varela24"))
        b = Text("Continue anyway?\n",None,MyLangManager.TrFont("varela24"))
        
        self._Board.SetAndBlitText(a.Words()+b.Words())
        
    def KeyDown(self,event):
        if event.key == CurKeys["A"] or event.key == CurKeys["Menu"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            return   
    
    def Draw(self):
        self.ClearCanvas()
        self._Board.Draw()


class APIOBJ(object):

    _Page = None
    _PICO8 ="/home/cpi/games/PICO-8"
    _pico8 ="/home/cpi/games/PICO-8/pico-8"
    
    def __init__(self):
        pass
        
    def CheckPico8(self):
        if FileExists(self._PICO8) and FileExists(self._pico8):
            return True
    
    def Init(self,main_screen):
        self._NOPicoPage = NOPICOPage()
        self._NOPicoPage._Name = "No Pico8"
        self._NOPicoPage._Screen = main_screen
        self._NOPicoPage.Init()
        
        self._HashErrPage = PICO8ZipHashErrPage()
        self._HashErrPage._Name = "Md5sum failed"
        self._HashErrPage._Screen = main_screen
        self._HashErrPage.Init()
                
    def API(self,main_screen):
        if main_screen !=None:
            if self.CheckPico8() == False:
                main_screen._MsgBox.SetText("Starting pico-8")
                main_screen._MsgBox.Draw()
                main_screen.SwapAndShow()
                pygame.time.delay(300)
                cmdpath = "/home/cpi/games/PICO-8/PICO-8.sh"
                pygame.event.post( pygame.event.Event(RUNEVT, message=cmdpath))
            else:
                main_screen.PushPage(self._NOPicoPage)
                #main_screen.PushPage(self._HashErrPage)
                main_screen.Draw()
                main_screen.SwapAndShow()

OBJ = APIOBJ()
def Init(main_screen):    
    OBJ.Init(main_screen)
def API(main_screen):
    OBJ.API(main_screen)
