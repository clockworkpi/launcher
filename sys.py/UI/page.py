# -*- coding: utf-8 -*- 

import pygame
from pygame.locals import *
from sys import exit
import os
import sys
import math

from libs import easing

#import base64
#from beeprint import pp

### local import
from constants    import ALIGN,icon_width,icon_height,Width,Height,ICON_TYPES
from util_funcs   import midRect
from keys_def     import CurKeys
from icon_pool    import MyIconPool

class PageStack:
    def __init__(self):
        self.stack = list()

    def Push(self,data):
        if data not in self.stack:
            self.stack.append(data)
            return True
        return False

    def Pop(self):
        if len(self.stack)<=0:
            return None,False
        return self.stack.pop(),True
    
    def Length(self):
        return len(self.stack)

class PageSelector:
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 0
    _Parent = None
    _Alpha  = 0
    _OnShow = True
    _IconSurf = None 
    def __init__(self):
        pass

    def Init(self,x,y,w,h,alpha):
        self._PosX   = x
        self._PosY   = y
        self._Width   = w
        self._Height  = h
        self._Alpha   = alpha

    def Adjust(self,x,y,w,h,alpha):
        self._PosX   = x
        self._PosY   = y
        self._Width   = w
        self._Height  = h
        self._Alpha   = alpha

    def Draw(self):
        canvas  = self._Parent._CanvasHWND
        idx     = self._Parent._PsIndex
        iconidx = self._Parent._IconIndex

        if idx < len(self._Parent._Icons):
            x       = self._Parent._Icons[idx]._PosX+self._Parent._PosX
            y       = self._Parent._Icons[iconidx]._PosY ## only use current icon's PosY
        
            rect    = midRect(x,y,self._Width,self._Height,self._Parent._Width,self._Parent._Height)
            if rect.width <=0 or rect.height <= 0 :
                return

            #color = (244,197,66,50)
            #pygame.draw.rect(canvas,color,rect,1)
            if self._IconSurf != None:
                self._Parent._CanvasHWND.blit(self._IconSurf,rect)
            
class Page(object):
    _PosX=0
    _PosY=0
    _Width=0
    _Height=0
    _Icons = []
    _Ps = None
    _PsIndex = 0
    _IconNumbers = 0
    _IconIndex   = 0 ## shows which icon current selected, the Selector can not move here
    _PrevIconIndex = 0 ## for remember the  Highlighted Icon ,restore it's PosY to average
    _Index = 0
    _Align = ALIGN["SLeft"]
    _CanvasHWND = None # 
    _HWND       = None # 
    _OnShow     = False
    _Name       = ""
    _Screen     = None ## Should be the Screen Class
    _PageIconMargin = 20
    _FootMsg    = ["Nav.","","","","Enter"] ## Default Page Foot info

    _SelectedIconTopOffset=20
    _EasingDur   = 30
    
    def __init__(self):
        self._Icons = []


    def AdjustHLeftAlign(self): ## adjust coordinator and append the PageSelector
        self._PosX = self._Index*self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height
        
        cols = int(Width /icon_width)
        rows = int( (self._IconNumbers * icon_width)/Width + 1)
        if rows < 1:
            rows = 1

        cnt = 0

        for i in range(0,rows):
            for j in range(0,cols):
                start_x = icon_width/2  + j*icon_width
                start_y = icon_height/2 + i*icon_height
                icon = self._Icons[cnt]
                icon.Adjust(start_x,start_y,icon_width-4,icon_height-4,0)
                icon._Index = cnt
                icon._Parent = self
                if cnt >= (self._IconNumbers -1):
                    break
                cnt+=1
        
        ps = PageSelector()
        ps._IconSurf = MyIconPool._Icons["blueselector"]
        ps._Parent = self
        ps.Init(icon_width/2, TitleBar._BarHeight+icon_height/2,92,92,128)
        self._Ps = ps
        self._PsIndex = 0
        self._OnShow = False


    def AdjustSLeftAlign(self): ## adjust coordinator and append the PageSelector
        self._PosX = self._Index*self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height
        
        start_x = (self._PageIconMargin + icon_width+self._PageIconMargin) /2
        start_y = self._Height/2
        
        for i in range(0,self._IconNumbers):
            it = self._Icons[i]
            it._Parent = self
            it._Index = i
            it.Adjust(start_x+i*self._PageIconMargin+i*icon_width,start_y,icon_width-6,icon_height-6,0)
            it._ImgSurf = pygame.transform.smoothscale(it._ImgSurf,(it._Width,it._Height))

        ps = PageSelector()
        ps._IconSurf = MyIconPool._Icons["blueselector"]
        ps._Parent = self
        ps.Init(start_x,start_y,92,92,128)
        
        self._Ps = ps
        self._PsIndex = 0
        self._OnShow = False
        
        if self._IconNumbers > 1:
            self._PsIndex = 1
            self._IconIndex = self._PsIndex
            self._PrevIconIndex = self._IconIndex
            self._Icons[self._IconIndex]._PosY -= self._SelectedIconTopOffset

    def AdjustSAutoLeftAlign(self): ## adjust coordinator and append the PageSelector
        self._PosX = self._Index*self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height
        
        start_x = (self._PageIconMargin + icon_width+self._PageIconMargin) /2
        start_y = self._Height/2

        if self._IconNumbers == 1:
            start_x = self._Width / 2
            start_y = self._Height/2
            
            it = self._Icons[0]
            it._Parent = self
            it._Index = 0
            it.Adjust(start_x,start_y,icon_width,icon_height,0)
            #it._ImgSurf = pygame.transform.smoothscale(it._ImgSurf,(it._Width,it._Height))

        elif self._IconNumbers == 2:
            start_x = (self._Width - self._PageIconMargin - self._IconNumbers*icon_width) / 2 + icon_width/2
            start_y = self._Height /2

            for i in range(0,self._IconNumbers):
                it = self._Icons[i]
                it._Parent = self
                it._Index = i
                it.Adjust(start_x+i*self._PageIconMargin + i*icon_width,start_y, icon_width, icon_height,0)
                #it._ImgSurf = pygame.transform.smoothscale(it._ImgSurf,(it._Width,it._Height))
                
        elif self._IconNumbers > 2:
            for i in range(0,self._IconNumbers):
                it = self._Icons[i]
                it._Parent = self
                it._Index = i
                it.Adjust(start_x+i*self._PageIconMargin + i*icon_width,start_y,icon_width,icon_height,0)
                #it._ImgSurf = pygame.transform.smoothscale(it._ImgSurf,(it._Width,it._Height))

        ps = PageSelector()
        ps._IconSurf = MyIconPool._Icons["blueselector"]
        ps._Parent = self
        ps.Init(start_x,start_y,92,92,128)
        
        self._Ps = ps
        self._PsIndex = 0
        self._OnShow = False

        if self._IconNumbers > 1:
            self._PsIndex = 1
            self._IconIndex = self._PsIndex
            self._PrevIconIndex = self._IconIndex
            self._Icons[self._IconIndex]._PosY -= self._SelectedIconTopOffset

    def InitLeftAlign(self):
        self._PosX = self._Index*Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height
        
        cols = int(self._Width /icon_width)
        rows = int((self._IconNumbers * icon_width)/self._Width + 1)
        if rows < 1:
            rows = 1
        cnt = 0
        for i in range(0,rows):
            for j in range(0,cols):
                start_x = icon_width/2  + j*icon_width
                start_y = TitleBar._BarHeight + icon_height/2 + i*icon_height
                icon = IconItem()
                icon.Init(start_x,start_y,icon_width-4,icon_height-4,0)
                icon._Index = cnt
                icon._Parent = self
                self._Icons.append(icon)
                if cnt >= (self._IconNumbers -1):
                    break
                cnt+=1
                
        ps = PageSelector()
        ps._IconSurf = MyIconPool._Icons["blueselector"]
        ps._Parent = self
        ps.Init(icon_width/2,icon_height/2,92,92,128)
        self._Ps = ps
        self._PsIndex = 0
        self._OnShow = False

    def Adjust(self): ## default init way, 
        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height

        if self._Align == ALIGN["HLeft"]:
            start_x = (self._Width - self._IconNumbers*icon_width)/2 + icon_width/2
            start_y = self._Height/2

            for i in range(0,self._IconNumbers):
                it = self._Icons[i]
                it._Parent = self
                it._Index = i
                it.Adjust(start_x+i*icon_width,start_y,icon_width,icon_height,0)

            ps = PageSelector()
            ps._IconSurf = MyIconPool._Icons["blueselector"]
            ps._Parent = self
            ps.Init(start_x,start_y,92,92,128)
            self._Ps = ps
            self._PsIndex = 0
            self._OnShow = False
        elif self._Align == ALIGN["SLeft"]:
            start_x = (self._PageIconMargin + icon_width+self._PageIconMargin) /2
            start_y = self._Height/2
            
            for i in range(0,self._IconNumbers):
                it = self._Icons[i]
                it._Parent = self
                it._Index = i
                it.Adjust(start_x+i*self._PageIconMargin+i*icon_width,start_y,icon_width,icon_height,0)
                

       
            ps = PageSelector()
            ps._IconSurf = MyIconPool._Icons["blueselector"]
            ps._Parent = self
            ps.Init(start_x,start_y-self._SelectedIconTopOffset,92,92,128)
            
            self._Ps = ps
            self._PsIndex = 0
            self._OnShow = False
            
            if self._IconNumbers > 1:
                self._PsIndex = 1
                self._IconIndex = self._PsIndex
                self._PrevIconIndex = self._IconIndex
                self._Icons[self._IconIndex]._PosY -= self._SelectedIconTopOffset
                
                
    def Init(self): ## default init way, 
        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._CanvasHWND = self._Screen._CanvasHWND

        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height

        start_x = (self._Width - self._IconNumbers*icon_width)/2 + icon_width/2
        start_y = self._Height/2

        for i in range(0,self._IconNumbers):
            it = IconItem()
            it._Parent = self
            it._Index = i
            it.Init(start_x+i*icon_width,start_y,icon_width,icon_height,0)
            self._Icons.append(it)
            
        if self._IconNumbers > 0:
            ps = PageSelector()
            ps._IconSurf = MyIconPool._Icons["blueselector"]
            ps._Parent = self
            ps.Init(start_x,start_y,icon_width+4,icon_height+4,128)
            self._Ps = ps
            self._PsIndex = 0
            self._OnShow = False
            
    def IconStepMoveData(self,icon_eh,cuts):## no Sine,No curve,plain movement steps data
        all_pieces = []
        piece = icon_eh / cuts

        c = 0.0
        prev = 0.0
        for i in range(0,cuts):
            c+=piece
            dx = c-prev
            if dx < 0.5:
                dx = 1.0
                
            all_pieces.append( math.ceil(dx) )
            if c >= icon_eh:
                break

        c = 0
        bidx = 0
        for i in all_pieces:
            c+=i
            bidx+=1
            if c >= icon_eh:
                break

        all_pieces = all_pieces[0:bidx]

        if len(all_pieces) < cuts:
            dff = cuts - len(all_pieces)
            diffa = []
            for i in range(0,dff):
                diffa.append(0)
            all_pieces.extend( diffa)
                
        return all_pieces

    def EasingData(self,start,distance):##generate easing steps data
        current_time  = 0.0
        start_posx    = 0.0
        current_posx  = start_posx
        final_posx    = float(distance)
        posx_init     = start
        dur           = self._EasingDur
        last_posx     = 0.0
        all_last_posx = []
        for i in range(0,distance*dur):
            current_posx = easing.SineIn(current_time,start_posx,final_posx-start_posx,float(dur))
            if current_posx >= final_posx:
                current_posx = final_posx

            dx = current_posx - last_posx
            all_last_posx.append(int(dx))
            current_time+=1
            last_posx = current_posx
            if current_posx >= final_posx:
                break
            c = 0
        for i in all_last_posx:
            c+=i
        if c < final_posx -start_posx:
            all_last_posx.append(final_posx - c)

        return all_last_posx

    def IconSmoothUp(self,icon_ew):
        data = self.EasingData(self._PosX,icon_ew)
        data2 = self.IconStepMoveData(self._SelectedIconTopOffset,len(data))
        
        for i,v in enumerate(data):
            
            self.ClearCanvas()
            
            self._Icons[self._IconIndex]._PosY -= data2[i]
            
            if self._Icons[self._PrevIconIndex]._PosY < self._Height/2:
                self._Icons[self._PrevIconIndex]._PosY+=data2[i]

            self.DrawIcons()
            self._Screen.SwapAndShow()        
                
    def IconsEasingLeft(self,icon_ew):

        data = self.EasingData(self._PosX,icon_ew)
        data2 = self.IconStepMoveData(self._SelectedIconTopOffset,len(data))
        
        for i,v in enumerate(data):
            
            self.ClearCanvas()
            self._PosX -= v
            
            self._Icons[self._IconIndex]._PosY -= data2[i]
            
            if self._Icons[self._PrevIconIndex]._PosY < self._Height/2:
                self._Icons[self._PrevIconIndex]._PosY+=data2[i]
            self.DrawIcons()
            self._Screen.SwapAndShow()
                
    def IconsEasingRight(self,icon_ew):
        
        data = self.EasingData(self._PosX,icon_ew)
        data2 = self.IconStepMoveData(self._SelectedIconTopOffset,len(data))
        
        for i,v in enumerate(data):
            self.ClearCanvas()
            self._PosX += v

            
            self._Icons[self._IconIndex]._PosY-=data2[i]
            
            if self._Icons[self._PrevIconIndex]._PosY < self._Height/2:
                self._Icons[self._PrevIconIndex]._PosY+=data2[i]
                
            self.DrawIcons()
            self._Screen.SwapAndShow()
            
    def EasingLeft(self,ew): #ew int

        data = self.EasingData(self._PosX,ew)
        
        for i in data:
            self._PosX -=i
            self.Draw()
            self._Screen.SwapAndShow()
            
    def EasingRight(self,ew):

        data = self.EasingData(self._PosX,ew)
        
        for i in data:
            self._PosX += i
            self.Draw()
            self._Screen.SwapAndShow()
            
    def MoveLeft(self,ew):
        self._PosX -= ew
    def MoveRight(self,ew):
        self._PosX += ew
        
    def ResetPageSelector(self):
        self._PsIndex = 0
        self._IconIndex = 0
        self._Ps._OnShow = True

    def DrawPageSelector(self):
        if self._Ps._OnShow == True:
            self._Ps.Draw()
            
    def MoveIconIndexPrev(self):
        
        self._IconIndex-=1
        if self._IconIndex < 0:
            self._IconIndex = 0
            self._PrevIconIndex = self._IconIndex
            return False
        self._PrevIconIndex = self._IconIndex+1
        return True
    
    def MoveIconIndexNext(self):
        #True for Moved,False is boundary
        self._IconIndex+=1
        if self._IconIndex > (self._IconNumbers - 1):
            self._IconIndex = self._IconNumbers -1
            self._PrevIconIndex = self._IconIndex
            return False
        self._PrevIconIndex = self._IconIndex-1
        return True

    
    def IconClick(self):
        
        if self._IconIndex > (len(self._Icons) -1):
            return

        cur_icon = self._Icons[self._IconIndex]
        if self._Ps._OnShow == False:
            return
        if cur_icon._MyType == ICON_TYPES["EXE"]:
            print("IconClick: %s %d"%(cur_icon._CmdPath,cur_icon._Index))
            self._Screen.RunEXE(cur_icon._CmdPath)
            
        elif cur_icon._MyType == ICON_TYPES["DIR"]:
            child_page = self._Icons[self._IconIndex]._LinkPage
            if child_page != None:
                child_page.Draw()
                self._Screen._MyPageStack.Push(self._Screen._CurrentPage)
                self._Screen._CurrentPage = child_page
        elif cur_icon._MyType == ICON_TYPES["FUNC"]:
            print("IconClick API: %d"%(cur_icon._Index))
            #print("%s"% cur_icon._CmdPath)
            api_cb = getattr(cur_icon._CmdPath,"API",None)
            if api_cb != None:
                if callable(api_cb):
                    cur_icon._CmdPath.API(self._Screen)
        elif cur_icon._MyType == ICON_TYPES["Emulator"]:
            cur_icon._CmdPath.API(self._Screen)
            
    def ReturnToUpLevelPage(self):
        pop_page,ok = self._Screen._MyPageStack.Pop()
        if ok == True:
            #self._Screen._CurrentPage.ResetPageSelector()
            pop_page.Draw()
            self._Screen._CurrentPage = pop_page
            on_return_back_cb = getattr(self._Screen._CurrentPage,"OnReturnBackCb",None)
            if on_return_back_cb != None:
                if callable(on_return_back_cb):
                    self._Screen._CurrentPage.OnReturnBackCb()
        else:
            if self._Screen._MyPageStack.Length() == 0:
                if len(self._Screen._Pages) > 0:
                    self._Screen._CurrentPage = self._Screen._Pages[self._Screen._PageIndex]
                    self._Screen._CurrentPage.Draw()
                    print("OnTopLevel ",self._Screen._PageIndex)

    def ClearCanvas(self):
        self._CanvasHWND.fill(self._Screen._SkinManager.GiveColor("White")) 

    def ClearIcons(self):
        for i in range(0,self._IconNumbers):
            self._Icons[i].Clear()

    def DrawIcons(self):
        for i in range(0,self._IconNumbers):
            self._Icons[i].Draw()
            

    def KeyDown(self,event):##default keydown,every inherited page class should have it's own KeyDown
        if event.key == CurKeys["A"]:
            if self._FootMsg[3] == "Back":
                self.ReturnToUpLevelPage()
                self._Screen.Draw()
                self._Screen.SwapAndShow()
                return
    
        if event.key == CurKeys["Menu"]:
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["Right"]:
            if self.MoveIconIndexNext() == True:
                if self._IconIndex == (self._IconNumbers -1) or self._PrevIconIndex == 0:
                    self.IconSmoothUp(icon_width+ self._PageIconMargin) # only move up selected icon,no horizontal translation
                else:
                    self.IconsEasingLeft(icon_width + self._PageIconMargin)

                self._PsIndex  = self._IconIndex
                self._Screen.Draw()
                self._Screen.SwapAndShow()
                
            
        if event.key == CurKeys["Left"]:
            if self.MoveIconIndexPrev() == True:
                if self._IconIndex == 0 or self._PrevIconIndex == (self._IconNumbers -1):
                    self.IconSmoothUp(icon_width+ self._PageIconMargin)
                else:
                    self.IconsEasingRight(icon_width + self._PageIconMargin)

                self._PsIndex = self._IconIndex
                self._Screen.Draw()
                self._Screen.SwapAndShow()
                
        if event.key == CurKeys["Enter"]:
            self.IconClick()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

    def Draw(self):
        self.ClearCanvas()
        self.DrawIcons()
        self.DrawPageSelector()


