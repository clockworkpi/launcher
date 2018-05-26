# GameShell launcher
This is the launcher for GameShell based on 320x240 resolution and D-Pad layout.

# Directory structure
/home/cpi/
├── apps
│   ├── emulators
│   └── launcher
│       ├── Menu
│       ├── sys.py
│       └── truetype
├── games
│   ├── FreeDM
│   ├── GBX
│   ├── MAME
│   ├── NES
│   └── nxengine
└── music

# Dependent packages
* validators, numpy, requests, python-mpd2, beeprint, python-pycurl, python-alsaaudio, python-pygame, python-gobject, python-xlib, python-wicd
* wicd (For Wi-Fi)
* mpd (For music player)

## Install dependent packages
```
sudo apt-get -y install mpd ncmpcpp git libuser
sudo apt-get -y install python-wicd  wicd wicd-curses python-pycurl python-alsaaudio python-pygame python-gobject python-xlib   

sudo apt-get -y install python-pip   
sudo pip install validators numpy requests python-mpd2
```
