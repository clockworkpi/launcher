# -*- coding: utf-8 -*- 

from sound_page import SoundPage

import myvars

def InitSoundPage(main_screen):

    myvars.SoundPage = SoundPage()
    
    myvars.SoundPage._Screen = main_screen
    myvars.SoundPage._Name = "Sound volume"
    myvars.SoundPage.Init()
