import os
import platform
import sqlite3
import json

from wicd import misc 
from pyaria2_rpc.pyaria2 import Wsrpc

import libs.websocket as websocket

aria2_ws = "ws://localhost:6800/jsonrpc"
aria2_db = "aria2tasks.db"
warehouse_db = "warehouse.db"

rpc = Wsrpc('localhost',6800)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@misc.threaded
def game_install_thread(aria2_result):
    try:
        #print("game_install_thread ",aria2_result)
        if "files" in aria2_result:
            if len(aria2_result["files"]) <= 0:
                return
        if "arm" not in platform.machine():
            return

        ret = aria2_result["files"][0]['uris']

        remote_file_url = ret[0]['uri']
        menu_file = remote_file_url.split("raw.githubusercontent.com")[1]
        local_menu_file = "%s/aria2download%s" % (os.path.expanduser('~'),menu_file )
        local_menu_file_path = os.path.dirname(local_menu_file)


        if os.path.exists(local_menu_file) == True:

           gametype = "launcher"

           if local_menu_file.endswith(".tar.gz"):
               gametype = "launcher"
           if local_menu_file.endswith(".p8.png"):
               gametype = "pico8"
           if local_menu_file.endswith(".tic"):
               gametype = "tic80"

           if gametype == "launcher":
               #tar zxvf 
               _cmd = "tar zxvf '%s' -C %s" % (local_menu_file, local_menu_file_path)
               print(_cmd)
               os.system(_cmd)
           if gametype == "pico8":
               _cmd="cp -rf '%s' ~/.lexaloffle/pico-8/carts/" % local_menu_file
               print(_cmd)
               os.system(_cmd)
           if gametype == "tic80":
               _cmd = "cp -rf '%s' ~/games/TIC-80/" % local_menu_file
               print(_cmd)
               os.system(_cmd)


    except Exception as ex:
        print("app install error: ",ex)
         

def on_message(ws, message):
    global rpc
    print("got message ",message)
    #decode json
    #lookup in the sqlite db ,update the status[error,complete],
    #uncompress the game into destnation folder in the game_install_thread
    aria2_noti = json.loads(message)
    if "method" in aria2_noti and aria2_noti["method"] == "aria2.onDownloadError":
         gid = aria2_noti["params"][0]["gid"]
         msg = rpc.tellStatus(gid)
         ws.send(msg)

    if "method" in aria2_noti and aria2_noti["method"] == "aria2.onDownloadComplete":
         gid = aria2_noti["params"][0]["gid"]
         msg = rpc.tellStatus(gid)
         ws.send(msg)
         #game_install_thread(gid)
    
    if "method" not in aria2_noti and "result" in aria2_noti:
        result = aria2_noti["result"]
        if "status" in result:
             if result["status"] == "error":
                 try:
                     print(result["errorMessage"])
                     for x in result["files"]:
                         if os.path.exists(x["path"]):
                             os.remove(x["path"])
                         if os.path.exists(x["path"]+".aria2"):
                             os.remove(x["path"]+".aria2")

                 except Exception as ex:
                     print(ex)
             if result["status"] == "complete":
                 game_install_thread(result)

       
def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print "on open"

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return conn
 
 
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)



def init_sqlite3():
    global aria2_db
    global warehouse_db

    database = aria2_db
 
    sql_create_tasks_table = """ CREATE TABLE IF NOT EXISTS tasks (
                                        id integer PRIMARY KEY,
                                        gid text NOT NULL,
                                        title text NOT NULL,
                                        file  text NOT NULL,
                                        type  text NOT NULL,
                                        status text,
                                        totalLength text,
                                        completedLength text,
                                        fav text
                                    ); """

    sql_create_warehouse_table = """ CREATE TABLE IF NOT EXISTS warehouse (
                                        id integer PRIMARY KEY,
                                        title text NOT NULL,
                                        file  text NOT NULL,
                                        type  text NOT NULL
                                        ); """
 
    conn = create_connection(database)
 
    if conn is not None:
        create_table(conn, sql_create_tasks_table)
        conn.close()
    else:
        print("Error! cannot create the database connection.")
        exit()

    database = warehouse_db
    conn = create_connection(database)
 
    if conn is not None:
        create_table(conn, sql_create_warehouse_table)
        conn.close()
    else:
        print("Error! cannot create the database connection.")
        exit()



if __name__ == "__main__":
    init_sqlite3()
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(aria2_ws,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
#    ws.on_open = on_open
    ws.run_forever()
