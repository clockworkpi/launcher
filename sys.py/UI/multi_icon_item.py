# -*- coding: utf-8 -*- 

import pygame
#from beeprint import pp

## local import
from constants  import icon_width,icon_height,ICON_TYPES,ALIGN,icon_ext,Width,Height
from util_funcs import color_surface,midRect
from label      import Label
from icon_item  import IconItem

##Resource file contains multi icons in single image
##usually the Image contains icons in Vertical, convert 1.png 2.png 3.png -append out.png

class MultiIconItem(IconItem):
    _IconWidth=18
    _IconHeight=18
    _IconIndex = 0  # icon index on the resource Image 
    
    def CreateImageSurf(self):        
        if self._ImgSurf == None and self._ImageName != "":
#            print(self._ImageName)
            self._ImgSurf = pygame.image.load( self._ImageName ).convert_alpha() 
            

    def DrawTopLeft(self):
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
            self._Parent._CanvasHWND.blit(self._ImgSurf,pygame.Rect(self._PosX+self._Parent._PosX,
                                                                    self._PosY+self._Parent._PosY,
                                                                    self._Width,self._Height),
                                          (0,self._IconIndex*self._IconHeight,self._IconWidth,self._IconHeight))
        
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
                                                                self._Width,self._Height,Width,Height),
                                          (0,self._IconIndex*self._IconHeight,self._IconWidth,self._IconHeight))
            
