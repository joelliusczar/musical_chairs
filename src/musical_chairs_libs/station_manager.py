import os
import sys
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, desc, func, insert, delete, update
from musical_chairs_libs.config_loader import get_configured_db_connection
from musical_chairs_libs.tables import stations, tags, stations_tags
from musical_chairs_libs.connection_decorator import provide_db_conn


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

def get_station_pk(stationName, conn):
	st = stations.c
	query = select(st.pk) \
		.select_from(stations) \
		.where(st.name == stationName)
	row = conn.execute(query).fetchone()
	pk = row.pk if row else None
	return pk

@provide_db_conn()
def get_tag_pk(tagName, conn):
	t = tags.c
	query = select(t.pk) \
		.select_from(tags) \
		.where(t.name == tagName)
	row = conn.execute(query).fetchone()
	pk = row.pk if row else None
	return pk

@provide_db_conn()
def does_station_exist(stationName, conn):
	st = stations.c
	query = select(func.count(1)).select_from(stations).where(st.name == stationName)
	res = conn.execute(query).fetchone()
	return res.count < 1

@provide_db_conn()
def add_station(stationName, displayName, conn):
	try:
		stmt = insert(stations).values(name = stationName, displayName = displayName)
		conn.execute(stmt)
	except IntegrityError:
		print("Could not insert")
		sys.exit(1)

def _get_or_save_tag(tagName, conn):
	if not tagName:
		return None
	tg = tags.c
	query = select(tg.pk).select_from(tags).where(tg.name == tagName)
	row = conn.execute(query).fetchone()
	if row:
		return row.pk
	stmt = insert(tags).values(name = tagName)
	res = conn.execute(stmt)
	return res.lastrowid

@provide_db_conn()
def assign_tag_to_station(stationName, tagName, conn):
	stationPk = get_station_pk(stationName, conn)
	tagPk = _get_or_save_tag(tagName, conn)
	try:
		stmt = insert(stations_tags).values(stationFk = stationPk, tagFk = tagPk)
		conn.execute(stmt)
	except IntegrityError as ex:
		print("Could not insert")
		print(ex)
		sys.exit(1)

@provide_db_conn()
def remove_station(stationName, conn):
	sttg = stations_tags.c
	st = stations.c
	stationPk = get_station_pk(stationName, conn)
	assignedTagsDel = delete(stations_tags).where(sttg.stationFk == stationPk)
	conn.execute(assignedTagsDel)
	stationDel = delete(stations).where(st.stationPk == stationPk)
	conn.execute(stationDel)