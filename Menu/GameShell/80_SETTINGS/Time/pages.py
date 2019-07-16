# -*- coding: utf-8 -*- 

from timezone_lib_list_page import TimezoneListPage
import myvars

def InitTimePage(main_screen):
    myvars.TimePage = None

def InitTimezoneListPage(main_screen):
    myvars.TimezoneListPage = TimezoneListPage()
    myvars.TimezoneListPage._Screen = main_screen
    myvars.TimezoneListPage._Name   = "Timezone Selection"
    myvars.TimezoneListPage.Init()
