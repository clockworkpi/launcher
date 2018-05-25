# -*- coding: utf-8 -*- 


#import dbus
#import dbus.service
#from wicd import misc 
##misc.to_bool
##misc.misc.noneToString
##misc.to_unicode
##misc.Noneify
#from wicd.translations import _
#from wicd import wpath
#from wicd import dbusmanager


## local UI import
from libs.DBUS      import bus,daemon,wireless,wired

from keyboard import Keyboard
from wifi_list import WifiList

import myvars


def InitScanPage(main_screen):
    global wireless
    global daemon
    global bus
    
    myvars.ScanPage = WifiList()
    myvars.ScanPage._Name = "Scan wifi"
   
    myvars.ScanPage._Wireless = wireless
    myvars.ScanPage._Daemon = daemon
    myvars.ScanPage._Dbus = bus
   

    myvars.ScanPage._Screen = main_screen
    myvars.ScanPage.Init()


    if daemon != None:
        #Bind signals
        myvars.ScanPage._Dbus.add_signal_receiver(myvars.ScanPage.DbusScanFinishedSig, 'SendEndScanSignal',
                                                  'org.wicd.daemon.wireless')
        myvars.ScanPage._Dbus.add_signal_receiver(myvars.ScanPage.DbusScanStarted, 'SendStartScanSignal',
                                                  'org.wicd.daemon.wireless')
        #
        myvars.ScanPage._Dbus.add_signal_receiver(myvars.ScanPage.DbusDaemonStatusChangedSig, 'StatusChanged',
                                                  'org.wicd.daemon')
        myvars.ScanPage._Dbus.add_signal_receiver(myvars.ScanPage.DbusConnectResultsSent, 'ConnectResultsSent',
                                                  'org.wicd.daemon')

def InitPasswordPage(main_screen):

    myvars.PasswordPage = Keyboard()
    myvars.PasswordPage._Name = "Enter wifi password"

    myvars.PasswordPage._Screen = main_screen
    myvars.PasswordPage.Init()

