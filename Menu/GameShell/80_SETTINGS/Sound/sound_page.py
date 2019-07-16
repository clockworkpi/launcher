# -*- coding: utf-8 -*- 

import pygame

#from libs.roundrects import aa_round_rect

import alsaaudio

## local UI import
from UI.constants import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.icon_item import IconItem
from UI.label  import Label
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys, IsKeyMenuOrB
from UI.slider     import Slider
from UI.multi_icon_item import MultiIconItem
from UI.skin_manager import MySkinManager

from UI.icon_pool  import MyIconPool

from libs.roundrects import aa_round_rect

import myvars

class SoundSlider(Slider):
    OnChangeCB = None
    
    _Parent     = None
    _VolumeLabel =None
    
    def __init__(self):
        Slider.__init__(self)
        
    def Init(self):
        self._Width = self._Parent._Width
        self._Height = self._Parent._Height
        
        self._VolumeLabel = Label()
        self._VolumeLabel.SetCanvasHWND(self._CanvasHWND)
        self._VolumeLabel.Init("VOLUME",MySkinManager.GiveFont("EurostileBold13"))
        self._VolumeLabel.SetColor(MySkinManager.GiveColor('Text'))
        
    def SetValue(self,vol):#pct 0-100
        if vol  >= 0 and vol <= 100:
            self._Value = vol
        
    def Further(self):
        self._Value+=5

        if self._Value > 100:
            self._Value = 100
        
        if self.OnChangeCB != None:
            if callable(self.OnChangeCB):
                self.OnChangeCB( self._Value )
        
    def StepBack(self):
        self._Value-=5

        if self._Value < 0:
            self._Value = 0
            
        if self.OnChangeCB != None:
            if callable(self.OnChangeCB):
                self.OnChangeCB( self._Value )
    
    def Draw(self):
        start_x = 82
        start_y = self._Parent._Screen._Height/2-5
        height = 30
        width = 4
        seg = self._Value / 5

        for i in range(0, 20):
            rect = pygame.Rect(start_x+i*(width*2),start_y,width,height)
            if i > seg:
                pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('Text'),rect, 1)
                #aa_round_rect(self._CanvasHWND,rect, MySkinManager.GiveColor('Text'),1,1, MySkinManager.GiveColor('White'))
            else:
                pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('Text'),rect, 0)   
                #aa_round_rect(self._CanvasHWND,rect, MySkinManager.GiveColor('Text'),1,0, MySkinManager.GiveColor('White'))
        
        self._VolumeLabel.NewCoord(118,self._Parent._Screen._Height/2-30)
        self._VolumeLabel.Draw(True)
        
        minus_box_rect = pygame.Rect(start_x- (4+6)*4,start_y,6*4,30)
        pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('Text'),minus_box_rect, 0) 
        
        minus_rect     = pygame.Rect(start_x-8*4,start_y+14,2*4,2)
        pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('White'),minus_rect, 0) 
        
        plus_box_rect = pygame.Rect(start_x + 39*4 +4*4,start_y,6*4,30)
        pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('Text'),plus_box_rect, 0) 
        
        cross1_rect     = pygame.Rect(start_x+39*4+4*4+2*4,start_y+14,2*4,2)
        pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('White'),cross1_rect, 0) 
        cross2_rect     = pygame.Rect(start_x+39*4+4*4+2*4+3,start_y+14-3,2,2*4)
        pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('White'),cross2_rect, 0) 
        
class SoundPage(Page):

    _MySlider = None
    _FootMsg = ["Nav","","","Back","Enter"]

    def Init(self):
        self._CanvasHWND = self._Screen._CanvasHWND
        self._Width =  self._Screen._Width
        self._Height = self._Screen._Height
        
        self._MySlider = SoundSlider()

        self._MySlider._Parent = self        
        self._MySlider.SetCanvasHWND(self._CanvasHWND)

        self._MySlider.OnChangeCB = self.WhenSliderDrag

        self._MySlider.Init()
        
        try:
            m = alsaaudio.Mixer()
            self._MySlider.SetValue(m.getvolume()[0])
        except Exception,e:
            print(str(e))
            self._MySlider.SetValue(0)


    def OnLoadCb(self):
        try:
            m = alsaaudio.Mixer()
            self._MySlider.SetValue(m.getvolume()[0])
        except Exception,e:
            print(str(e))
                
    def WhenSliderDrag(self,value): ##value 0-100
        if value < 0 or value > 100:
            return
        
        m = alsaaudio.Mixer()
        m.setvolume(int(value))
        
    def KeyDown(self,event):
        
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
        if event.key == CurKeys["Right"]:
            self._MySlider.Further()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
        if event.key == CurKeys["Left"]:
            self._MySlider.StepBack()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
    def Draw(self):
        self.ClearCanvas()
        
        self._MySlider.Draw()

        


    
