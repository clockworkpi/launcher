# -*- coding: utf-8 -*- 

import pygame

from libs import easing

## local UI import
from UI.constants  import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.fonts  import fonts
from UI.util_funcs import midRect
from UI.keys_def import CurKeys
from UI.icon_item import IconItem
from UI.icon_pool    import MyIconPool

from libs.roundrects import aa_round_rect

from textarea  import Textarea
from text_item import TextItem

import myvars

class KeyboardIcon(IconItem):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 0
    _Color = pygame.Color(83,83,83)
    _MyType  = ICON_TYPES["NAV"] 
    _Parent  = None
    _Str     = ""
    
    def Draw(self):
        self._Parent._CanvasHWND.blit(self._ImgSurf, \
            midRect(self._PosX,self._PosY,self._Width,self._Height,Width,Height))


class KeyboardSelector(PageSelector):
    
    def Draw(self):
        sec_idx = self._Parent._SectionIndex
        row_idx = self._Parent._RowIndex
        idx     = self._Parent._PsIndex
        
        x       = self._Parent._SecsKeys[sec_idx][row_idx][idx]._PosX
        y       = self._Parent._SecsKeys[sec_idx][row_idx][idx]._PosY
        w       = self._Parent._SecsKeys[sec_idx][row_idx][idx]._Width+6
        h       = self._Parent._SecsKeys[sec_idx][row_idx][idx]._Height+1

        rect    = midRect(x,y,w,h,self._Parent._Width,self._Parent._Height)
        if rect.width <=0 or rect.height <= 0 :
            return

        aa_round_rect(self._Parent._CanvasHWND,rect, (126,206,244),3,0,(126,206,244))
#        pygame.draw.rect(self._Parent._CanvasHWND,(0,0,0),rect,1)

class Keyboard(Page):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 0
    _SectionNumbers = 3
    _SectionIndex = 1

    _Icons = {}
    _Secs = {}
    _SecsKeys = {}
    _KeyboardLayoutFile = "UI/keyboard_keys.layout"
    _Textarea = None
    _Selector = None
    _LeftOrRight = 1
    _FootMsg           = ["Nav.","ABC","Done","Backspace","Enter"]

    _RowIndex    = 0
    
    def __init__(self):
        self._Secs     = {}
        self._SecsKeys = {}
        self._Icons    = {}

    def ReadLayoutFile(self,fname):
        LayoutIndex = 0
        with open(fname) as f:
            content = f.readlines()

        content = [ x.strip() for x in content]
        content = [ x.split(" ") for x in content]

        for i in content:
            i = [ x.strip() for x in i]
            if len(i) > 2:
                if LayoutIndex in self._Secs:
                    self._Secs[LayoutIndex].append(i)
                else:
                    self._Secs[LayoutIndex] = []
                    self._Secs[LayoutIndex].append(i)
            else:
                LayoutIndex+=1

    def SetPassword(self,pwd):
        
        pwd_list = list(pwd)
        self._Textarea.ResetMyWords()
        for i in pwd_list:
            self._Textarea.AppendText(i)
            #self._Textarea.BlitText()
        
    def Init(self):
        self._CanvasHWND = self._Screen._CanvasHWND
        self.ReadLayoutFile(self._KeyboardLayoutFile) ## assign to _Secs
        self._SectionNumbers = len(self._Secs)
        self._PosX = self._Index*self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height
        
        fontobj = fonts["veramono24"]
        word_margin = 15

        start_x = (self._Width - fontobj.size( "".join(self._Secs[0][0]))[0]-len(self._Secs[0][0])*word_margin)/2+word_margin/2
        start_y = 0
        cnt = 0
        for i in range(0,self._SectionNumbers):
            self._SecsKeys[i] = []
            for j in range(0,len(self._Secs[i])):
                self._SecsKeys[i].append( [] )
                
                start_x = (self._Width - fontobj.size( "".join(self._Secs[i][j]))[0]-len(self._Secs[i][j])*word_margin)/2+word_margin/2
                start_x = start_x + i*Width
                start_y = 84+j*(word_margin+14)
                for idx,val in enumerate(self._Secs[i][j]):
                    ti = TextItem()
                    ti._FontObj = fontobj
                    ti._Parent = self

                    if val == "_L" or val == "_R":
                        it  = KeyboardIcon()
                        it._ImgSurf = MyIconPool._Icons[val]
                        it._Parent = self
                        it._Str = val
                        it.Init(start_x+it._ImgSurf.get_width()/2  ,start_y,it._ImgSurf.get_width(),it._ImgSurf.get_height(),0)
                        #self._Icons[val] = it
                        self._SecsKeys[i][j].append(it)
                        self._IconNumbers+=1
                        start_x = start_x + it._ImgSurf.get_width()+word_margin
                        
                    else:
                        if val == "_S":
                            val = "Space"
                            ti._FontObj = fonts["veramono15"]
                            ti._Bold = True
                        
                        cur_alpha_size  = ti._FontObj.size( val)
                        ti.Init(start_x + cur_alpha_size[0]/2,start_y,cur_alpha_size[0],cur_alpha_size[1],0)
                        ti._Str = val
                    
                        start_x = start_x + cur_alpha_size[0]+word_margin # prepare for next alpha
                        self._SecsKeys[i][j].append(ti)
    
        self._SectionIndex = 0

        self._Textarea = Textarea()
        
        self._Textarea._PosX = 4
        self._Textarea._PosY = 4
        self._Textarea._Width= self._Width - 4*2
        self._Textarea._Height = 60
        self._Textarea._CanvasHWND = self._CanvasHWND
        self._Textarea.Init()


        ps = KeyboardSelector()
        ps._Parent = self
        ps.Init(start_x,start_y,25,25,128)
        self._Ps = ps
        self._PsIndex = 0
        self._Ps._OnShow = True

    def SelectUpChar(self):
        sec_idx = self._SectionIndex
        self._RowIndex-=1
        if self._RowIndex <0:
            self._RowIndex = len(self._SecsKeys[sec_idx])-1

        if self._PsIndex >=len(self._SecsKeys[sec_idx][self._RowIndex]):
            self._PsIndex = len(self._SecsKeys[sec_idx][self._RowIndex])-1


        self.ClearCanvas()
        self.Draw()
        self._Screen.SwapAndShow()
            
    def SelectDownChar(self):
        sec_idx = self._SectionIndex
        self._RowIndex+=1
        if self._RowIndex >= len(self._SecsKeys[sec_idx]):
            self._RowIndex = 0

        if self._PsIndex >=len(self._SecsKeys[sec_idx][self._RowIndex]):
            self._PsIndex = len(self._SecsKeys[sec_idx][self._RowIndex])-1

        self.ClearCanvas()
        self.Draw()
        self._Screen.SwapAndShow()
        
    def SelectNextChar(self):
        sec_idx = self._SectionIndex
        row_idx = self._RowIndex
        self._PsIndex+=1
        if self._PsIndex >= len(self._SecsKeys[sec_idx][row_idx]):
            self._PsIndex = 0
            self._RowIndex+=1
            if self._RowIndex >= len(self._SecsKeys[sec_idx]):
                self._RowIndex = 0
        
        self.ClearCanvas()
        self.Draw()
        self._Screen.SwapAndShow()

    def SelectPrevChar(self):
        sec_idx = self._SectionIndex    
        self._PsIndex-=1
        if self._PsIndex < 0:
            self._RowIndex-=1
            if self._RowIndex <=0:
                self._RowIndex = len(self._SecsKeys[sec_idx])-1
            self._PsIndex = len(self._SecsKeys[sec_idx][self._RowIndex]) -1

        self.ClearCanvas()
        self.Draw()
        self._Screen.SwapAndShow()
      
    def ClickOnChar(self):
        sec_idx = self._SectionIndex        
        alphabet = self._SecsKeys[sec_idx][self._RowIndex][self._PsIndex]._Str

        if alphabet == "Space":
            alphabet = " "
        
        if alphabet == "_L" or alphabet == "_R":
            if alphabet == "_L":
                self._Textarea.SubTextIndex()
            elif alphabet == "_R":
                self._Textarea.AddTextIndex()
        else:
            self._Textarea.AppendText(alphabet)
        
        self._Textarea.Draw()
        self._Screen.SwapAndShow()


    def KeyboardShift(self):
        current_time = 0.0
        start_posx   = 0.0
        current_posx = start_posx
        final_posx   = 320.0
        posx_init    = 0.0
        dur          = 30
        last_posx    = 0.0 
        all_last_posx = []

        for i in range(0,Width*dur):
            current_posx = easing.SineIn(current_time,start_posx,final_posx-start_posx,float(dur))
            if current_posx >= final_posx:
                current_posx = final_posx

            dx  = current_posx - last_posx
            all_last_posx.append(int(dx))
            current_time +=1
            last_posx = current_posx
            if current_posx >= final_posx:
                break
        
        c = 0
        for i in all_last_posx:
            c+=i
        if c < final_posx - start_posx:
            all_last_posx.append(final_posx - c)

        for i in all_last_posx:
            for j in range(0,self._SectionNumbers):
                for u in self._SecsKeys[j]:
                    for x in u: 
                        x._PosX += self._LeftOrRight*i
            
            self.ResetPageSelector()
            self.ClearCanvas()
            self.Draw()
            self._Screen.SwapAndShow()
        
    def KeyDown(self,event):# event from pygame.event.get()
        if event.key == CurKeys["Up"]:
            self.SelectUpChar()
        if event.key == CurKeys["Down"]:
            self.SelectDownChar()
        if event.key == CurKeys["Right"]:
            self.SelectNextChar()
        if event.key == CurKeys["Left"]:
            self.SelectPrevChar()
        if event.key == CurKeys["B"] or event.key == CurKeys["Enter"]:
            self.ClickOnChar()
        if event.key == CurKeys["X"]:
            if self._SectionIndex <= 0:
                self._LeftOrRight = -1
            if self._SectionIndex >= (self._SectionNumbers -1):
                self._LeftOrRight = 1
            self.KeyboardShift()

            self._SectionIndex -= self._LeftOrRight

            #print(self._SectionIndex) # on which keyboard section now
            self.Draw()
            self._Screen.SwapAndShow()
        
        if event.key == CurKeys["Menu"]: # we assume keyboard always be child page
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
        if event.key == CurKeys["Y"]: #done 
            print("".join(self._Textarea._MyWords))
            self.ReturnToUpLevelPage()
            self._Screen.SwapAndShow()
            ## config and connect now
            myvars.ScanPage.ConfigWireless( "".join(self._Textarea._MyWords)) 

        if event.key == CurKeys["A"]:
            self._Textarea.RemoveFromLastText()
            self._Textarea.Draw()
            self._Screen.SwapAndShow()

    def Draw(self):
        self.ClearCanvas()
        self._Ps.Draw()
        for i in range(0,self._SectionNumbers):
            for j in self._SecsKeys[i]:
                for u in j:
                    u.Draw()

        
        self._Textarea.Draw()


