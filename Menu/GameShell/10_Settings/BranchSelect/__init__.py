import git

from libs.roundrects import aa_round_rect

from UI.constants import Width
from UI.page import Page, PageSelector
from UI.scroller import ListScroller
from UI.info_page_list_item import InfoPageListItem
from UI.keys_def import CurKeys, IsKeyStartOrA, IsKeyMenuOrB
from UI.skin_manager import MySkinManager
from UI.lang_manager import MyLangManager

class SelectPage(Page):
    _MyList = []

    def __init__(self):
        Page.__init__(self)
        self._Icons = {}
    
    def Init(self):
        self._ListFontObj = MyLangManager.TrFont("varela15")
        self._ListSmFontObj = MySkinManager.GiveFont("varela12")
        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._HWND = self._Screen._CanvasHWND
                self._CanvasHWND = self._Screen._CanvasHWND
        
        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height

        ps = GamePageSelector()
        ps._Parent = self 

        self._Ps = ps
        self._PsIndex = 0

        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = 2
        self._Scroller._PosY = 2
        self._Scroller.Init()
    
    def Generate(self, game, branches, current):
        start_x  = 0
        start_y  = 0
        i = 0
        self._Game = game

        for branch in branches:
            li = InfoPageListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + i*InfoPageListItem._Height

            li._Width  = Width
            li._Fonts["normal"] = self._ListFontObj
            
            li._Fonts["small"] = self._ListSmFontObj
            
            li._LinkObj = branch

            li.Init(branch)
            
            if branch == current:
                self._PsIndex = i

            li._PosX = 2
            self._MyList.append(li)

            i = i + 1
    
    def Draw(self):
        self.ClearCanvas()
        if len(self._MyList) * InfoPageListItem._Height > self._Height:
            self._Ps._Width = self._Width - 10
            self._Ps._PosX  = 9
            self._Ps.Draw()        
            for i in self._MyList:
                i.Draw()
            
            self._Scroller.UpdateSize(len(self._MyList)*InfoPageListItem._Height, self._PsIndex*InfoPageListItem._Height)
            self._Scroller.Draw()
        
        else:
            self._Ps._Width = self._Width
            self._Ps.Draw()
            for i in self._MyList:
                i.Draw()
    
    def KeyDown(self, event):
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
        if event.key == CurKeys["Up"]:
            self.ScrollUp()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        if event.key == CurKeys["Down"]:
            self.ScrollDown()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
        if IsKeyStartOrA(event.key):
            self.Click()
    
    def Click(self):
        if self._PsIndex >= len(self._MyList):
            return
        
        cur_li = self._MyList[self._PsIndex]
        git.checkout_branch(self._Game, cur_li._LinkObj)


class GamePageSelector(PageSelector):
    _BackgroundColor = MySkinManager.GiveColor('Front')

    def __init__(self):
        self._PosX = 0
        self._PosY = 0
        self._Height = 0
    
    def AnimateDraw(self, x2, y2):
        pass 

    def Draw(self):
        idx = self._Parent._PsIndex
        if idx < len( self._Parent._MyList):
            x = self._PosX+2
            y = self._Parent._MyList[idx]._PosY+1
            h = self._Parent._MyList[idx]._Height -3
        
            self._PosX = x
            self._PosY = y
            self._Height = h

            aa_round_rect(self._Parent._CanvasHWND,  
                          (x,y,self._Width-4,h),self._BackgroundColor,4,0,self._BackgroundColor)

class BranchSelectPage(Page):
    _MyList = []

    def __init__(self):
        Page.__init__(self)
        self._Icons = {}
    
    def Init(self):
        self._SubPage = SelectPage()
        self._SubPage._Screen = self._Screen
        self._SubPage._Name = "Select Branch"
        self._SubPage.Init()

        self._ListFontObj = MyLangManager.TrFont("varela15")
        self._ListSmFontObj = MySkinManager.GiveFont("varela12")
        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._HWND = self._Screen._CanvasHWND
                self._CanvasHWND = self._Screen._CanvasHWND
        
        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height

        ps = GamePageSelector()
        ps._Parent = self 

        self._Ps = ps
        self._PsIndex = 0

        self._Scroller = ListScroller()
        self._Scroller._Parent = self
        self._Scroller._PosX = 2
        self._Scroller._PosY = 2
        self._Scroller.Init()

        start_x  = 0
        start_y  = 0
        i = 0
        games = git.get_games()
        for game in games:
            li = InfoPageListItem()
            li._Parent = self
            li._PosX   = start_x
            li._PosY   = start_y + i*InfoPageListItem._Height

            li._Width  = Width
            li._Fonts["normal"] = self._ListFontObj
            
            li._Fonts["small"] = self._ListSmFontObj
            
            li._LinkObj = game

            li.Init( game.split("/")[-1] )
            
            sm_text = str(len(git.get_branches(game)[0]))
            li.SetSmallText(sm_text)
            
            li._PosX = 2
            self._MyList.append(li)

            i = i + 1
    
    def Draw(self):
        self.ClearCanvas()
        if len(self._MyList) * InfoPageListItem._Height > self._Height:
            self._Ps._Width = self._Width - 10
            self._Ps._PosX  = 9
            self._Ps.Draw()        
            for i in self._MyList:
                i.Draw()
            
            self._Scroller.UpdateSize(len(self._MyList)*InfoPageListItem._Height, self._PsIndex*InfoPageListItem._Height)
            self._Scroller.Draw()
        
        else:
            self._Ps._Width = self._Width
            self._Ps.Draw()
            for i in self._MyList:
                i.Draw()
    
    def KeyDown(self, event):
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
        if event.key == CurKeys["Up"]:
            self.ScrollUp()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        if event.key == CurKeys["Down"]:
            self.ScrollDown()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
        if IsKeyStartOrA(event.key):
            self.Click()
    
    def Click(self):
        if self._PsIndex >= len(self._MyList):
            return
        
        cur_li = self._MyList[self._PsIndex]
        branches, current = git.get_branches(cur_li._LinkObj)

        self._SubPage.Generate(cur_li._LinkObj, branches, current)
        self._Screen.PushPage(self._SubPage)
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        

class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = BranchSelectPage()
        self._Page._Screen = main_screen
        self._Page._Name ="Branch Select"
        self._Page.Init()
        
    def API(self,main_screen):
        if main_screen !=None:
            main_screen.PushPage(self._Page)
            main_screen.Draw()
            main_screen.SwapAndShow()

OBJ = APIOBJ()
def Init(main_screen):    
    OBJ.Init(main_screen)
def API(main_screen):
    OBJ.API(main_screen)