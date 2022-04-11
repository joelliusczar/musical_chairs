import os
import sys
import itertools
from typing import Callable, Iterator, Optional, Tuple
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import Row
from sqlalchemy import select, \
	func, \
	insert, \
	delete, \
	update
from musical_chairs_libs.wrapped_db_connection import WrappedDbConnection
from musical_chairs_libs.tables import stations, \
	tags, \
	stations_tags, \
	songs_tags, \
	songs, \
	albums, \
	artists, \
	song_artist
from musical_chairs_libs.dtos import Tag, \
	StationInfo, \
	SongItem
from musical_chairs_libs.config_loader import ConfigLoader

class StationService:

	def __init__(self, 
		conn: WrappedDbConnection,
		configLoader: Optional[ConfigLoader]=None
	):
			if not conn:
				if not configLoader:
					configLoader = ConfigLoader()
				conn = configLoader.get_configured_db_connection()
			self.conn = conn

	def set_station_proc(self, stationName: str) -> None:
		pid = os.getpid()
		st = stations.c
		stmt = update(stations)\
			.values(procId = pid).where(st.name == stationName)
		self.conn.execute(stmt)

	def remove_station_proc(self, stationName: str) -> None:
		st = stations.c
		stmt = update(stations)\
			.values(procId = None).where(st.name == stationName)
		self.conn.execute(stmt)

	def end_all_stations(self) -> None:
		st = stations.c
		query = select(st.procId).select_from(stations).where(st.procId != None)
		for row in self.conn.execute(query).fetchall():
			pid: int = row.procId #type: ignore
			try:
				os.kill(pid, 2)
			except: pass
		stmt = update(stations).values(procId = None)
		self.conn.execute(stmt)

	def get_station_pk(self, stationName: str) -> Optional[int]:
		st = stations.c
		query = select(st.pk) \
			.select_from(stations) \
			.where(st.name == stationName)
		row = self.conn.execute(query).fetchone()
		pk: Optional[int] = row.pk if row else None #type: ignore
		return pk

	def get_tag_pk(self, tagName: str) -> Optional[int]:
		t = tags.c
		query = select(t.pk) \
			.select_from(tags) \
			.where(t.name == tagName)
		row = self.conn.execute(query).fetchone()
		pk: Optional[int] = row.pk if row else None #type: ignore
		return pk

	def does_station_exist(self, stationName: str) -> bool:
		st = stations.c
		query = select(func.count(1))\
			.select_from(stations)\
			.where(st.name == stationName)
		res = self.conn.execute(query).fetchone()
		return res.count < 1 if res else False

	def add_station(self, stationName: str, displayName: str) -> None:
		try:
			stmt = insert(stations)\
				.values(name = stationName, displayName = displayName)
			self.conn.execute(stmt)
		except IntegrityError:
			print("Could not insert")
			sys.exit(1)

	def get_or_save_tag(self, tagName: str) -> Optional[int]:
		if not tagName:
			return None
		tg = tags.c
		query = select(tg.pk).select_from(tags).where(tg.name == tagName)
		row = self.conn.execute(query).fetchone()
		if row:
			return row.pk #type: ignore
		stmt = insert(tags).values(name = tagName)
		res = self.conn.execute(stmt)
		return res.lastrowid #type: ignore

	def assign_tag_to_station(self,stationName: str, tagName: str) -> None:
		stationPk = self.get_station_pk(stationName)
		tagPk = self.get_or_save_tag(tagName)
		try:
			stmt = insert(stations_tags)\
				.values(stationFk = stationPk, tagFk = tagPk)
			self.conn.execute(stmt)
		except IntegrityError as ex:
			print("Could not insert")
			print(ex)
			sys.exit(1)

	def remove_station(self, stationName: str) -> None:
		sttg = stations_tags.c
		st = stations.c
		stationPk = self.get_station_pk(stationName)
		assignedTagsDel = delete(stations_tags)\
			.where(sttg.stationFk == stationPk)
		self.conn.execute(assignedTagsDel)
		stationDel = delete(stations).where(st.stationPk == stationPk)
		self.conn.execute(stationDel)

	def get_station_list(self) -> Iterator[StationInfo]:
		st = stations.c
		sgtg = songs_tags.c
		sttg = stations_tags.c
		tg = tags.c
		query = select(
			st.pk, 
			st.name, 
			tg.name, 
			tg.pk,
			func.min(st.displayName)
		).select_from(stations) \
			.join(stations_tags, st.pk == sttg.stationFk) \
			.join(songs_tags, sgtg.tagFk == sttg.tagFk) \
			.join(tags, sttg.tagFk == tg.pk) \
			.group_by(st.pk, st.name, tg.name, tg.pk) \
			.having(func.count(sgtg.tagFk) > 0)
		records = self.conn.execute(query)
		partitionFn: Callable[[Row], Tuple[int, str]] = \
			lambda r: (r[st.pk], r[st.name])
		for key, group in itertools.groupby(records, partitionFn): #type: ignore
			yield StationInfo(
				id=key[0], 
				name=key[1],
				tags=list(map(lambda r: Tag(r[tg.pk], r[tg.name]), group)) #type: ignore
			)

	def get_station_song_catalogue(
		self, 
		stationPk: Optional[int]=None,
		stationName: Optional[str]=None, 
		limit: Optional[int]=None, 
		offset: int = 0
	) -> Iterator[SongItem]:
		sg = songs.c
		st = stations.c
		sttg = stations_tags.c
		sgtg = songs_tags.c
		ab = albums.c
		ar = artists.c
		sgar = song_artist.c
		baseQuery = select(
			sg.pk, 
			sg.title, 
			ab.name.label("album"), \
			ar.name.label("artist"), \
		).select_from(stations) \
			.join(stations_tags, st.pk == sttg.stationFk) \
			.join(songs_tags, sgtg.tagFk == sttg.tagFk) \
			.join(songs, sg.pk == sgtg.songFk) \
			.join(albums, sg.albumFk == ab.pk, isouter=True) \
			.join(song_artist, sg.pk == sgar.songFk, isouter=True) \
			.join(artists, sgar.artistFk == ar.pk, isouter=True) \
			.limit(limit) \
			.offset(offset)
		if stationPk:
			query = baseQuery.where(st.pk == stationPk)
		elif stationName:
			query = baseQuery.where(st.name == stationName)
		else:
			raise ValueError("Either stationName or pk must be provided")
		records = self.conn.execute(query)
		for row in records: #type: ignore
			yield SongItem(row.pk, #type: ignore
				row.title, #type: ignore
				row.album, #type: ignore
				row.artist #type: ignore
			)

