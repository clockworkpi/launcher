# -*- coding: utf-8 -*- 

## local UI import
import pages
import myvars

def Init(main_screen):
    pages.InitSoundPage(main_screen)

def API(main_screen):
    
    if main_screen !=None:
        main_screen.PushCurPage()
        main_screen.SetCurPage(myvars.SoundPage)
        main_screen.Draw()
        main_screen.SwapAndShow()
        
