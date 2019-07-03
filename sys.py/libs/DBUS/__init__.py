# -*- coding: utf-8 -*- 

import dbus
import dbus.service

import sys
from wicd import misc 
##misc.to_bool
##misc.misc.noneToString
##misc.to_unicode
##misc.Noneify
from wicd.translations import _
from wicd import wpath
from wicd import dbusmanager
from wicd import misc

import time
import gobject

if getattr(dbus, 'version', (0, 0, 0)) < (0, 80, 0):
    import dbus.glib
else:
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

bus = daemon = wireless = wired =  None

manager = objects = adapter  = None 
devices = {}

def setup_dbus(force=True):
    global bus,daemon,wireless,wired
    global manager,objects,adapter,devices
    
    try:
        dbusmanager.connect_to_dbus()
    except dbus.DBusException:
        print >> sys.stderr,\
            _("Can't connect to wicd daemon,trying to start it automatically...")
    else:
        bus = dbusmanager.get_bus()
        dbus_ifaces = dbusmanager.get_dbus_ifaces()
        daemon      = dbus_ifaces["daemon"] ## @dbus.service.method('org.wicd.daemon')
        wireless    = dbus_ifaces["wireless"] ## @dbus.service.method('org.wicd.daemon.wireless')
        wired       = dbus_ifaces["wired"]    ## @
        
    
        ### BlueZ
        try:
            proxy_obj = bus.get_object("org.bluez", "/")
            manager = dbus.Interface(proxy_obj,"org.freedesktop.DBus.ObjectManager")
            objects = manager.GetManagedObjects()
            
            for path, interfaces in objects.iteritems():
                if "org.bluez.Device1" in interfaces:
                    devices[path] = interfaces["org.bluez.Device1"] ## like /org/bluez/hci0/dev_xx_xx_xx_yy_yy_yy
        
            proxy_obj = bus.get_object("org.bluez", "/org/bluez/hci0")
            adapter = dbus.Interface(proxy_obj, "org.bluez.Adapter1")
        except Exception as e:
            print(str(e))
        
        if not daemon:
            print("Error connecting to wicd via D-Bus")

        
        
        
    return True


def wifi_strength():
    fast = not daemon.NeedsExternalCalls()
    if not fast:
        iwconfig = wireless.GetIwconfig()
    else:
        iwconfig = ''
    
    if daemon.GetSignalDisplayType() == 0:
        strength = wireless.GetCurrentSignalStrength(iwconfig)
    else:
        strength = wireless.GetCurrentDBMStrength(iwconfig)

    return strength


def get_wifi_ip():
    if wireless == None:
        return None
    return wireless.GetWirelessIP('')

def is_wifi_connected_now():
    if wireless == None:
        return False
    
    wireless_connecting = wireless.CheckIfWirelessConnecting()
    fast = not daemon.NeedsExternalCalls()        
    if wireless_connecting:
        return False
    else:
        if not fast:
            iwconfig = wireless.GetIwconfig()
        else:
            iwconfig = ''
        if check_for_wireless(iwconfig,wireless.GetWirelessIP(''),None):
            return True
        else:
            return False

def check_for_wireless(iwconfig,wireless_ip,set_status):
    if not wireless_ip:
        return False
    network = wireless.GetCurrentNetwork(iwconfig)
    if not network:
        return False
    network = misc.to_unicode(network)
    if daemon.GetSignalDisplayType() == 0:
        strength = wireless.GetCurrentSignalStrength(iwconfig)
    else:
        strength = wireless.GetCurrentDBMStrength(iwconfig)

    if strength is None:
        return False
    
    strength = misc.to_unicode(daemon.FormatSignalForPrinting(strength))
    ip = misc.to_unicode(wireless_ip)

    """
    print(_('dbus Connected to $A at $B (IP: $C)').replace
          ('$A', network).replace
          ('$B', strength).replace
          ('$C', ip))
    """
    return True
