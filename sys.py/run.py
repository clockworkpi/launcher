# -*- coding: utf-8 -*- 
import os
import dbus
import dbus.service
import sys
import commands
import logging
import errno

from wicd import misc
import libs.websocket as websocket
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
import json

#from beeprint import pp
########
if getattr(dbus, 'version', (0, 0, 0)) < (0, 80, 0):
    import dbus.glib
else:
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

import config
#local UI import
from UI.constants    import Width,Height,icon_width,icon_height,DT,RUNEVT,RUNSYS,ICON_TYPES,POWEROPT,RESTARTUI,RUNSH
from UI.util_funcs   import ReplaceSuffix,FileExists, ReadTheFileContent,midRect,color_surface,SwapAndShow,GetExePath,X_center_mouse,ArmSystem
from UI.page         import PageStack,PageSelector,Page
from UI.label        import Label
from UI.icon_item    import IconItem
#from UI.fonts        import fonts
from UI.title_bar    import TitleBar
from UI.foot_bar     import FootBar
from UI.main_screen  import MainScreen
from UI.above_all_patch import SoundPatch
from UI.icon_pool    import MyIconPool
from UI.createby_screen import CreateByScreen
from UI.skin_manager import MySkinManager
from libs.DBUS            import setup_dbus


if not pygame.display.get_init():
    pygame.display.init()
if not pygame.font.get_init():
    pygame.font.init()

gobject_main_loop = None

sound_patch = None

myscriptname = os.path.basename(os.path.realpath(__file__))

everytime_keydown = time.time()

passout_time_stage = 0

last_brt = -1

gobject_flash_led1 = -1
gobject_flash_led1_counter = 0

Keys = []
crt_screen = None

def gobject_loop():
    """
    here to receive dbus signal 
    """ 
    try:
        gobject_main_loop.run()
    except KeyboardInterrupt:
        gobject_main_loop.quit()
        exit(-1)

def GobjectFlashLed1(main_screen):
    global gobject_flash_led1_counter
    
    if main_screen._Closed == False:
        if gobject_flash_led1_counter > 0:
            try:
                f = open("/proc/driver/led1","w")
            except IOError:
                print( "open /proc/driver/led1 IOError")
                pass
            else:
                with f:
                    f.seek(0)
                    f.write("0")
                    f.truncate()
                    f.close()

            gobject_flash_led1_counter = 0
        return True
    
    gobject_flash_led1_counter+=1

    if gobject_flash_led1_counter == 3:
        try:
            f = open("/proc/driver/led1","w")
        except IOError:
            print( "open /proc/driver/led1 IOError")
            pass
        else:
            with f:
                f.seek(0)
                f.write("1")
                f.truncate()
                f.close()
    

    elif gobject_flash_led1_counter == 5:
        try:
            f = open("/proc/driver/led1","w")
        except IOError:
            print( "open /proc/driver/led1 IOError")
            pass
        else:
            with f:
                f.seek(0)
                f.write("0")
                f.truncate()
                f.close()
    
    if gobject_flash_led1_counter == 11:
        gobject_flash_led1_counter = 1
    
    return True

    
def RestoreLastBackLightBrightness(main_screen):
    global last_brt,passout_time_stage,gobject_flash_led1

    passout_time_stage = 0
    main_screen._TitleBar._InLowBackLight = -1
    main_screen._Closed = False
    
    
    if last_brt == -1:
        return True

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
    try:
        f = open("/proc/driver/led1","w")
    except IOError:
        print( "open /proc/driver/led1 IOError")
        pass
    else:
        with f:
            f.seek(0)
            f.write("0")
            f.truncate()
            f.close()
    
    if main_screen._CounterScreen._Counting==True:
        main_screen._CounterScreen.StopCounter()
        main_screen.Draw()
        main_screen.SwapAndShow()
        return False
        
    return True

def InspectionTeam(main_screen):
    global everytime_keydown,last_brt,passout_time_stage,gobject_flash_led1
    
    cur_time = time.time()
    time_1 = config.PowerLevels[config.PowerLevel][0]
    time_2 = config.PowerLevels[config.PowerLevel][1]
    time_3 = config.PowerLevels[config.PowerLevel][2]
    
    if cur_time - everytime_keydown > time_1 and passout_time_stage == 0:
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
                if brt > 0:
                    if last_brt < 0:
                        last_brt = brt ## remember brt for restore

                    brt = 1
                    f.seek(0)
                    f.write(str(brt))
                    f.truncate()
                    f.close()

        main_screen._TitleBar._InLowBackLight = 0

        if time_2 != 0:
            passout_time_stage = 1 # next 
        everytime_keydown = cur_time
    
    elif cur_time - everytime_keydown > time_2 and passout_time_stage == 1:
        print("timeout, close screen %d" % int(cur_time - everytime_keydown))
        try:
            f = open(config.BackLight,"r+")
        except IOError:
            pass
        else:
            with f:
                brt = 0
                f.seek(0)
                f.write(str(brt))
                f.truncate()
                f.close()

        
        main_screen._TitleBar._InLowBackLight = 0
        main_screen._Closed = True
        if time_3 != 0:
            passout_time_stage = 2 # next
        
        everytime_keydown = cur_time
        
    elif cur_time - everytime_keydown > time_3 and passout_time_stage == 2:
        print("Power Off counting down")
                
        try:
            f = open(config.BackLight,"r+")
        except IOError:
            pass
        else:
            with f:
                brt = last_brt
                f.seek(0)
                f.write(str(brt))
                f.truncate()
                f.close()
            
            main_screen._CounterScreen.Draw()
            main_screen._CounterScreen.SwapAndShow()
            main_screen._CounterScreen.StartCounter()
        
        main_screen._TitleBar._InLowBackLight = 0

        passout_time_stage = 4
        
    return True

def RecordKeyDns(thekey,main_screen):
    global Keys,crt_screen
    
    if len(Keys) < 10:
        Keys.append(thekey)
    else:
        Keys = []
        Keys.append(thekey)
    
    keys = ''.join(map(str,Keys))
    #print(keys)
    if keys == "273273274274276276275275106107":##uuddllrrab
        crt_screen.Draw()
        crt_screen.SwapAndShow()
        main_screen._TitleBar._InLowBackLight = 0 ##pause titlebar drawing
        return True
    
    return False



def release_self_fds():
    fds_flags= ["pipe","socket",".ttf"]
    """List process currently open FDs and their target """
    if sys.platform != 'linux2':
        raise NotImplementedError('Unsupported platform: %s' % sys.platform)

    ret = {}
    base = '/proc/self/fd'
    for num in os.listdir(base):
        path = None
        try:
            path = os.readlink(os.path.join(base, num))
        except OSError as err:
            # Last FD is always the "listdir" one (which may be closed)
            if err.errno != errno.ENOENT:
                raise
        ret[int(num)] = path
    
    for key in ret:
      if ret[key] != None and isinstance(ret[key], str):
        for i in fds_flags:
          if i in ret[key]:
            os.close(key)
            break
    return ret  

  
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
                
                endpos = len(event.message)
                space_break_pos = endpos
                for i in range(0,endpos):
                    if event.message[i] == "/" and event.message[i-1] == " " and i > 6:
                        space_break_pos = i-1
                        break
                
                exec_app_cmd = "cd "+os.path.dirname(event.message[:space_break_pos])+";"
                exec_app_cmd += event.message
                exec_app_cmd += "; sync & cd "+GetExePath()+"; exec python "+myscriptname
                print(exec_app_cmd)
                release_self_fds()
                os.execlp("/bin/sh","/bin/sh","-c", exec_app_cmd)
                os.chdir( GetExePath())
                os.execlp("python","python"," "+myscriptname)
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
                endpos = len(event.message)
                space_break_pos = endpos
                for i in range(0,endpos):
                    if event.message[i] == "/" and event.message[i-1] == " " and i > 6:
                        space_break_pos = i-1
                        break
                                        
                exec_app_cmd = "cd "+os.path.dirname(event.message[:space_break_pos])+";" 
                exec_app_cmd += event.message
                exec_app_cmd += "; sync & cd "+GetExePath()+"; exec python "+myscriptname
                print(exec_app_cmd)
                release_self_fds()
                os.execlp("/bin/sh","/bin/sh","-c", exec_app_cmd)
                os.chdir( GetExePath())
                os.execlp("python","python"," "+myscriptname)
            return
        if event.type == RESTARTUI:
            pygame.quit()
            gobject_main_loop.quit()
            os.chdir(GetExePath())
            exec_app_cmd = " sync & cd "+GetExePath()+"; exec python "+myscriptname
            print(exec_app_cmd)
            release_self_fds()
            os.execlp("/bin/sh","/bin/sh","-c", exec_app_cmd)
            os.chdir( GetExePath())
            os.execlp("python","python"," "+myscriptname)
            return
        if event.type == RUNSH:
            pygame.quit()
            gobject_main_loop.quit()
            exec_app_cmd = event.message +";"
            release_self_fds()
            os.execlp("/bin/sh","/bin/sh","-c", exec_app_cmd)
            sys.exit(-1)
            return
        if event.type == POWEROPT:
            everytime_keydown = time.time()
            
            return
        if event.type == pygame.KEYUP:
            
            pygame.event.clear(pygame.KEYDOWN)
            return
        if event.type == pygame.KEYDOWN:
            everytime_keydown = time.time()
            if RestoreLastBackLightBrightness(main_screen) == False:
                return
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

            if RecordKeyDns(event.key,main_screen) == False:
                key_down_cb = getattr(main_screen,"KeyDown",None)
                if key_down_cb != None:
                    if callable( key_down_cb ):
                        main_screen.KeyDown(event)
            
            main_screen._LastKeyDown = everytime_keydown
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
def aria2_ws(main_screen):
    def on_message(ws, message):
        print("run.py aria2_ws on_message: ",message)
        try:
            aria2_noti = json.loads(message)
            if "method" in aria2_noti and aria2_noti["method"] == "aria2.onDownloadError":
                gid = aria2_noti["params"][0]["gid"]

            if "method" in aria2_noti and aria2_noti["method"] == "aria2.onDownloadComplete":
                gid = aria2_noti["params"][0]["gid"]
                on_comp_cb = getattr(main_screen._CurrentPage,"OnAria2CompleteCb",None)
                if on_comp_cb != None:
                    if callable( on_comp_cb ):
                        main_screen._CurrentPage.OnAria2CompleteCb(gid)
                #game_install_thread(gid)
        except Exception as ex:
            print(ex)

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print("### closed ###")
    
     
    #websocket.enableTrace(True)
    try:
        ws = websocket.WebSocketApp("ws://localhost:6800/jsonrpc",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
#    ws.on_open = on_open
        ws.run_forever()
    except:
        return


@misc.threaded
def socket_thread(main_screen):
    global everytime_keydown

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
                
            if tokens[0].lower() == "quit": #eg: echo "quit" | socat - UNIX-CONNECT:/tmp/gameshell
                conn.close()
                on_exit_cb = getattr(main_screen,"OnExitCb",None)
                if on_exit_cb != None:
                    if callable( on_exit_cb ):
                        main_screen.OnExitCb(None)
                
                gobject_main_loop.quit()
                exit()
            
            if tokens[0].lower() == "keydown": ## simulate keydown event
                everytime_keydown = time.time()
                if RestoreLastBackLightBrightness(main_screen) == False:
                    print("RestoreLastBackLightBrightness unix socket false")

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

            if tokens[0].lower() == "redraw": #echo "redraw titlebar" | socat - UNIX-CONNECT:/tmp/gameshell
                if len(tokens) > 1:
                    area = tokens[1].lower()
                    if area == "titlebar":
                        if hasattr(main_screen._TitleBar,'Redraw'):
                             if main_screen._TitleBar.Redraw != None and callable(main_screen._TitleBar.Redraw):
                                  main_screen._TitleBar.Redraw()
                    

def big_loop(screen):
    global sound_patch,gobject_flash_led1
    
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
    main_screen.ReadTheDirIntoPages("/home/cpi/apps/Menu",1,main_screen._Pages[ len(main_screen._Pages) -1])
    main_screen.ReunionPagesIcons()
    
    main_screen.FartherPages()

    
    title_bar._SkinManager = main_screen._SkinManager
    foot_bar._SkinManager  = main_screen._SkinManager
    
    sound_patch = SoundPatch()
    sound_patch._Parent = main_screen
    sound_patch.Init()
    #pp(main_screen._Pages[0],True,6)

    screen.fill(MySkinManager.GiveColor("White"))
    main_screen.Draw()
    main_screen.SwapAndShow()

    #gobject.timeout_add(DT,gobject_pygame_event_timer,main_screen)
    gobject_flash_led1 = gobject.timeout_add(200,GobjectFlashLed1,main_screen)
    
    gobject.timeout_add(DT,gobject_pygame_event_poll_timer,main_screen)
    gobject.timeout_add(3000,title_bar.GObjectRoundRobin)


    socket_thread(main_screen)
    aria2_ws(main_screen)
    
    gobject_loop()
    

###MAIN()###
if __name__ == '__main__':
    
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    X_center_mouse()
    
    os.chdir( os.path.dirname(os.path.realpath(__file__)) )
    
    SCREEN_SIZE = (Width*config.GlobalScale,Height*config.GlobalScale)
    screen = pygame.display.set_mode(SCREEN_SIZE,pygame.DOUBLEBUF | pygame.HWSURFACE, 32)

    pygame.event.set_allowed(None) 
    pygame.event.set_allowed([pygame.KEYDOWN,pygame.KEYUP,RUNEVT,RUNSYS,POWEROPT,RESTARTUI,RUNSH])
    
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

    config.GlobalCanvas = pygame.Surface((Width,Height),0,32)
    config.GlobalCanvas2 = pygame.Surface(SCREEN_SIZE ,0,32)
    
    crt_screen = CreateByScreen()
    crt_screen.Init()
    crt_screen._HWND = config.GlobalCanvas
    
    big_loop(config.GlobalCanvas)
    
