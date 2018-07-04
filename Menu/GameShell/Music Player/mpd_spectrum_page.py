# -*- coding: utf-8 -*- 

import time
import pygame

from numpy import fromstring,ceil,abs,log10,isnan,isinf,int16
from numpy import fft as Fft

import gobject

from beeprint import pp

## local UI import
from UI.constants import Width,Height
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.fonts  import fonts
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys

from Queue import Queue, Empty
from threading  import Thread



from list_item  import ListItem

import myvars

class PIFI(object):
    _MPD_FIFO = "/tmp/mpd.fifo"
    _SAMPLE_SIZE = 256
    _SAMPLING_RATE = 44100
    _FIRST_SELECTED_BIN = 5
    _NUMBER_OF_SELECTED_BINS = 10
    _SCALE_WIDTH = Height/2 - 20

    count = 0
    average = 0
    
    def __init__(self):
        self.sampleSize = self._SAMPLE_SIZE
        self.samplingRate = self._SAMPLING_RATE
        self.firstSelectedBin = self._FIRST_SELECTED_BIN
        self.numberOfSelectedBins = self._NUMBER_OF_SELECTED_BINS
        
        # Initialization : frequency bins
        freq = Fft.fftfreq(self.sampleSize) * self.samplingRate
        freqR = freq[:self.sampleSize/2]
        self.bins = freqR[self.firstSelectedBin:self.firstSelectedBin+self.numberOfSelectedBins]
        
        self.resetSmoothing()
    
    def resetSmoothing(self):
        self.count = 0
        self.average = 0
        
    def smoothOut(self, x):
        self.count += 1
        self.average = (self.average*self.count + x) / (self.count+1)
        return self.average
    
    def scaleList(self, _list):
        for i,x in enumerate(_list):
            if isnan(x) or isinf(x):
                _list[i] = 0

        # Compute a simple just-above 'moving average' of maximums
        maximum = 1.1*self.smoothOut(max( _list ))
        if maximum == 0:
            scaleFactor = 0.0
        else:
            scaleFactor = self._SCALE_WIDTH/float(maximum)
            
        # Compute the scaled list of values
        scaledList = [int(x*scaleFactor) for x in _list ]
        return scaledList
        
    def computeSpectrum(self, fifoFile):
        
        # Read PCM samples from fifo
        rawSamples = fifoFile.read(self.sampleSize)    # will return empty lines (non-blocking)
        if len(rawSamples) == 0:
            print("computeSpectrum read zero")
            return [],[]
        else:
            pass
##            print("computeSpectrum %d " % len(rawSamples))
            
        pcm = fromstring(rawSamples, dtype=int16)
        
        # Normalize [-1; +1]
        pcm = pcm / (2.**15)
        
        # Compute FFT
        N = pcm.size
        fft = Fft.fft(pcm)
        uniquePts = ceil((N+1)/2.0)
        fft = fft[0:int(uniquePts)]
        
        # Compute amplitude spectrum
        amplitudeSpectrum = abs(fft) / float(N)
        
        # Compute power spectrum
        p = amplitudeSpectrum**2
        
        # Multiply by two to keep same energy
        # See explanation:
        # https://web.archive.org/web/20120615002031/http://www.mathworks.com/support/tech-notes/1700/1702.html
        if N % 2 > 0: 
            # odd number of points
            # odd nfft excludes Nyquist point
            p[1:len(p)] = p[1:len(p)] * 2 
        else:
            # even number of points
            p[1:len(p) -1] = p[1:len(p) - 1] * 2
        
        # Power in logarithmic scale (dB)
        logPower = 10*log10(p)
        
        # Compute RMS from power
        #rms = numpy.sqrt(numpy.sum(p))
        #print "RMS(power):", rms
        
        # Select a significant range in the spectrum
        spectrum = logPower[self.firstSelectedBin:self.firstSelectedBin+self.numberOfSelectedBins]
            
        # Scale the spectrum 
        scaledSpectrum = self.scaleList(spectrum)
        
        return (self.bins, scaledSpectrum)
    

class MPDSpectrumPage(Page):

    _Icons = {}
    _Selector=None
    _FootMsg = ["Nav","","","Back",""]
    _MyList = []
    _ListFont = fonts["veramono12"]

    _PIFI   =  None
    _FiFo   = None
    _Color  = pygame.Color(126,206,244)
    _GobjectIntervalId = -1
    _Queue = None
    _KeepReading = True
    
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

        self.Start()

        self._GobjectIntervalId = gobject.timeout_add(50,self.Playing)
        
    def Start(self):
        
        try:
            self._FIFO = open(self._PIFI._MPD_FIFO)
            q = Queue()
            self._Queue = q
            
            t = Thread(target=self.GetSpectrum)
            t.daemon = True # thread dies with the program
            t.start()
            
        except IOError:
            print("open %s failed"%self._PIFI._MPD_FIFO)
            self._FIFO = None
            return


    def GetSpectrum(self):
        if self._FIFO == None:
            print("self._FIFO none")
            return
        
        (bins,scaledSpectrum) = self._PIFI.computeSpectrum(self._FIFO)
        self._Queue.put( scaledSpectrum )

        self._KeepReading = False
        
        return ## Thread ends

    def Playing(self):
        if self._Screen.CurPage() == self:
            if self._KeepReading == False:
                self._KeepReading = True
                
                t = Thread(target=self.GetSpectrum)
                t.daemon=True
                t.start()
                
            self._Screen.Draw()
            self._Screen.SwapAndShow()
            
        else:
            
            return False
        
        return True
    
    def OnLoadCb(self):

        if self._Queue != None:
            with self._Queue.mutex:
                self._Queue.queue.clear()
        
        try:
            if self._GobjectIntervalId != -1:
                gobject.source_remove(self._GobjectIntervalId)
        except:
            pass
        
        self._GobjectIntervalId = gobject.timeout_add(50,self.Playing)

    
    def KeyDown(self,event):
        if event.key == CurKeys["Menu"] or event.key == CurKeys["A"]:
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

        bw = 10
        spects = None
        try:
            spects = self._Queue.get_nowait()
#            print("get_nowait: " , spects)
        except Empty:
            return
        else: # got line
            if len(spects) == 0:
                return
            w = self._Width / len(spects)
            left_margin = (w-bw)/2
            for i,v in enumerate(spects):
                pygame.draw.rect(self._CanvasHWND,self._Color,(i*w+left_margin,self._Height-v,bw,v),0)
        
