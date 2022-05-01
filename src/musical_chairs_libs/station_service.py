#pyright: reportUnknownMemberType=false
import sys
import itertools
from typing import Callable, Iterator, Optional, Tuple
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import Row
from sqlalchemy.engine import Connection
from sqlalchemy import select, \
	func, \
	insert, \
	delete, \
	update
from sqlalchemy.sql import ColumnCollection
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
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.os_process_manager import OSProcessManager

class StationService:

	def __init__(self, 
		conn: Optional[Connection]=None,
		envManager: Optional[EnvManager]=None,
		processManager: Optional[OSProcessManager]=None
	):
			if not conn:
				if not envManager:
					envManager = EnvManager()
				conn = envManager.get_configured_db_connection()
			if not processManager:
				processManager = OSProcessManager()
			self.conn = conn
			self.process_manager = processManager

	def set_station_proc(self, stationName: str) -> None:
		pid = self.process_manager.getpid()
		st: ColumnCollection = stations.columns
		stmt = update(stations)\
			.values(procId = pid).where(st.name == stationName)
		self.conn.execute(stmt)

	def remove_station_proc(self, stationName: str) -> None:
		st: ColumnCollection = stations.columns
		stmt = update(stations)\
			.values(procId = None).where(st.name == stationName)
		self.conn.execute(stmt)

	def end_all_stations(self) -> None:
		st: ColumnCollection = stations.columns
		query = select(st.procId).select_from(stations).where(st.procId != None)
		for row in self.conn.execute(query).fetchall():
			pid: int = row.procId  #pyright: ignore [reportGeneralTypeIssues]
			self.process_manager.end_process(pid)
		stmt = update(stations).values(procId = None)
		self.conn.execute(stmt)

	def get_station_pk(self, stationName: str) -> Optional[int]:
		st: ColumnCollection = stations.columns
		query = select(st.pk) \
			.select_from(stations) \
			.where(st.name == stationName)
		row = self.conn.execute(query).fetchone()
		pk: Optional[int] = row.pk if row else None #pyright: ignore [reportGeneralTypeIssues]
		return pk

	def get_tag_pk(self, tagName: str) -> Optional[int]:
		t: ColumnCollection = tags.columns
		query = select(t.pk) \
			.select_from(tags) \
			.where(t.name == tagName)
		row = self.conn.execute(query).fetchone()
		pk: Optional[int] = row.pk if row else None #pyright: ignore [reportGeneralTypeIssues]
		return pk

	def does_station_exist(self, stationName: str) -> bool:
		st: ColumnCollection = stations.columns
		query = select(func.count(1))\
			.select_from(stations)\
			.where(st.name == stationName)
		res = self.conn.execute(query).fetchone()
		count: int = res.count < 1 if res else 0
		return count < 1 

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
		tg: ColumnCollection = tags.columns
		query = select(tg.pk).select_from(tags).where(tg.name == tagName)
		row = self.conn.execute(query).fetchone()
		if row:
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		stmt = insert(tags).values(name = tagName)
		res = self.conn.execute(stmt)
		insertedPk: int = res.lastrowid 
		return insertedPk

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
		sttg: ColumnCollection = stations_tags.columns
		st: ColumnCollection = stations.columns
		stationPk = self.get_station_pk(stationName)
		assignedTagsDel = delete(stations_tags)\
			.where(sttg.stationFk == stationPk)
		self.conn.execute(assignedTagsDel)
		stationDel = delete(stations).where(st.stationPk == stationPk)
		self.conn.execute(stationDel)

	def get_station_list(self) -> Iterator[StationInfo]:
		st: ColumnCollection = stations.columns
		sgtg: ColumnCollection = songs_tags.columns
		sttg: ColumnCollection = stations_tags.columns
		tg: ColumnCollection = tags.columns
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
		mapFn: Callable[[Row], Tag] = \
			lambda r: Tag(r[tg.pk],r[tg.name])
		for key, group in itertools.groupby(records, partitionFn): #pyright: ignore [reportUnknownVariableType]
			yield StationInfo(
				id=key[0], 
				name=key[1],
				tags=list(map(mapFn, group)) #pyright: ignore [reportUnknownArgumentType] 
			)

	def get_station_song_catalogue(
		self, 
		stationPk: Optional[int]=None,
		stationName: Optional[str]=None, 
		limit: Optional[int]=None, 
		offset: int = 0
	) -> Iterator[SongItem]:
		sg: ColumnCollection = songs.columns
		st: ColumnCollection = stations.columns
		sttg: ColumnCollection = stations_tags.columns
		sgtg: ColumnCollection = songs_tags.columns
		ab: ColumnCollection = albums.columns
		ar: ColumnCollection = artists.columns
		sgar: ColumnCollection = song_artist.columns
		baseQuery = select(
			sg.pk, 
			sg.name.label("song"), 
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
		for row in records: #pyright: ignore [reportUnknownVariableType] 
			yield SongItem(row.pk, #pyright: ignore [reportUnknownArgumentType] 
				row.song, #pyright: ignore [reportUnknownArgumentType] 
				row.album, #pyright: ignore [reportUnknownArgumentType] 
				row.artist #pyright: ignore [reportUnknownArgumentType] 
			)

