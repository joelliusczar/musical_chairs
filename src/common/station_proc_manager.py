#!/usr/bin/env python2

import os
import signal

def set_station_proc(conn, stationName):
    cursor = conn.cursor()
    pid = os.getpid()
    params = (pid, stationName, )
    cursor.execute("UPDATE [Stations] "
        "SET [ProcId] = ? "
        "WHERE [Name] = ?", params)
    cursor.close()

def remove_station_proc(conn, stationName):
    cursor = conn.cursor()
    params = (stationName, )
    cursor.execute("UPDATE [Stations] "
        "SET [ProcId] = NULL "
        "WHERE [Name] = ?", params)
    cursor.close()

def end_all_stations(conn):
    cursor = conn.cursor()
    for row in cursor.execute("SELECT [ProcId] FROM [Stations] "
        "WHERE [ProcId] IS NOT NULL"):
        pid = row[0]
        try:
            os.kill(pid, 2)
        except: pass
    cursor.close()
    updateCursor = conn.cursor()
    updateCursor.execute("UPDATE [Stations] "
        "SET [ProcId] = NULL ")
    updateCursor.close()

