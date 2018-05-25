

class Slider(object):
    _PosX = 0
    _PosY = 0
    _Width = 0
    _Height = 0
        
    _Value = 0
    _CanvasHWND = None
    
    _Range = []
    
    def __init__(self):
        self._Range = [0,255]

    def Init(self):
        self._Value = 0
        
    def SetValue(self,v):
        self._Value = int(v)

    def SetRange(self,m1,m2):
        if m1 >= m2:
            return
        
        self._Range[0] = m1
        self._Range[1] = m2


    def SetCanvasHWND(self,cav):
        self._CanvasHWND = cav
        
    def KeyDown(self):
        pass

    def Draw(self):
        pass

    
