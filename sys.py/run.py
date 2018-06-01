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
import time
import gobject


import socket
import pygame
from sys import exit
import os

from beeprint import pp
########
if getattr(dbus, 'version', (0, 0, 0)) < (0, 80, 0):
    import dbus.glib
else:
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)


#local UI import
from UI.constants    import Width,Height,bg_color,icon_width,icon_height,DT,GMEVT,RUNEVT,RUNSYS,ICON_TYPES
from UI.util_funcs   import ReplaceSuffix,FileExists, ReadTheFileContent,midRect,color_surface,SwapAndShow,GetExePath,X_center_mouse
from UI.page         import PageStack,PageSelector,Page
from UI.label        import Label
from UI.icon_item    import IconItem
#from UI.fonts        import fonts
from UI.title_bar    import TitleBar
from UI.foot_bar     import FootBar
from UI.main_screen  import MainScreen
from UI.above_all_patch import SoundPatch
from UI.icon_pool    import MyIconPool

from libs.DBUS            import setup_dbus

import config

if not pygame.display.get_init():
    pygame.display.init()
if not pygame.font.get_init():
    pygame.font.init()

gobject_main_loop = None

sound_patch = None

myscriptname = os.path.basename(os.path.realpath(__file__))

everytime_keydown = time.time()

last_brt = -1

def gobject_loop():
    """
    here to receive dbus signal 
    """ 
    try:
        gobject_main_loop.run()
    except KeyboardInterrupt:
        gobject_main_loop.quit()
        exit(-1)


def RestoreLastBackLightBrightness(main_screen):
    global last_brt
    
    if last_brt == -1:
        return

    try:
        f = open(config.BackLight,"r+")
    except IOError:
        print( "RestoreLastBackLightBrightness open %s failed, try to adjust brightness in Settings" % config.BackLight)
        pass
    else:
        with f:
            content = f.readlines()
            content = [x.strip() for x in content]
            brt=int(content[0])        
            if brt < last_brt:
                f.seek(0)
                f.write(str( last_brt ))
                f.truncate()
                f.close()
                last_brt = -1
                main_screen._TitleBar._InLowBackLight = -1
            else:
                
                f.close()
                return

def InspectionTeam(main_screen):
    global everytime_keydown,last_brt
    
    cur_time = time.time()

    if cur_time - everytime_keydown > 40:
        print("timeout, dim screen %d" % int(cur_time - everytime_keydown))

        try:
            f = open(config.BackLight,"r+")
        except IOError:
            pass
        else:
            with f:
                content = f.readlines()
                content = [x.strip() for x in content]
                brt=int(content[0])
                if brt > 1:
                    last_brt = brt ## remember brt for restore
                    brt = 1
                    f.seek(0)
                    f.write(str(brt))
                    f.truncate()
                    f.close()

                    main_screen._TitleBar._InLowBackLight = 0
                    
        everytime_keydown = cur_time
        
    return True

def event_process(event,main_screen):
    global sound_patch
    global everytime_keydown 
    if event != None:
        pygame.event.clear()
        if event.type == pygame.ACTIVEEVENT:
            print(" ACTIVEEVENT !")
            return
        if event.type == pygame.QUIT:
            exit()
        if event.type == GMEVT:
            main_screen.Draw()
            main_screen.SwapAndShow()
            pygame.event.clear(GMEVT)
            return
        if event.type == RUNEVT:

            if config.DontLeave==True:
                os.chdir(GetExePath())
                os.system( "/bin/sh -c "+event.message)
            else:
                on_exit_cb = getattr(main_screen,"OnExitCb",None)
                if on_exit_cb != None:
                    if callable( on_exit_cb ):
                        main_screen.OnExitCb(event)
                
                pygame.quit()
                gobject_main_loop.quit()
                os.chdir( GetExePath())
                exec_app_cmd = event.message
                exec_app_cmd += "; sync & cd "+GetExePath()+"; exec python "+myscriptname
                print(exec_app_cmd)
                os.execlp("/bin/sh","/bin/sh","-c", exec_app_cmd)
                os.chdir( GetExePath())
                os.exelp("python","python"," "+myscriptname)
                sys.exit(-1)
            return

        if event.type == RUNSYS:
            if config.DontLeave==True:
                os.chdir(GetExePath())
                os.system( "/bin/sh -c "+event.message)
            else:
                pygame.quit()
                gobject_main_loop.quit()
                os.chdir( GetExePath())
                exec_app_cmd = event.message
                exec_app_cmd += "; sync & cd "+GetExePath()+"; exec python "+myscriptname
                print(exec_app_cmd)
                os.execlp("/bin/sh","/bin/sh","-c", exec_app_cmd)
                os.chdir( GetExePath())
                os.exelp("python","python"," "+myscriptname)
            return
        if event.type == pygame.KEYUP:
            
            pygame.event.clear(pygame.KEYDOWN)
            return
        if event.type == pygame.KEYDOWN:
            everytime_keydown = time.time()
            RestoreLastBackLightBrightness(main_screen)
            ###########################################################
            if event.key == pygame.K_q:
                on_exit_cb = getattr(main_screen,"OnExitCb",None)
                if on_exit_cb != None:
                    if callable( on_exit_cb ):
                        main_screen.OnExitCb(event)
                
                gobject_main_loop.quit()
                exit()

            if event.key == pygame.K_KP_PLUS:
                if main_screen._CurrentPage._Name != "Sound volume": ## name from Menu/GameShell/10_Settings/Sound/pages.py
                    main_screen.Draw()
                    sound_patch.VolumeUp()
                    sound_patch.Draw()
                    
                    main_screen.SwapAndShow()
                    #pygame.time.delay(200)
                    #main_screen.Draw()
                    #main_screen.SwapAndShow()
                
            if event.key == pygame.K_KP_MINUS:
                if main_screen._CurrentPage._Name != "Sound volume":
                    main_screen.Draw()
                    
                    sound_patch.VolumeDown()
                    sound_patch.Draw()
                    
                    main_screen.SwapAndShow()
                    #pygame.time.delay(200)
                    #main_screen.Draw()
                    #main_screen.SwapAndShow()
                    
            
            ###########################################################
            if event.key == pygame.K_ESCAPE:
                pygame.event.clear()
            
            key_down_cb = getattr(main_screen,"KeyDown",None)
            if key_down_cb != None:
                if callable( key_down_cb ):
                    main_screen.KeyDown(event)
            
            return
                    
def gobject_pygame_event_poll_timer(main_screen):
    
    event = pygame.event.poll()

    event_process(event,main_screen)

    InspectionTeam(main_screen)
    
    return True 

def gobject_pygame_event_timer(main_screen):
    global sound_patch
    
    for event in pygame.event.get():
        event_process(event,main_screen)
    
    return True 


@misc.threaded
def socket_thread(main_screen):
    socket_path = "/tmp/gameshell"
    if os.path.exists(socket_path):
        os.remove(socket_path)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socket_path)
    while True:
        server.listen(1)
        conn, addr = server.accept()
        datagram = conn.recv(1024)
        if datagram:
            tokens = datagram.strip().split()

            if tokens[0].lower() == "esc":
                escevent = pygame.event.Event(pygame.KEYDOWN,{'scancode':9,'key': 27, 'unicode': u'\x1b', 'mod': 0})
                current_page_key_down_cb = getattr(main_screen._CurrentPage,"KeyDown",None)
                if current_page_key_down_cb != None:
                    if callable( current_page_key_down_cb ):
                        main_screen._CurrentPage.KeyDown(escevent)
                
            if tokens[0].lower() == "quit":
                conn.close()
                on_exit_cb = getattr(main_screen,"OnExitCb",None)
                if on_exit_cb != None:
                    if callable( on_exit_cb ):
                        main_screen.OnExitCb(None)
                
                gobject_main_loop.quit()
                exit()
                                
            if tokens[0].lower() == "poweroff":
                escevent = pygame.event.Event(pygame.KEYDOWN,{'scancode':9,'key': 27, 'unicode': u'\x1b', 'mod': 0})
                for i in range(0,5):
                    current_page_key_down_cb = getattr(main_screen._CurrentPage,"KeyDown",None)
                    if current_page_key_down_cb != None:
                        if callable( current_page_key_down_cb ):
                            main_screen._CurrentPage.KeyDown(escevent)
                    
                    if main_screen._MyPageStack.Length() == 0: ## on Top Level 
                        break
                
                if main_screen._CurrentPage._Name == "GameShell":
                    for i in main_screen._CurrentPage._Icons:
                        if i._MyType == ICON_TYPES["FUNC"]:
                            if i._Label.GetText() == "PowerOFF":
                                api_cb = getattr(i._CmdPath,"API",None)
                                if api_cb != None:
                                    if callable(api_cb):
                                        i._CmdPath.API(main_screen)   
                
def big_loop():
    global sound_patch
    
    title_bar = TitleBar()
    title_bar.Init(screen)
    foot_bar  = FootBar()
    foot_bar.Init(screen)

    main_screen = MainScreen()
    main_screen._HWND = screen
    main_screen._TitleBar = title_bar 
    main_screen._FootBar  = foot_bar
    main_screen.Init()
    main_screen.ReadTheDirIntoPages("../Menu",0,None)
    main_screen.FartherPages()

    title_bar._SkinManager = main_screen._SkinManager
    foot_bar._SkinManager  = main_screen._SkinManager
    
    sound_patch = SoundPatch()
    sound_patch._Parent = main_screen
    sound_patch.Init()
    #pp(main_screen._Pages[0],True,6)

    screen.fill(bg_color)
    main_screen.Draw()
    main_screen.SwapAndShow()

    #gobject.timeout_add(DT,gobject_pygame_event_timer,main_screen)
    gobject.timeout_add(DT,gobject_pygame_event_poll_timer,main_screen)
    gobject.timeout_add(3000,title_bar.GObjectRoundRobin)


    socket_thread(main_screen)
    
    gobject_loop()
    

###MAIN()###
if __name__ == '__main__':
    
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    X_center_mouse()
    
    os.chdir( os.path.dirname(os.path.realpath(__file__)) )
    
    SCREEN_SIZE = (Width,Height)
    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)

    pygame.event.set_allowed(None) 
    pygame.event.set_allowed([pygame.KEYDOWN,pygame.KEYUP,GMEVT,RUNEVT,RUNSYS])
    
    pygame.key.set_repeat(DT+DT*6+DT/2, DT+DT*3+DT/2)


    MyIconPool.Init()
    
    setup_dbus()

    gobject.threads_init()
    
    gobject_main_loop = gobject.MainLoop()

#    if pygame.display.get_active() == True:
#        print("I am actived")
    
    if pygame.image.get_extended() == False:
        print("This pygame does not support PNG")
        exit()

    
    big_loop()
    
