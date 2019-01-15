# -*- coding: utf-8 -*- 

import pygame

from skin_manager import MySkinManager
from lang_manager import MyLangManager
from widget       import Widget

class MultiLabel(Widget): ##Multi Line Label 
    _Width=135
    _Height=100
    _Text=""
    _FontObj=None
    _Color = MySkinManager.GiveColor('Text')
    _CanvasHWND = None
    _TextSurf = None
    _MaxWidth = 0
    
    def __init__(self):
        pass
    
    def Init(self,text,font_obj,color=MySkinManager.GiveColor('Text')):
        self._Color = color
        self._FontObj = font_obj
        self._Text = text
        
        self.blit_text(self._CanvasHWND,self._Text,(self._PosX,self._PosY),self._FontObj)
        

    def SetColor(self,color):
        self._Color = color
    
    def GetText(self):
        return self._Text
    
    def SetText(self,text):
        self._Text = text
        
        self.blit_text(self._CanvasHWND,self._Text,(self._PosX,self._PosY),self._FontObj) 
        
    def SetCanvasHWND(self,_canvashwnd):
        self._CanvasHWND = _canvashwnd

    def blit_text(self, surface,text, pos, font):
        iscjk = MyLangManager.IsCJKMode()
        
        color = self._Color
        words = [word.split(' ') for word in text.splitlines()]
        space = font.size(' ')[0]
        
        if iscjk:
            space = 0
            words = [list(word.decode("utf8")) for word in text.splitlines()]
        
        max_width = self._Width
        x ,y = pos
        row_total_width = 0
        lines = 0 
        line_max = 12
        row_max  = 4
        if iscjk:
            line_max = line_max*2
        
        for i,line in enumerate(words[:row_max]): 
            for word in line[:line_max]:
                word_surface = font.render(word, True, color)
                word_width = word_surface.get_width()
                word_height = word_surface.get_height()
                row_total_width += word_width
                if row_total_width+space  >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                    row_total_width = word_width
                    
                    if lines == 0:
                        lines += word_height
                    else:
                        lines += word_height
                    
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.
            lines += word_height        
        self._Height = lines

    
    def Draw(self):
        #my_text = self._FontObj.render( self._Text,True,self._Color)
        self.blit_text(self._CanvasHWND,self._Text,(self._PosX,self._PosY),self._FontObj)
        #pygame.draw.rect(self._CanvasHWND,(83,83,83), (self._PosX,self._PosY,self._Width,self._Height) , 1 )
        #self._CanvasHWND.blit(my_text,(self._PosX,self._PosY,self._Width,self._Height))
