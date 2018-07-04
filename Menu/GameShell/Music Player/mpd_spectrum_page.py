# -*- coding: utf-8 -*- 

import time
import pygame

from numpy import fromstring,ceil,abs,log10,isnan,isinf,int16,sqrt,mean
from numpy import fft as Fft

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

    rmscount=0
    rmsaverage=0
    
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
        self.rmscount = 0
        self.rmsaverage = 0

    def rms_smoothOut(self, x):
        self.rmscount += 1
        self.rmsaverage = (self.rmsaverage*self.rmscount + x) / (self.rmscount+1)
        return self.rmsaverage
    
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

        # Compute RMS directly from signal
        rms = sqrt(mean(pcm**2))
        # Compute a simple 'moving maximum'
        maximum = 2*self.rms_smoothOut(rms)
        if maximum == 0:
            scaleFactor = 0.0
        else:
            scaleFactor = self._SCALE_WIDTH/float(maximum)
        
        final_rms = int(rms*scaleFactor)
        
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
        scaledSpectrum.append( final_rms)
        return scaledSpectrum
    

class MPDSpectrumPage(Page):

    _Icons = {}
    _Selector=None
    _FootMsg = ["Nav","","","Back",""]
    _MyList = []
    _ListFont = fonts["veramono12"]

    _PIFI   =  None
    _FIFO   = None
    _Color  = pygame.Color(126,206,244)
    _GobjectIntervalId = -1
    _Queue = None
    _KeepReading = True

    _BGpng = None
    _BGwidth = 320
    _BGheight = 200

    _SheepHead = None
    _SheepHeadW = 69
    _SheepHeadH = 66

    _SheepBody = None
    _SheepBodyW = 105
    _SheepBodyH = 81

    _freq_count = 0
    _head_dir = 0

    _Neighbor = None
    
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
        
        scaledSpectrum = self._PIFI.computeSpectrum(self._FIFO)
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
        if self._FIFO == None:
            self.Start()
            
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
            if self._FIFO != None and self._FIFO.closed == False:
                try:
                    self._FIFO.close()
                    self._FIFO = None
                except Exception, e:
                    print(e)
                
            
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
            spects = self._Queue.get_nowait() ## last element is rms
#            print("get_nowait: " , spects)
        except Empty:
            return
        else: # got line
            if len(spects) == 0:
                return
            w = self._Width / len( spects[0:-1] )
            left_margin = (w-bw)/2
            for i,v in enumerate(spects[0:-1]):
                pygame.draw.rect(self._CanvasHWND,self._Color,(i*w+left_margin,self._Height-v,bw,v),0)
        


    
