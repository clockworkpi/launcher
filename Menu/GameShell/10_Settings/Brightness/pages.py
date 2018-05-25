# -*- coding: utf-8 -*- 

from brightness_page import BrightnessPage

import myvars

def InitBrightnessPage(main_screen):

    myvars.BrightnessPage = BrightnessPage()
    
    myvars.BrightnessPage._Screen = main_screen
    myvars.BrightnessPage._Name = "Brightness"
    myvars.BrightnessPage.Init()
