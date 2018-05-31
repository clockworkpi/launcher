# -*- coding: utf-8 -*- 

import pygame
import os
import subprocess

#from libs import easing
#from datetime import datetime

#import base64
#from beeprint import pp
import string
from Xlib import X,display
import config

def SkinMap(orig_file_or_dir):
    DefaultSkin = "default"
    
    if orig_file_or_dir.startswith(".."):
        ret  = orig_file_or_dir.replace("..","../skin/"+config.SKIN)
        if FileExists(ret) == False:
            ret = orig_file_or_dir.replace("..","../skin/"+DefaultSkin)
    else:
        ret = "../skin/"+config.SKIN+"/sys.py/"+orig_file_or_dir
        if FileExists(ret) == False:
            ret = "../skin/"+DefaultSkin+"/sys.py/"+orig_file_or_dir
        
    if FileExists( ret ):
        return ret
    else:  ## if not existed both in default or custom skin ,return where it is
        return orig_file_or_dir

def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'])

def get_git_revision_short_hash():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])


def X_center_mouse():
    d = display.Display()
    s = d.screen()
    root = s.root
    width = s.width_in_pixels
    height = s.height_in_pixels
#    print(width,height)
    root.warp_pointer(width/2,height/2)
        
    d.sync()


def IsPythonPackage(self,dirname):
    files = os.listdir(dirname)
    for i in sorted(files):
        if i.endswith("__init__.py"):
            return True
    return False
    
def MakeExecutable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

def GetExePath():# get self dir
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.getcwd()
    return dir_path

def CmdClean(cmdpath):#escape spec chars
    spchars = "\\`$();|{}&'\"*?<>[]!^~-#\n\r "
    for i in spchars:
        cmdpath = string.replace(cmdpath,i,"\\"+i)

    return cmdpath

def ReplaceSuffix(orig_file_str,new_ext):
    filename,ext = os.path.splitext(orig_file_str)
    ext = ext.strip()
    if ext != "":
        return "%s.%s"%(filename,new_ext)

def FileExists(name): # both file and dir checked
    return os.path.exists(name)


def ReadTheFileContent(filename):
    data = ""
    with open(filename, 'r') as myfile:
        data = myfile.read()
    return data

def midRect(x,y,width,height,canWidth,canHeight):
    return pygame.Rect(min(canWidth,x-width/2),min(canHeight,y-height/2),width,height)

#surface color change
def color_surface(surface, color):
    red = color.r
    green = color.g
    blue = color.b
    arr = pygame.surfarray.pixels3d(surface)
    arr[:,:,0] = red
    arr[:,:,1] = green
    arr[:,:,2] = blue


def DrawText(canvas,text, x,y,width,height,canWidth,canHeight,fontObj):# text for content,fontObj for pygame.font.Font
    _w = 0
    _tp = len(text)

    for idx,t in enumerate(fontObj.metrics(text)):
        _w = _w + t[1] - t[0]
        if _w > icon_width:
            _tp = idx
            break
    width = _w #recalc the width of text
    if width > icon_width: ##Label width max is icon width
        width = icon_width

    if _tp < len(text):##cut the text to fit width
        text = text[0:_tp]

    canvas.blit(fontObj.render(text,True,(83,83,83)),midRect(x,y,width,height,canWidth,canHeight))


def SwapAndShow():
    pygame.display.update()
