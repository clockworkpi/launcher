# -*- coding: utf-8 -*- 

import pygame


#import math

## local UI import
from UI.constants import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.icon_item import IconItem
from UI.fonts  import fonts
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys
from UI.slider     import Slider
from UI.icon_pool  import MyIconPool
from UI.multi_icon_item import MultiIconItem
from config import BackLight
import myvars

class BSlider(Slider):

    
    OnChangeCB = None
    _BGpng = None
    _BGwidth = 179
    _BGheight = 153

    _NeedleSurf = None
    _Scale      = None
    _Parent     = None
    _Icons      = {}
    
    def __init__(self):
        Slider.__init__(self)
        self._Icons = {}
    def Init(self):
        self._Width = self._Parent._Width
        self._Height = self._Parent._Height
        
        bgpng = IconItem()
        bgpng._ImgSurf = MyIconPool._Icons["light"]
        bgpng._MyType = ICON_TYPES["STAT"]
        bgpng._Parent = self
        bgpng.Adjust(0,0,self._BGwidth,self._BGheight,0)
        self._Icons["bg"] = bgpng
        ##self._NeedleSurf = pygame.Surface( (38,12),pygame.SRCALPHA )
        
        scale = MultiIconItem()
        scale._MyType = ICON_TYPES["STAT"]
        scale._Parent = self
        scale._ImgSurf = MyIconPool._Icons["scale"]
        scale._IconWidth = 82
        scale._IconHeight = 63
        scale.Adjust(0,0,82,63,0)
        self._Icons["scale"] = scale

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

        self._Icons["bg"].NewCoord(self._Width/2,self._Height/2 +11 )
        self._Icons["bg"].Draw()

        self._Icons["scale"].NewCoord(self._Width/2,self._Height/2 )

        icon_idx = self._Value - 1
        if icon_idx < 0:
            icon_idx = 0
        
        self._Icons["scale"]._IconIndex = icon_idx
        self._Icons["scale"].Draw()
        """
        pygame.draw.line(self._CanvasHWND,(255,0,0), (posx,self._PosY),(self._Width,self._PosY),3) ## range line
        pygame.draw.line(self._CanvasHWND,(0,0,255), (self._PosX,self._PosY),(posx,self._PosY),3) ## range line
        
        pygame.draw.circle(self._CanvasHWND,(255,255,255),( posx, self._PosY),7,0)        
        pygame.draw.circle(self._CanvasHWND,(0,0,0)      ,( posx, self._PosY),7,1)## outer border
        """
        
        
        
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
        
        if event.key == CurKeys["Menu"] or event.key == CurKeys["A"]:
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

        


    
