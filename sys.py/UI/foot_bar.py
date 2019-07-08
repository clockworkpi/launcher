# -*- coding: utf-8 -*-

import pygame
import os


##local import
from constants  import Width,Height,ICON_TYPES,ALIGN
from util_funcs import FileExists,midRect
from icon_item  import IconItem
from multi_icon_item import MultiIconItem
from icon_pool  import MyIconPool
from libs.roundrects import aa_round_rect
from lang_manager import MyLangManager
from widget      import Widget
from skin_manager import MySkinManager

import config

icon_base_path = MySkinManager.GiveIcon("gameshell/footbar_icons/")

class FootBarIcon(MultiIconItem):

    def TotalWidth(self):
        return self._Width+self._Label._Width

    def Draw(self):
        if self._Align==ALIGN["VCenter"]: #default
            if self._Label != None:
                self._Label._PosX = self._PosX - self._Label._Width/2
                self._Label._PosY = self._PosY + self._Height/2 + 12

        elif self._Align ==ALIGN["HLeft"]:
            if self._Label != None:
                self._Label._PosX = self._PosX + self._Width/2 + 3
                self._Label._PosY = self._PosY - self._Label._Height/2

        if self._Label!=None:
            self._Label.Draw()

        if self._ImgSurf != None:
            self._Parent._CanvasHWND.blit(self._ImgSurf,midRect(self._PosX,
                                                                self._PosY,
                                                                self._Width,self._Height,Width,Height),
                                          (0,self._IconIndex*self._IconHeight,self._IconWidth,self._IconHeight))
class FootBar(Widget):
    _Width     = Width
    _Height    = 20
    _BarHeight = 20.5
    _BorderWidth = 1
    _CanvasHWND = None
    _HWND       = None
    _Icons      = {}
    _IconWidth   = 18
    _IconHeight  = 18
    _LabelFont   = MyLangManager.TrFont("veramono10")
    _State       = "normal"

    _SkinManager = None

    def __init__(self):
        self._Icons = {}


    def ReadFootBarIcons(self,icondir):
        if FileExists(icondir) == False and os.path.isdir(icondir) == False:
            return

        keynames = ["nav","x","y","a","b","select"]

        share_surf = pygame.image.load(icon_base_path+"footbar.png").convert_alpha()

        files = os.listdir(icondir)
        for _i,i in enumerate( keynames):
            it = FootBarIcon()
            it._MyType = ICON_TYPES["NAV"]
            it._Parent = self
            it._ImgSurf= share_surf
            it._Align = ALIGN["HLeft"] # (x)text <=

            it.AddLabel("game",self._LabelFont)
            it.Adjust(self._IconWidth/2+_i*self._IconWidth, self._IconHeight/2+2, self._IconWidth, self._IconHeight,0)
            it._IconIndex = _i
            self._Icons[i] = it


    def Init(self,screen):
        self._HWND       = screen
        self._CanvasHWND = pygame.Surface((Width,int(self._BarHeight)))

        self.ReadFootBarIcons(icon_base_path)

        round_corners   =  MultiIconItem()
        round_corners._IconWidth = 10
        round_corners._IconHeight = 10

        round_corners._MyType = ICON_TYPES["STAT"]
        round_corners._Parent = self
        round_corners._ImgSurf = MyIconPool.GiveIconSurface("roundcorners")
        round_corners.Adjust(0,0,10,10,0)

        self._Icons["round_corners"] = round_corners

    def ResetNavText(self):
        self._Icons["nav"]._Label.SetText(MyLangManager.Tr("Nav"))
        self._State = "normal"
        self.Draw()
        return False

    def UpdateNavText(self,texts):
        self._State = "tips"
        texts = MyLangManager.Tr(texts)
        my_text = self._LabelFont.render(texts,True,self._SkinManager.GiveColor("Text"))
        """
        _w = 0
        for i, x in enumerate(("b","a","y","x")):
            if self._Icons[x]._Label._Text!="":
                if i==0:
                    _w += self._Icons[x].TotalWidth()
                else:
                    _w += self._Icons[x].TotalWidth()+5
        """
        left_width = self._Width  - 18

        final_piece = ""
        for i ,v in enumerate(texts):
            text_slice = texts[:i+1]
            my_text = self._LabelFont.render(text_slice,True, self._SkinManager.GiveColor("Text"))
            final_piece = text_slice
            if my_text.get_width() >= left_width:
                break

        print("finalpiece %s" %final_piece)
        self._Icons["nav"]._Label.SetText( final_piece )

        self.Draw()

    def SetLabelTexts(self,texts):
        barr = ["nav","y","x","b","a","select"]
        texts2 = texts + [""] if len(texts) == 5 else texts

        for idx,x in enumerate(barr):
            try:
                self._Icons[x]._Label.SetText(MyLangManager.Tr(texts2[idx]))
            except IndexError:
                print("Index "+x+" doesn't exist!")


    def ClearCanvas(self):
        self._CanvasHWND.fill( self._SkinManager.GiveColor("White") )

        self._Icons["round_corners"].NewCoord(5,self._Height -5 )
        self._Icons["round_corners"]._IconIndex = 2
        self._Icons["round_corners"].Draw()

        self._Icons["round_corners"].NewCoord(self._Width-5,self._Height-5)
        self._Icons["round_corners"]._IconIndex = 3
        self._Icons["round_corners"].Draw()


        """
        aa_round_rect(self._CanvasHWND,
                    (0,0,self._Width,self._Height),self._BgColor,8,0, self._BgColor)

        pygame.draw.rect(self._CanvasHWND,self._BgColor,(0,0,Width,self._BarHeight/2), 0 )
        """

    def Draw(self):
        self.ClearCanvas()
        self._Icons["nav"].NewCoord(self._IconWidth/2+3,self._IconHeight/2+2)
        self._Icons["nav"].Draw()

        if self._State == "normal":
            _w=0
            #for i,x in enumerate(("a","b","x","y")):
            for i, x in enumerate(("b","a","y","x","select")):
                if self._Icons[x]._Label._Text!="":
                    if i==0:
                        _w += self._Icons[x].TotalWidth()
                    else:
                        _w += self._Icons[x].TotalWidth()+5

                    start_x = self._Width - _w
                    start_y = self._IconHeight/2+2
                    self._Icons[x].NewCoord(start_x,start_y)
                    self._Icons[x].Draw()


        pygame.draw.line(self._CanvasHWND,self._SkinManager.GiveColor("Line"),(0,0),(Width,0),self._BorderWidth)

        if self._HWND  != None:
            self._HWND.blit(self._CanvasHWND,(self._PosX,Height - self._Height,Width,self._BarHeight))
