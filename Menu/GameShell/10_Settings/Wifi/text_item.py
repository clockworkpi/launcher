# -*- coding: utf-8 -*- 
#local import
from UI.constants import Width,Height,ICON_TYPES
from UI.icon_item import IconItem
from UI.util_funcs import midRect

class TextItem(IconItem):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 0
    _Str    = ""
    _Color = (83,83,83)
    _FontObj = None
    _Bold    = False
    _MyType  = ICON_TYPES["LETTER"] 
    _Parent  = None

    def Draw(self):
        self._FontObj.set_bold(self._Bold)
        my_text = self._FontObj.render(self._Str,True,self._Color)
        if my_text.get_width() != self._Width:
            self._Width = my_text.get_width()
        if my_text.get_height() != self._Height:
            self._Height = my_text.get_height()

        self._Parent._CanvasHWND.blit(my_text, \
            midRect(self._PosX,self._PosY,self._Width,self._Height,Width,Height))
