# -*- coding: utf-8 -*- 

import pygame

from libs.roundrects import aa_round_rect

import alsaaudio

## local package import
from constants   import ICON_TYPES,icon_ext,icon_width,icon_height,RUNEVT
from icon_item   import IconItem
from page        import Page,PageStack
from title_bar   import TitleBar
from foot_bar    import FootBar
from constants   import Width,Height,bg_color
from util_funcs  import midRect
from fonts       import fonts
from keys_def    import CurKeys
from label       import Label




class AboveAllPatch(object):
    _PosX  =Width/2
    _PosY  =Height/2
    _Width =50
    _Height=120
    
    _Text  =""
    _FontObj=fonts["veramono20"]
    _Parent =None
    _Color = pygame.Color(83,83,83)
    _ValColor= pygame.Color(0,0,255)
    _CanvasHWND = None
    _TextSurf = None
    _Icons   = {}
    _Value   = 0
    
    def __init__(self):
        self._Icons = {}
    
    def Init(self):
        pass
    
    def SetCanvasHWND(self,_canvashwnd):
        self._CanvasHWND = _canvashwnd

    def Draw(self):
        start_rect = midRect(self._PosX,self._PosY,self._Width,self._Height,Width,Height)
        aa_round_rect(self._CanvasHWND,start_rect, self._Color,3,0, self._Color)

        if self._Value > 10:
            vol_height = int(self._Height * (float( self._Value)/100.0))
            dheight    = self._Height - vol_height
            
            vol_rect = pygame.Rect(self._PosX-self._Width/2, self._PosY-self._Height/2+dheight, self._Width, vol_height)

            aa_round_rect(self._CanvasHWND,vol_rect, self._ValColor,3,0, self._ValColor)
        
        else:
            vol_height = 10
            dheight    = self._Height - vol_height
            vol_rect = pygame.Rect(self._PosX-self._Width/2, self._PosY-self._Height/2+dheight, self._Width, vol_height)

            aa_round_rect(self._CanvasHWND,vol_rect, self._ValColor,3,0, self._ValColor)
    

class SoundPatch(AboveAllPatch):

    _ValColor =  pygame.Color(131,199,219)
    _Segs       = [0,15,29, 45,55,65, 75,90,100]
    snd_segs = [ [0,20],[21,40],[41,50],[51,60],[61,70],[71,85],[86,90],[91,95],[96,100] ]

    def Init(self):
        self.SetCanvasHWND(self._Parent._CanvasHWND)
        
    def VolumeUp(self):
        m = alsaaudio.Mixer()
        vol = m.getvolume()[0]
        vol += 10
        if vol > 100:
            vol = 100

        m.setvolume(vol)

        self._Value = vol
        
        return vol
        
    def VolumeDown(self):
        m = alsaaudio.Mixer()
        vol = m.getvolume()[0]
        vol -= 10
        if vol < 0:
            vol = 0
        m.setvolume(vol)

        print(vol)
        self._Value = vol
        return vol


    def Draw(self):
        # 200 total width
        # h = 40
        ge = 0
        for i,v in enumerate(self.snd_segs):
            if  self._Value >= v[0] and self._Value <= v[1]:
                ge = i
                break
        
        for i in range(0,ge+1):
            #w = 10,h = 40
            vol_rect = pygame.Rect(80+i*20, self._Height/2+20,10, 40)
            
            aa_round_rect(self._CanvasHWND,vol_rect, self._ValColor,3,0, self._ValColor)
    
