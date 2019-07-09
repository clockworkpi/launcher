# -*- coding: utf-8 -*- 
import os
import platform
from UI.util_funcs   import FileExists,ArmSystem

CurKeySet = "GameShell" ## >>>    PC or GameShell   <<<

DontLeave = False

BackLight = "/proc/driver/backlight"
Battery   = "/sys/class/power_supply/axp20x-battery/uevent"


MPD_socket = "/tmp/mpd.socket"

UPDATE_URL="https://raw.githubusercontent.com/clockworkpi/CPI/master/launcher_ver0.4.json"

VERSION="stable 1.25"

SKIN=None

ButtonsLayout="xbox"

## three timer values in seconds: dim screen, close screen,PowerOff
## zero means no action
PowerLevels = {}
PowerLevels["supersaving"] = [10,30,120]
PowerLevels["powersaving"] = [40,120,300]
PowerLevels["server"]      = [40,120,0]
PowerLevels["balance_saving"] = [40,0,0]

PowerLevel = "balance_saving"

def PreparationInAdv():
    global SKIN,ButtonsLayout
    global PowerLevel
    
    if SKIN != None:
        return

    SKIN= "../skin/default"
    
    if FileExists("%s/.gameshell_skin" % os.path.expanduser('~')) == True:
        with open("%s/.gameshell_skin" % os.path.expanduser('~'),"r") as f:
          gameshell_skin = f.read()
        
        gameshell_skin = gameshell_skin.strip()
        SKIN= gameshell_skin
        
    if FileExists(".buttonslayout") == True:
        with open(".buttonslayout") as f:
            btnlayout = f.read()
        
        btnlayout = btnlayout.strip()
        ButtonsLayout = btnlayout
        if ButtonsLayout != "xbox" and ButtonsLayout != "snes":
            ButtonsLayout = "xbox"
        
    if FileExists(".powerlevel") == False:
        os.system("touch .powerlevel")
    
    with open(".powerlevel","r") as f:
        powerlevel = f.read()
    
    powerlevel = powerlevel.strip()
    if powerlevel != "":
        PowerLevel = powerlevel
        if powerlevel != "supersaving":
            ArmSystem("sudo iw wlan0 set power_save off >/dev/null")
        else:
            ArmSystem("sudo iw wlan0 set power_save on > /dev/null")
    else:
        ArmSystem("sudo iw wlan0 set power_save off >/dev/null")

PreparationInAdv()
##sys.py/.powerlevel

