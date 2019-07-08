# -*- coding: utf-8 -*- 

import pygame
from libs.roundrects import aa_round_rect

## local UI import
from UI.page         import Page,PageStack,PageSelector
from UI.label        import Label
from UI.skin_manager import MySkinManager
from UI.lang_manager import MyLangManager
from UI.widget       import Widget 

class Textarea(Widget):
    _BackgroundColor = MySkinManager.GiveColor('TitleBg')
    _CanvasHWND  = None
    _MyWords     = []
    _BlitWords   = []
    _FontObj     = None
    _LineNumber  = 0
    _TextLimit   = 63
    _TextFull    = False
    _TextIndex   = 0
    _BlitIndex   = 0

    def __init__(self):
        pass
    
    def Init(self):
        self._FontObj = MyLangManager.TrFont("veramono24")
        #pygame.font.Font(fonts_path["veramono"],24)

    def SubTextIndex(self):

        self._TextIndex-=1
        if self._TextIndex < 0:
            self._TextIndex = 0

    def AddTextIndex(self):
        self._TextIndex +=1
        if self._TextIndex > len(self._MyWords):
            self._TextIndex = len(self._MyWords)
        
    def ResetMyWords(self):
        self._MyWords = []
        self._TextIndex = 0
        
    def RemoveFromLastText(self):
        if len(self._MyWords) > 0:
            self.SubTextIndex()
            
            del self._MyWords[self._TextIndex]
            
            return self._MyWords

    def AppendText(self,alphabet):
        
        self.AppendAndBlitText(alphabet)

    def AppendAndBlitText(self,alphabet):
        
        if self._TextFull != True:
            
            self._MyWords.insert(self._TextIndex,alphabet)
            self.BlitText()
            self.AddTextIndex()
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
            t = self._FontObj.render(v, True, (8, 135, 174))
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
        
        # only paint 2 rows
        if len(blit_rows) == 1:
            self._BlitWords = blit_rows[0]
            self._BlitIndex = self._TextIndex
        elif len(blit_rows) == 2 or cursor_row < 2:
            self._BlitWords = blit_rows[0] + blit_rows[1]
            self._BlitIndex = self._TextIndex
        else:
            self._BlitWords = blit_rows[cursor_row - 1] + blit_rows[cursor_row]
            self._BlitIndex = self._TextIndex
            for i,v in enumerate(blit_rows):
                if i == cursor_row - 1:
                    break
                self._BlitIndex -= len(v)
            
    def BlitText(self):
        """
        blit every single word into surface and calc the width ,check multi line 
        """
        # build up blitwords
        self.BuildBlitText()

        w = 0
        xmargin = 5
        endmargin = 15
        x = self._PosX+xmargin
        y = self._PosY
        linenumber = 0
        self._TextFull = len(self._MyWords) > self._TextLimit
        for i, v in enumerate(self._BlitWords):
            t = self._FontObj.render(v,True,(8,135,174))
            w += t.get_width()

            if w >= self._Width-endmargin and linenumber == 0:
                linenumber +=1
                x = self._PosX+xmargin
                y = self._PosY + t.get_height() * linenumber
                w = 0
            
            self._CanvasHWND.blit(t, (x,y))
            x += t.get_width()
        
    def Cursor(self):
        w = 0
        xmargin = 5
        endmargin = 15
        x = self._PosX+xmargin
        y = self._PosY
        linenumber = 0
        for i,v in enumerate(self._BlitWords[:self._BlitIndex]):
            t = self._FontObj.render(v,True,(8,135,174))
            w += t.get_width()

            if w >= self._Width-endmargin and linenumber == 0:
                x = self._PosX+xmargin
                y = self._PosY+ t.get_height()
                w = 0
                linenumber +=1
            
            if w >= self._Width-endmargin*3 and linenumber > 0:
                x += t.get_width()
                break
            x += t.get_width()
            
        self._CanvasHWND.blit(self._FontObj.render("_",True,(0,0,0)),(x+1,y-2))
    
    def Draw(self):
        #aa_round_rect(self._CanvasHWND, (4,24.5+6,312,60),self._BackgroundColor,4,0,self._BackgroundColor)

        aa_round_rect(self._CanvasHWND,  
                    (self._PosX,self._PosY,self._Width,self._Height),self._BackgroundColor,4,0,self._BackgroundColor)


        
        self.BlitText()
        self.Cursor()
