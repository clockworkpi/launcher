# -*- coding: utf-8 -*- 

import pygame


#import math

## local UI import
from UI.constants import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.icon_item import IconItem
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys, IsKeyMenuOrB
from UI.slider     import Slider
from UI.icon_pool  import MyIconPool
from UI.multi_icon_item import MultiIconItem
from UI.skin_manager import MySkinManager


from config import BackLight


import myvars

class BSlider(Slider):

    
    OnChangeCB = None
    _Parent     = None
    _Icons      = {}
    
    def __init__(self):
        Slider.__init__(self)
        self._Icons = {}
    def Init(self):
        self._Width = self._Parent._Width
        self._Height = self._Parent._Height
        
        self._BrightnessLabel = Label()
        self._BrightnessLabel.SetCanvasHWND(self._CanvasHWND)
        self._BrightnessLabel.Init("BRIGHT",MySkinManager.GiveFont("EurostileBold13"))
        self._BrightnessLabel.SetColor(MySkinManager.GiveColor('Text'))
        

    def SetValue(self,brt):
        self._Value = brt
        
    def Further(self):
        self._Value+=1
        if self._Value > 9:
            self._Value = 9
            
        if self.OnChangeCB != None:
            if callable(self.OnChangeCB):
                self.OnChangeCB(self._Value)
                    
    def StepBack(self):
        self._Value-=1

        if self._Value < 1:
            self._Value = 1

        if self.OnChangeCB != None:
            if callable(self.OnChangeCB):
                self.OnChangeCB(self._Value)
    
    def Draw(self):
        start_x = 82
        start_y = self._Parent._Screen._Height/2-5
        height = 30
        width = 4
        padding = 15
        seg = self._Value-1

        for i in range(0,9):
            rect = pygame.Rect(start_x+i*(width+padding),start_y,width,height)
            if i > seg:
                pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('Text'),rect, 1)
                #aa_round_rect(self._CanvasHWND,rect, MySkinManager.GiveColor('Text'),1,1, MySkinManager.GiveColor('White'))
            else:
                pygame.draw.rect(self._CanvasHWND,MySkinManager.GiveColor('Text'),rect, 0)   
                #aa_round_rect(self._CanvasHWND,rect, MySkinManager.GiveColor('Text'),1,0, MySkinManager.GiveColor('White'))
        
        self._BrightnessLabel.NewCoord(118,self._Parent._Screen._Height/2-30)
        self._BrightnessLabel.Draw(True)
        
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


        
class BrightnessPage(Page):

    _MySlider = None
    _FootMsg = ["Nav","","","Back","Enter"]

    
    def Init(self):
        self._CanvasHWND = self._Screen._CanvasHWND
        self._Width =  self._Screen._Width
        self._Height = self._Screen._Height
        
        self._MySlider = BSlider()
#        self._MySlider._Width = Width - 20
#        self._MySlider._Height = 30
#        self._MySlider._PosX  = (self._Width - self._MySlider._Width)/2
#        self._MySlider._PosY  = 40
        self._MySlider._Parent = self
        self._MySlider.SetCanvasHWND(self._CanvasHWND)
        self._MySlider.OnChangeCB = self.WhenSliderDrag
        self._MySlider.Init()

        brt  = self.ReadBackLight()
        
        self._MySlider.SetValue( brt)

    
    def ReadBackLight(self):
        try:
            f = open(BackLight)
        except IOError:
            return 0
        else:
            with f:
                content = f.readlines()
                content = [x.strip() for x in content]
                return int(content[0])

        return 0

    def OnLoadCb(self):
         brt  = self.ReadBackLight()
         
         self._MySlider.SetValue( brt)
         
    def SetBackLight(self,newbrt):
        try:
            f = open(BackLight,'w')
        except IOError:
            print("Open write %s failed %d" % (BackLight,newbrt))
            return False
        else:
            with f:
                f.write(str(newbrt))
                return True
        
    def WhenSliderDrag(self,value): ##value 
        self.SetBackLight(value)
        
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

        


    
