import os
from sqlalchemy import select, desc, func, insert, delete, update
from musical_chairs_libs.tables import stations

def set_station_proc(conn, stationName):
    pid = os.getpid()
    st = stations.c
    stmt = update(stations).values(procId = pid).where(st.name == stationName)
    conn.execute(stmt)

def remove_station_proc(conn, stationName):
    st = stations.c
    stmt = update(stations).values(procId = None).where(st.name == stationName)
    conn.execute(stmt)

def end_all_stations(conn):
    st = stations.c
    query = select(st.procId).select_from(stations).where(st.procId != None)
    for row in conn.execute(query).fetchall():
        pid = row.procId
        try:
            os.kill(pid, 2)
        except: pass
    stmt = update(stations).values(procId = None)
    conn.execute(stmt)


