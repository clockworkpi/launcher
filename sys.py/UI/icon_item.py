# -*- coding: utf-8 -*- 

import pygame

## local import
from constants  import icon_width,icon_height,ICON_TYPES,ALIGN,icon_ext,Width,Height
from util_funcs import color_surface,midRect
from label      import Label

class IconItem:
    _PosX=0
    _PosY=0
    _Width=0
    _Height=0
    _ImageName=""
    _ImgSurf = None
    _Parent = None
    _Index  = 0
    _MyType = ICON_TYPES["EXE"]
    _CmdPath = ""
    _LinkPage = None
    _Label   = None
    _Align   = ALIGN["VCenter"] # set for the Icon Image and Text Label
    
    def __init__(self):
        self._ImgSurf=None
        

    def Init(self,x,y,w,h,at): # the Surface is assigned in Screen 
        self._PosX = x
        self._PosY = y
        self._Width = w
        self._Height = h
        self._AnimationTime = at

    def SetLableColor(self,color):
        self._Label.SetColor(color)
        
    def NewCoord(self,x,y):
        self._PosX = x
        self._PosY = y

    def AddLabel(self,text,fontobj):
        if self._Label == None:
            self._Label = Label()
            self._Label.Init(text,fontobj)
        else:
            #just replace the text
            self._Label._Init(text,fontobj)

    def Adjust(self,x,y,w,h,at): # the Surface is assigned in Screen 
        self.Init(x,y,w,h,at)

        if self._Label != None:
            self._Label.SetCanvasHWND( self._Parent._CanvasHWND)

        self.CreateImageSurf()
        self.AdjustLinkPage()

    def AdjustLinkPage(self):
        if self._MyType==ICON_TYPES["DIR"] and self._LinkPage != None:
            self._LinkPage._Index = 0
            self._LinkPage._Align = ALIGN["SLeft"]
            self._LinkPage._IconNumbers = len(self._LinkPage._Icons)
            self._LinkPage._Screen = self._Parent._Screen
            self._LinkPage._CanvasHWND       = self._Parent._Screen._CanvasHWND
            
            self._LinkPage._FootMsg =  ["Nav.","","","Back","Enter"] ## Default Page Foot info
            
            if self._LinkPage._Align == ALIGN["HLeft"]:
                self._LinkPage.AdjustHLeftAlign()
            elif self._LinkPage._Align == ALIGN["SLeft"]:
                self._LinkPage.AdjustSAutoLeftAlign()
                if self._LinkPage._IconNumbers > 1:
                    self._LinkPage._PsIndex = 1
                    self._LinkPage._IconIndex = self._LinkPage._PsIndex

    def CreateImageSurf(self):
        
        if self._ImgSurf == None and self._ImageName != "":
#            print(self._ImageName)
            self._ImgSurf = pygame.image.load( self._ImageName ).convert_alpha() 
            if self._ImgSurf.get_width() > icon_width or self._ImgSurf.get_height() > icon_height:
                self._ImgSurf = pygame.transform.scale(self._ImgSurf,(icon_width,icon_height))
   
    def ChangeImgSurfColor(self,color):
        color_surface(self._ImgSurf,color)

    def Clear(self):
        pass

    def Draw(self):
        if self._Align==ALIGN["VCenter"]: #default
            if self._Label != None:
                self._Label._PosX = self._PosX - self._Label._Width/2 + self._Parent._PosX
                self._Label._PosY = self._PosY + self._Height/2 +6  + self._Parent._PosY
                
        elif self._Align ==ALIGN["HLeft"]:
            if self._Label != None:
                self._Label._PosX = self._PosX + self._Width/2 + 3 + self._Parent._PosX
                self._Label._PosY = self._PosY - self._Label._Height/2 + self._Parent._PosY

        if self._Label!=None:
            self._Label.Draw()
        
        if self._ImgSurf != None:
            self._Parent._CanvasHWND.blit(self._ImgSurf,midRect(self._PosX+self._Parent._PosX,
                                       self._PosY+self._Parent._PosY,
                                       self._Width,self._Height,Width,Height))
