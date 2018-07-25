# -*- coding: utf-8 -*- 

import pygame

#from libs.roundrects import aa_round_rect

import alsaaudio

## local UI import
from UI.constants import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.icon_item import IconItem
from UI.label  import Label
from UI.fonts  import fonts
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys
from UI.slider     import Slider
from UI.multi_icon_item import MultiIconItem


from UI.icon_pool  import MyIconPool

import myvars

class SoundSlider(Slider):
    OnChangeCB = None
    
    _BGpng = None
    _BGwidth = 192
    _BGheight = 173

    _NeedleSurf = None
    _Scale      = None
    _Parent     = None
    
    snd_segs = [ [0,20],[21,40],[41,50],[51,60],[61,70],[71,85],[86,90],[91,95],[96,100] ]

    
    def __init__(self):
        Slider.__init__(self)
        
    def Init(self):
        self._Width = self._Parent._Width
        self._Height = self._Parent._Height
        
        self._BGpng = IconItem()
        self._BGpng._ImgSurf = MyIconPool._Icons["vol"]
        self._BGpng._MyType = ICON_TYPES["STAT"]
        self._BGpng._Parent = self
        self._BGpng.Adjust(0,0,self._BGwidth,self._BGheight,0)

        ##self._NeedleSurf = pygame.Surface( (38,12),pygame.SRCALPHA )
        
        self._Scale = MultiIconItem()
        self._Scale._MyType = ICON_TYPES["STAT"]
        self._Scale._Parent = self
        self._Scale._ImgSurf = MyIconPool._Icons["scale"]
        self._Scale._IconWidth = 82
        self._Scale._IconHeight = 63
        self._Scale.Adjust(0,0,82,63,0)
        
    def SetValue(self,vol):#pct 0-100
        for i,v in enumerate(self.snd_segs):
            if vol  >= v[0] and vol <= v[1]:
                self._Value = i # self._Value :  0 - 8
                break
        
    def Further(self):
        self._Value+=1

        if self._Value > len(self.snd_segs)-1:
            self._Value = len(self.snd_segs) -1

        vol = self.snd_segs[self._Value][0] + (self.snd_segs[self._Value][1] - self.snd_segs[self._Value][0])/2 
        
        if self.OnChangeCB != None:
            if callable(self.OnChangeCB):
                self.OnChangeCB( vol )
        
    def StepBack(self):
        self._Value-=1

        if self._Value < 0:
            self._Value = 0

        vol =  self.snd_segs[self._Value][0]
        
        if self.OnChangeCB != None:
            if callable(self.OnChangeCB):
                self.OnChangeCB( vol )
    
    def Draw(self):
        
        self._BGpng.NewCoord(self._Width/2,self._Height/2 )
        self._BGpng.Draw()

        self._Scale.NewCoord(self._Width/2,self._Height/2)

        self._Scale._IconIndex = self._Value
        
        self._Scale.Draw()
        
        
        
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

        


    
