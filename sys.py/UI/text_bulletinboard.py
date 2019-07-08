# -*- coding: utf-8 -*- 

import pygame
from libs.roundrects import aa_round_rect

## local UI import
from page         import Page,PageStack,PageSelector
from label        import Label
from skin_manager import MySkinManager
from lang_manager import MyLangManager
from widget       import Widget 
from textarea     import Textarea

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
    _RowPitch = -1 ## for \n
    _BreakPitch = -1 ## for  linebreak line wrapp
    
    def SetAndBlitText(self,words):# words => []
        
        if self._TextFull != True:            
            self._MyWords = words
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
        
        #print(self._MyWords)
        for i, v in enumerate(self._MyWords):
            if str(v) == "\n":
                w = 0
                x = self._PosX+xmargin
                linenumber+=2
                blit_rows.append([])
                blit_rows.append([])                
            else:
                t = v.Render()
                t_width = t.get_width()
                w += t_width
                del(t)
            
                blit_rows[linenumber].append(v)

                if i == self._TextIndex - 1:
                    cursor_row = linenumber

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
                if self._RowPitch > 0:
                    y = y + self._RowPitch
                else:
                    y = y + 16
                
                w = 0
                continue
                
            else:
                
                total_row_width = 0
                for i,v in enumerate(row):
                    t = v.Render()
                    total_row_width += t.get_width() 
                    if total_row_width > self._Width-endmargin:
                        start_x = self._PosX + xmargin
                    else:
                        if self._Align == "Center":
                            start_x = (self._Width - total_row_width)/2                            
        
            last_height = 0
            row_width = 0
            x = start_x
            y = y + last_height
            for i,v in enumerate(row):
                t = v.Render()
                row_width += t.get_width()
                
                if last_height < v.FnHeight():
                    last_height = v.FnHeight()
                
                if row_width >= self._Width-endmargin:                    
                    x = start_x
                    
                    if self._Align == "Center":
                        whatisleft = total_row_width - row_width
                        if whatisleft >= self._Width-endmargin:
                            x = start_x
                        else:
                            x = (self._Width-whatisleft)/2-endmargin
                    
                    if self._BreakPitch > 0:
                        y = y + self._BreakPitch
                    else:
                        y = y + last_height
                    
                    row_width = 0
            
                self._CanvasHWND.blit(t, (x,y))
                x += t.get_width()

    def Draw(self):
        #aa_round_rect(self._CanvasHWND, (4,24.5+6,312,60),self._BackgroundColor,4,0,self._BackgroundColor)

        aa_round_rect(self._CanvasHWND,  
                    (self._PosX,self._PosY,self._Width,self._Height),self._BackgroundColor,4,0,self._BackgroundColor)
        
        self.BlitText()  
