import sqlite3
import json

from wicd import misc 
from pyaria2_rpc.pyaria2 import Wsrpc

import libs.websocket as websocket

aria2_ws = "ws://localhost:6800/jsonrpc"
aria2_db = "aria2tasks.db"

rpc = Wsrpc('localhost',6800)

@misc.threaded
def game_install_thread():
    pass

def on_message(ws, message):
    global rpc
    print("got message")
    print(message)
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
    database = r"aria2tasks.db"
 
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
  
    conn = create_connection(database)
 
    if conn is not None:
        create_table(conn, sql_create_tasks_table)
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
