# -*- coding: utf-8 -*- 

import pygame
from libs.roundrects import aa_round_rect




## local UI import
from UI.page         import Page,PageStack,PageSelector
from UI.label        import Label
from UI.fonts        import fonts

class Textarea:
    _PosX =0 
    _PosY = 0
    _Width = 0
    _Height = 0
    _BackgroundColor = pygame.Color(229,229,229)
    _CanvasHWND  = None
    _MyWords     = []
    _FontObj     = None
    _LineNumber  = 0
    _TextFull    = False
    _TextIndex   = 0

    def __init__(self):
        pass
    
    def Init(self):
        self._FontObj = fonts["veramono24"] 
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
            print("is Full %s" % "".join(self._MyWords))

            
    def BlitText(self):
        """
        blit every single word into surface and calc the width ,check multi line 
        """
        w = 0
        xmargin = 5
        endmargin = 15
        x = self._PosX+xmargin
        y = self._PosY
        linenumber = 0
        self._TextFull = False
        for i,v in enumerate(self._MyWords):
            t = self._FontObj.render(v,True,(8,135,174))
            w += t.get_width()

            if w >= self._Width-endmargin and linenumber == 0:
                x = self._PosX+xmargin
                y = self._PosY+ t.get_height()
                w = 0
                linenumber +=1
            
            if w >= self._Width-endmargin*4 and linenumber > 0:
                self._TextFull = True
                self._CanvasHWND.blit(t, (x,y))
                break
            self._CanvasHWND.blit(t, (x,y))
            x += t.get_width()
        
    def Cursor(self):
        w = 0
        xmargin = 5
        endmargin = 15
        x = self._PosX+xmargin
        y = self._PosY
        linenumber = 0
        for i,v in enumerate(self._MyWords[:self._TextIndex]):
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
