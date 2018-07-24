# -*- coding: utf-8 -*- 

CurKeySet = "GameShell" ## >>>    PC or GameShell   <<<

DontLeave = False

BackLight = "/proc/driver/backlight"
Battery   = "/sys/class/power_supply/axp20x-battery/uevent"


MPD_socket = "/tmp/mpd.socket"

UPDATE_URL="https://raw.githubusercontent.com/clockworkpi/CPI/master/launcher_ver.json"

VERSION="stable 1.2"

SKIN="default"

## three timer values in seconds: dim screen, close screen,PowerOff
## zero means no action
PowerLevels = {}
PowerLevels["supersaving"] = [10,30,120]
PowerLevels["powersaving"] = [40,120,300]
PowerLevels["server"]      = [40,120,0]
PowerLevels["balance_saving"] = [40,0,0]

PowerLevel = "balance_saving"

##sys.py/.powerlevel

