# -*- coding: utf-8 -*- 

import os
import time
import pygame

import numpy
import math

import gobject

from beeprint import pp

## local UI import
from UI.constants import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.fonts  import fonts
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys
from UI.icon_item import IconItem
from UI.icon_pool  import MyIconPool

from threading  import Thread

from list_item  import ListItem

import myvars

class PIFI(object):
    _MPD_FIFO = "/tmp/mpd.fifo"
    _SAMPLE_SIZE = 1024
    _SAMPLING_RATE = 44100
    _FIRST_SELECTED_BIN = 5
    _NUMBER_OF_SELECTED_BINS = 1024

    
    def __init__(self):
        self.sampleSize = self._SAMPLE_SIZE
        self.samplingRate = self._SAMPLING_RATE
        
    def GetSpectrum(self,fifoFile,trim_by=10,log_scale=False,div_by=100):
        try:
            rawSamples = os.read(fifoFile,self.sampleSize)    # will return empty lines (non-blocking)
            if len(rawSamples) < 1:
#                print("Read error")
                return rawSamples
        except Exception,e:
            return ""
    
        data = numpy.fromstring(rawSamples, dtype=numpy.int16)

        data = data * numpy.hanning(len(data))

        left,right = numpy.split(numpy.abs(numpy.fft.fft(data)),2)
        spec_y     = numpy.add(left,right[::-1])

        if log_scale:
            spec_y=numpy.multiply(20,numpy.log10(spec_y))
        if trim_by:
            i=int((self.sampleSize/2)/trim_by)
            spec_y=spec_y[:i]
        if div_by:
            spec_y=spec_y/float(div_by)
        
        return spec_y
    
    
class MPDSpectrumPage(Page):

    _Icons = {}
    _Selector=None
    _FootMsg = ["Nav","","","Back",""]
    _MyList = []
    _ListFont = fonts["veramono12"]
    _SongFont = fonts["notosanscjk12"]
    _PIFI   =  None
    _FIFO   = None
    _Color  = pygame.Color(126,206,244)
    _GobjectIntervalId = -1
    _Queue = None
    _KeepReading = True
    _ReadingThread = None
    
    _BGpng = None
    _BGwidth = 320
    _BGheight = 200

    _SheepHead = None
    _SheepHeadW = 69
    _SheepHeadH = 66

    _SheepBody = None
    _SheepBodyW = 105
    _SheepBodyH = 81

    _RollCanvas = None
    _RollW     = 180
    _RollH     = 18
    
    _freq_count = 0
    _head_dir = 0

    _Neighbor = None


    _bby  = []
    _bbs  = []
    _capYPositionArray = []
    _frames = 0
    read_retry = 0
    _queue_data = []
    _vis_values = []
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}
        self._CanvasHWND = None
        self._MyList = []
        self._PIFI = PIFI()
            
    def Init(self):
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height

        self._CanvasHWND = self._Screen._CanvasHWND
        self._RollCanvas = pygame.Surface(( self._RollW,self._RollH))
        
        """
        self._BGpng = IconItem()
        self._BGpng._ImgSurf = MyIconPool._Icons["sheep_bg"]
        self._BGpng._MyType = ICON_TYPES["STAT"]
        self._BGpng._Parent = self
        self._BGpng.Adjust(0,0,self._BGwidth,self._BGheight,0)
        
        self._SheepHead = IconItem()
        self._SheepHead._ImgSurf = MyIconPool._Icons["sheep_head"]
        self._SheepHead._MyType = ICON_TYPES["STAT"]
        self._SheepHead._Parent = self
        self._SheepHead.Adjust(0,0,self._SheepHeadW,self._SheepHeadH,0)

        self._SheepBody = IconItem()
        self._SheepBody._ImgSurf = MyIconPool._Icons["sheep_body"]
        self._SheepBody._MyType = ICON_TYPES["STAT"]
        self._SheepBody._Parent = self
        self._SheepBody.Adjust(0,0,self._SheepBodyW,self._SheepBodyH,0)
        """
        
        self._cwp_png = IconItem()
        self._cwp_png._ImgSurf = MyIconPool._Icons["tape"]
        self._cwp_png._MyType = ICON_TYPES["STAT"]
        self._cwp_png._Parent = self
        self._cwp_png.Adjust(0,0,79,79,0)


        self._song_title = Label()
        self._song_title.SetCanvasHWND(self._RollCanvas)
        self._song_title.Init("Untitled",self._SongFont,(255,255,255))


        self._title = Label()
        self._title.SetCanvasHWND(self._CanvasHWND)
        self._title.Init("Title:",self._ListFont,(255,255,255))

        self._time = Label()
        self._time.SetCanvasHWND(self._CanvasHWND)
        self._time.Init("Time:",self._ListFont,(255,255,255))        


        self._time2 = Label()
        self._time2.SetCanvasHWND(self._CanvasHWND)
        self._time2.Init("00:00-00:00",self._ListFont,(255,255,255))        

        
        self.Start()
                
    def Start(self):

        if self._Screen.CurPage() != self:
            return
        
        try:
            self._FIFO = os.open(self._PIFI._MPD_FIFO, os.O_RDONLY | os.O_NONBLOCK)
            
            t = Thread(target=self.GetSpectrum)
            t.daemon = True # thread dies with the program
            t.start()
            self._ReadingThread = t
            
        except IOError:
            print("open %s failed"%self._PIFI._MPD_FIFO)
            self._FIFO = None
            return


    def GetSpectrum(self):
        while self._KeepReading and self._FIFO != None:
            raw_samples = self._PIFI.GetSpectrum(self._FIFO)
            if len(raw_samples) < 1:
                #print("sleeping... 0.01")
                time.sleep(0.01)
                self.read_retry+=1
                if self.read_retry > 40:
                    os.close(self._FIFO)
                    self._FIFO = os.open(self._PIFI._MPD_FIFO, os.O_RDONLY | os.O_NONBLOCK)
                    self.read_retry = 0
                
                self.Playing()
                
            else:
                self.read_retry = 0
                self._queue_data = raw_samples
                self.Playing()        
        

    def Playing(self):
        
        self._Screen.Draw()
        self._Screen.SwapAndShow()


    def ClearCanvas(self):
        self._CanvasHWND.fill((0,0,0))

    def SgsSmooth(self):
        passes = 1
        points = 3
        origs = self._bby[:]
        for p in range(0,passes):
            pivot = int(points/2.0)
            
            for i in range(0,pivot):
                self._bby[i] = origs[i]
                self._bby[ len(origs) -i -1 ] = origs[ len(origs) -i -1 ]

            smooth_constant = 1.0/(2.0*pivot+1.0)
            for i in range(pivot, len(origs)-pivot):
                _sum = 0.0
                for j in range(0,(2*pivot)+1):
                    _sum += (smooth_constant * origs[i+j-pivot]) +j -pivot

                self._bby[i] = _sum

            if p < (passes - 1):
                origs = self._bby[:]
    
    def OnLoadCb(self):
        if self._Neighbor != None:
            pass
        
        if self._KeepReading == False:
            self._KeepReading = True
        
        if self._FIFO == None:
            self.Start()
            
    
    def KeyDown(self,event):
        if event.key == CurKeys["Menu"] or event.key == CurKeys["A"]:
            try:
                os.close(self._FIFO)
                self._FIFO = None
                    
            except Exception, e:
                print(e)
                
            self._KeepReading = False
            self._ReadingThread.join()
            self._ReadingThread = None
            
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if event.key == CurKeys["Start"]:
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
        if event.key == CurKeys["Enter"]:
            pass

        
    def Draw(self):
        self.ClearCanvas()
        self._frames+=1
        
        bw = 10
        gap = 2
        margin_bottom = 72

        spects = None
        meterNum =  self._Width / float(bw +gap )  ## 320/12= 26
        meter_left = meterNum - int(meterNum)
        meter_left = meter_left*int(bw+gap)
        margin_left = meter_left / 2 + gap
        meterNum = int(meterNum)
        
        self._cwp_png.NewCoord(43,159)
        self._cwp_png.Draw()

        if self._Neighbor != None:
            if self._Neighbor._CurSongName != "":
                self._song_title.SetText(self._Neighbor._CurSongName)
            if self._Neighbor._CurSongTime != "":
                times = self._Neighbor._CurSongTime
                times_ = times.split(":")
                if len(times_)> 1:
                    cur = int(times_[0])
                    end = int(times_[1])
                    if cur > 3600:
                        cur_text = time.strftime('%H:%M:%S', time.gmtime(cur))
                    else:
                        cur_text = time.strftime('%M:%S', time.gmtime(cur))

                    if end > 3600:
                        end_text = time.strftime('%H:%M:%S', time.gmtime(end))
                    else:
                        end_text = time.strftime('%M:%S', time.gmtime(end))
                else:
                    cur_text = ""
                    end_text = times
                
                self._time2.SetText(cur_text+"-"+end_text)
                
                
        self._title.NewCoord(90,167)
        self._title.Draw()

        self._time.NewCoord(90,140)
        self._time.Draw()

        self._time2.NewCoord(135,140)
        self._time2.Draw()
    
        if self._RollCanvas != None:
#            self._RollCanvas.fill((111,22,33))
            self._RollCanvas.fill((0,0,0))
            if self._song_title._Width > self._RollW:
                if (self._song_title._PosX + self._song_title._Width) > self._RollW and self._frames % 30 == 0:
                    self._song_title._PosX -= 1
                elif (self._song_title._PosX + self._song_title._Width) <= self._RollW and self._frames % 30 == 0:
                    self._song_title._PosX  = 0
            else:
                self._song_title._PosX = 0
            
            self._song_title.Draw()
            
            self._CanvasHWND.blit(self._RollCanvas,(135,165,self._RollW,self._RollH))
        
        
        try:
            spects = self._queue_data
            if len(spects) == 0:
                return
#            print("spects:",spects)
            step = int( round( len( spects ) / meterNum) )

            self._bbs = []

            for i in range(0,meterNum):
                index = int(i*step)
                total = 0
                
                value = spects[index]
                self._bbs.append(value)
            
            if len(self._bby) < len(self._bbs):
                self._bby = self._bbs
            elif len(self._bby) == len(self._bbs):
                for i in range(0,len(self._bbs)):
                    self._bby[i] = (self._bby[i]+self._bbs[i])/2
                    
            self.SgsSmooth()
            
            for i in range(0,meterNum):
                value = self._bby[ i ]
                if math.isnan(value) or math.isinf(value):
                    value = 0

                value = value/32768.0
                value = value * 100
                value = value %  (self._Height-gap-margin_bottom)
                
                if len(self._vis_values) < len(self._bby):
                    self._vis_values.append(value)
                elif len(self._vis_values) == len(self._bby):
                    if self._vis_values[i] < value:
                        self._vis_values[i] = value


        except Empty:
            return
        else: # got line
            if len(self._vis_values) == 0:
                return

            for i in range(0,meterNum):
                value = self._vis_values[i]
         
                if len(self._capYPositionArray) < round(meterNum):
                    self._capYPositionArray.append(value)

                if value < self._capYPositionArray[i]:
                    self._capYPositionArray[i]-=0.5
                else:
                    self._capYPositionArray[i] = value

                pygame.draw.rect(self._CanvasHWND,(255,255,255),(i*(bw+gap)+margin_left,self._Height-gap-self._capYPositionArray[i]-margin_bottom,bw,gap),0)
                
                pygame.draw.rect(self._CanvasHWND,(255,255,255),(i*(bw+gap)+margin_left,self._Height-value-gap-margin_bottom,bw,value+gap),0)
                
                self._vis_values[i] -= 2       


    
