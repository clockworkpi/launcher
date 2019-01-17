# -*- coding: utf-8 -*- 

class Widget:
    _PosX =0 
    _PosY = 0
    _Width = 0
    _Height = 0

    def __init__(self):
        pass
    
    def NewCoord(self,x,y):
        self._PosX = x
        self._PosY = y
    
    def Coord(self):
        return self._PosX,self._PosY
    
    def Width(self):
        return self._Width
    
    def Height(self):
        return self._Height
    
    def Size(self):
        return self._Width,self._Height
