# -*- coding: utf-8 -*- 

import pygame
#import math
#import  commands
import dbus
#from beeprint import pp
from libs.roundrects import aa_round_rect
from UI.page   import Page,PageSelector
from UI.keys_def   import CurKeys, IsKeyMenuOrB
from libs.DBUS import  bus, adapter,devices


BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/gameshell/bleagent"

class Rejected(dbus.DBusException):
	_dbus_error_name = "org.bluez.Error.Rejected"

class BleAgent(dbus.service.Object):
    device_obj = None
    _Leader = None
    dev_path = ""
    
    def set_trusted(self,path):
        global BUS_NAME
        props = dbus.Interface(bus.get_object(BUS_NAME, path),
                        "org.freedesktop.DBus.Properties")
        props.Set("org.bluez.Device1", "Trusted", True)    
        
    def dev_connect(self,path):
        global BUS_NAME
        dev = dbus.Interface(bus.get_object(BUS_NAME, path),
                                "org.bluez.Device1")
                                
        print("dev_connect %s" % path)
        try:
            dev.Connect() 
        except Exception,e:
            print(str(e))
    
    @dbus.service.method(AGENT_INTERFACE,in_signature="", out_signature="")
    def Release(self):
        print("Agent release")
        

    @dbus.service.method(AGENT_INTERFACE,in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        print("AuthorizeService (%s, %s)" % (device, uuid)) ## directly authrized
        return

    @dbus.service.method(AGENT_INTERFACE,in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("RequestPinCode (%s)" % (device))
        set_trusted(device)
        return "0000"

    @dbus.service.method(AGENT_INTERFACE,in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey (%s)" % (device))
        set_trusted(device)
        passkey = "000000"
        return dbus.UInt32(passkey)

    @dbus.service.method(AGENT_INTERFACE,in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey (%s, %06u entered %u)" % (device, passkey, entered))
        self._Leader._PairPage.ShowPassKey(device,passkey,entered)
        
    @dbus.service.method(AGENT_INTERFACE,in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode (%s, %s)" % (device, pincode))
        self._Leader._PairPage.ShowPinCode(device,pincode)
        
    @dbus.service.method(AGENT_INTERFACE,in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print("RequestConfirmation (%s, %06d)" % (device, passkey))
        set_trusted(device)
        return

    @dbus.service.method(AGENT_INTERFACE,in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print("RequestAuthorization (%s)" % (device))
        
        return

    @dbus.service.method(AGENT_INTERFACE,in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")
    
    
    def pair_reply(self):
        print("Device paired under Agent")
        self.set_trusted(self.dev_path)
        self.dev_connect(self.dev_path)
        
        self._Leader._PairPage._dev_obj = self.device_obj
        self._Leader._PairPage.PairReplyCb()
        
    def pair_error(self,error):
        global adapter
        err_msg = ""
        err_name = error.get_dbus_name()
        print(err_name)
        if err_name == "org.freedesktop.DBus.Error.NoReply" and self.device_obj:
            err_msg = "Timed out. Cancelling pairing"
            print(err_msg)
            self.device_obj.CancelPairing()
        elif err_name == "org.bluez.Error.AuthenticationCanceled":
            err_msg = "Authentication Canceled"
        elif err_name == "org.bluez.Error.ConnectionAttemptFailed":
            err_msg = "Page Timeout"
        elif err_name == "org.bluez.Error.AlreadyExists":
            err_msg ="Already Exists"
            try:
                adapter.RemoveDevice(self.device_obj)
            except Exception,e:
                print("pair_error forget err:",str(e))
        
        elif err_name == "org.bluez.Error.AuthenticationFailed":
            err_msg = "Authentication Failed"
        else:    
            err_msg = "Pair error"
            print( err_name,str(error) )
            
        self.device_obj = None
        self._Leader._PairPage.PairErrorCb(err_msg)

class BleAgentPairPage(Page):
    
    ##show pin/password 
    ##show prompt 
    _Pin = ""
    _Pass = ""
    _dev_obj = None
    _FootMsg    = ["Nav","","","Back",""]
    
    def Init(self):
        self._PosX = self._Index * self._Screen._Width
        self._Width = self._Screen._Width
        self._Height = self._Screen._Height  
    
        #self._CanvasHWND = pygame.Surface((self._Width,self._Height))
        self._CanvasHWND = self._Screen._CanvasHWND
    
    def ShowPinCode(self,device,pincode):
        print("ShowPinCode %s %s" % (device,pincode))
        if self._Screen.CurPage() != self:
            self._Screen.PushPage(self)
            self.ClearCanvas()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
        self._Pin = "%s" % pincode
        txt = self.Pin
        if len(self._Pin) > 0:
            txt = "Pin code: %s" % self._Pin
        self._Screen._MsgBox.SetText(txt)
        self._Screen._MsgBox.Draw()
        self._Screen.SwapAndShow() 
        
    def ShowPassKey(self,device,passkey,entered):
        print("ShowPassKey %06u %u" % (passkey,entered))
        if self._Screen.CurPage() != self:
            self._Screen.PushPage(self)
            self.ClearCanvas()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
        
        self._Pass = "%06u" % passkey
        if len(self._Pass) > 0:
            txt = "Pair code: %s" % self._Pass
        self._Screen._MsgBox.SetText(txt)
        self._Screen._MsgBox.Draw()
        self._Screen.SwapAndShow() 
        
    def PairReplyCb(self):
        self.ClearCanvas()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
        self._Screen._MsgBox.SetText("Device paired")
        self._Screen._MsgBox.Draw()
        self._Screen.SwapAndShow()
        pygame.time.delay(1500)
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()        
        self._Screen._FootBar.ResetNavText()
        
    def PairErrorCb(self,error=None):
        self.ClearCanvas()
        self._Screen.Draw()
        self._Screen.SwapAndShow()
            
        self._Screen._MsgBox.SetText(error)
        self._Screen._MsgBox.Draw()
        self._Screen.SwapAndShow()
        pygame.time.delay(1500)
        self.ReturnToUpLevelPage()
        self._Screen.Draw()
        self._Screen.SwapAndShow()         
        self._Screen._FootBar.ResetNavText()        
        
    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
            if self._dev_obj != None:
                try:
                    self._dev_obj.CancelPairing()
                except Exception,e:
                    print(str(e))
            
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()
    
    
    def Draw(self):
        pass
        #self.ClearCanvas()
        
    
    
