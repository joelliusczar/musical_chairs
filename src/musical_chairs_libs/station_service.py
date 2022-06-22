#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
import itertools
from typing import\
	Any,\
	Callable,\
	Iterable,\
	Iterator,\
	Optional,\
	Sequence,\
	Tuple,\
	cast
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import Row
from sqlalchemy.engine import Connection
from sqlalchemy import select, \
	func, \
	insert, \
	delete, \
	update
from sqlalchemy.sql import ColumnCollection
from musical_chairs_libs.tables import\
	stations as stations_tbl, \
	tags as tags_tbl, \
	stations_tags as stations_tags_tbl, \
	songs_tags, \
	songs, \
	albums, \
	artists, \
	song_artist
from musical_chairs_libs.dtos import\
	SearchNameString,\
	Tag,\
	StationInfo, \
	SongItem,\
	StationCreationInfo,\
	SavedNameString
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.os_process_manager import OSProcessManager
from musical_chairs_libs.simple_functions import get_datetime, build_error_obj
from musical_chairs_libs.errors import AlreadyUsedError

sg: ColumnCollection = songs.columns
st: ColumnCollection = stations_tbl.columns
sttg: ColumnCollection = stations_tags_tbl.columns
sgtg: ColumnCollection = songs_tags.columns
sgar: ColumnCollection = song_artist.columns
ab: ColumnCollection = albums.columns
ar: ColumnCollection = artists.columns
tg: ColumnCollection = tags_tbl.columns

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
		self.get_datetime = get_datetime

	def set_station_proc(self, stationName: str) -> None:
		pid = self.process_manager.getpid()
		stmt = update(stations_tbl)\
			.values(procId = pid) \
			.where(func.lower(st.name) == func.lower(stationName))
		self.conn.execute(stmt)

	def remove_station_proc(self, stationName: str) -> None:
		stmt = update(stations_tbl)\
			.values(procId = None) \
			.where(func.lower(st.name) == func.lower(stationName))
		self.conn.execute(stmt)

	def end_all_stations(self) -> None:
		query = select(st.procId).select_from(stations_tbl)\
			.where(st.procId != None)
		for row in self.conn.execute(query).fetchall():
			pid: int = row.procId  #pyright: ignore [reportGeneralTypeIssues]
			self.process_manager.end_process(pid)
		stmt = update(stations_tbl).values(procId = None)
		self.conn.execute(stmt)

	def get_station_pk(self, stationName: str) -> Optional[int]:
		query = select(st.pk) \
			.select_from(stations_tbl) \
			.where(func.lower(st.name) == func.lower(stationName))
		row = self.conn.execute(query).fetchone()
		pk: Optional[int] = row.pk if row else None #pyright: ignore [reportGeneralTypeIssues]
		return pk

	def get_tag_pk(self, tagName: str) -> Optional[int]:
		query = select(tg.pk) \
			.select_from(tags_tbl) \
			.where(func.lower(tg.name) == func.lower(tagName))
		row = self.conn.execute(query).fetchone()
		pk = row["pk"] if row else None #pyright: ignore [reportGeneralTypeIssues]
		return pk

	def does_station_exist(self, stationName: str) -> bool:
		query = select(func.count(1))\
			.select_from(stations_tbl)\
			.where(func.lower(st.name) == func.lower(stationName))
		res = self.conn.execute(query).fetchone()
		count: int = res.count < 1 if res else 0
		return count < 1

	def add_station(self, stationName: str, displayName: str) -> bool:
		if self.does_station_exist(stationName):
			return False
		stmt = insert(stations_tbl)\
			.values(name = stationName, displayName = displayName)
		self.conn.execute(stmt)
		return True

	def get_or_save_tag(self, tagName: str) -> Optional[int]:
		if not tagName:
			return None
		query = select(tg.pk).select_from(tags_tbl) \
			.where(func.lower(tg.name) == func.lower(tagName))
		row = self.conn.execute(query).fetchone()
		if row:
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		stmt = insert(tags_tbl).values(name = tagName)
		res = self.conn.execute(stmt)
		insertedPk: int = res.lastrowid
		return insertedPk

	def assign_tag_to_station(self,stationName: str, tagName: str) -> bool:
		stationPk = self.get_station_pk(stationName)
		tagPk = self.get_or_save_tag(tagName)
		try:
			stmt = insert(stations_tags_tbl)\
				.values(stationFk = stationPk, tagFk = tagPk)
			self.conn.execute(stmt)
			return True
		except IntegrityError:
			print("Could not insert")
			return False

	def remove_station(self, stationName: str) -> None:
		stationPk = self.get_station_pk(stationName)
		assignedTagsDel = delete(stations_tags_tbl)\
			.where(sttg.stationFk == stationPk)
		self.conn.execute(assignedTagsDel)
		stationDel = delete(stations_tbl).where(st.stationPk == stationPk)
		self.conn.execute(stationDel)

	def get_stations_with_songs_list(self) -> Iterator[StationInfo]:
		query = select(
			st.pk,
			st.name,
			tg.name,
			tg.pk,
			func.min(st.displayName).label("displayName")
		).select_from(stations_tbl) \
			.join(stations_tags_tbl, st.pk == sttg.stationFk) \
			.join(songs_tags, sgtg.tagFk == sttg.tagFk) \
			.join(tags_tbl, sttg.tagFk == tg.pk) \
			.group_by(st.pk, st.name, tg.name, tg.pk) \
			.having(func.count(sgtg.tagFk) > 0)
		records = self.conn.execute(query)
		partitionFn: Callable[[Row], Tuple[int, str, str]] = \
			lambda r: (r[st.pk], r[st.name], r["displayName"])
		for key, group in itertools.groupby(records, partitionFn): #pyright: ignore [reportUnknownVariableType]
			yield StationInfo(
				id=key[0],
				name=key[1],
				displayName=key[2],
				tags=[Tag(r[tg.pk],r[tg.name]) for r in cast(Iterator[Row],group)]
			)

	def _attach_catalogue_joins(
		self,
		baseQuery: Any,
		stationPk: Optional[int]=None,
		stationName: Optional[str]=None
	) -> Any:
		appended_query = baseQuery\
			.select_from(stations_tbl) \
			.join(stations_tags_tbl, st.pk == sttg.stationFk) \
			.join(songs_tags, sgtg.tagFk == sttg.tagFk) \
			.join(songs, sg.pk == sgtg.songFk) \
			.join(albums, sg.albumFk == ab.pk, isouter=True) \
			.join(song_artist, sg.pk == sgar.songFk, isouter=True) \
			.join(artists, sgar.artistFk == ar.pk, isouter=True) \

		if stationPk:
			query = appended_query.where(st.pk == stationPk)
		elif stationName:
			query = appended_query.where(func.lower(st.name) == func.lower(stationName))
		else:
			raise ValueError("Either stationName or pk must be provided")
		return query

	def song_catalogue_count(
		self,
		stationPk: Optional[int]=None,
		stationName: Optional[str]=None
	) -> int:
		baseQuery = select(func.count(1))
		query = self._attach_catalogue_joins(baseQuery, stationPk, stationName)
		count = self.conn.execute(query).scalar() or 0
		return count

	def get_station_song_catalogue(
		self,
		stationPk: Optional[int]=None,
		stationName: Optional[str]=None,
		page: int = 0,
		limit: Optional[int]=None
	) -> Iterator[SongItem]:
		offset = page * limit if limit else 0

		baseQuery = select(
			sg.pk,
			sg.name.label("song"),
			ab.name.label("album"), \
			ar.name.label("artist"), \
		)
		query = self._attach_catalogue_joins(baseQuery, stationPk, stationName)\
			.offset(offset)\
			.limit(limit)
		records = self.conn.execute(query)
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield SongItem(cast(int,row.pk),
				cast(str, row.song),
				cast(str, row.album),
				cast(str, row.artist)
			)

	def can_song_be_queued_to_station(self, songPk: int, stationPk: int) -> bool:
		query = select(func.count(1)).select_from(songs_tags)\
			.join(stations_tags_tbl, (sttg.tagFk == sgtg.tagFk)\
				& (sttg.stationFk == stationPk))\
			.where(sgtg.songFk == songPk)
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False

	def get_tags_count(self) -> int:
		query = select(func.count(1)).select_from(tags_tbl)
		count = self.conn.execute(query).scalar() or 0
		return count

	def get_tags(
		self,
		page: int = 0,
		pageSize: Optional[int]=None,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None,
		tagIds: Optional[Iterable[int]]=None
	) -> Iterator[Tag]:
		offset = page * pageSize if pageSize else 0
		query = select(tg.pk, tg.name).select_from(tags_tbl)
		if stationId:
			query = query.join(stations_tags_tbl, tg.pk == sttg.tagFk)\
				.where(sttg.stationFk == stationId)
		elif stationName:
			searchStr = SearchNameString.format_name_for_search(stationName)
			query = query.join(stations_tags_tbl, tg.pk == sttg.tagFk)\
				.join(stations_tbl, sttg.stationFk == st.pk)\
				.where(func.format_name_for_search(st.name).like(f"%{searchStr}%"))
		if tagIds:
			query = query.where(tg.pk.in_(tagIds))
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query)
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield Tag(
				cast(int,row.pk),
				cast(str, row.name)
			)

	def remove_tags_for_station(self, stationId: int, tagIds: Iterable[int]) -> int:
		if not stationId:
			return 0
		tagIds = tagIds or []
		delStmt = delete(stations_tags_tbl).where(sttg.stationFk == stationId)\
			.where(sttg.tagFk.in_(tagIds))
		return cast(int, self.conn.execute(delStmt).rowcount)


	def add_tags_to_station(
		self,
		stationId: int,
		tags: Sequence[Tag],
		userId: Optional[int]=0
	) -> Iterable[Tag]:
		if stationId is None or not tags:
			return []
		uniqueTags = set(tags)
		uniqueTagIds = {t.id for t in uniqueTags}
		existingTagIds = {t.id for t in self.get_tags(stationId=stationId)}
		outTagIds = existingTagIds - uniqueTagIds
		inTagIds = uniqueTagIds - existingTagIds
		self.remove_tags_for_station(stationId, outTagIds)
		if not inTagIds:
			return uniqueTags
		lastModifiedUserId: Any = userId
		tagParams = [{
			"stationFk": stationId,
			"tagFk": t,
			"lastModifiedByUserFk": lastModifiedUserId,
			"lastModifiedTimestamp": self.get_datetime().timestamp()
		} for t in inTagIds]
		stmt = insert(stations_tags_tbl)
		self.conn.execute(stmt, tagParams)
		return uniqueTags

	def _is_stationName_used(self, stationName: SavedNameString) -> bool:
		queryAny: str = select(func.count(1)).select_from(stations_tbl)\
				.where(func.format_name_for_save(st.name) == str(stationName))
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False

	def is_stationName_used(self, stationName: str) -> bool:
		cleanedStationName = SavedNameString(stationName)
		if not cleanedStationName:
			return True
		return self._is_stationName_used(cleanedStationName)

	def get_station_for_edit(
		self,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None,
	) -> Optional[StationInfo]:
		query = select(st.pk, st.name, st.displayName)
		if stationId:
			query = query.where(st.pk == stationId)
		elif stationName:
			query = query.where(st.name == stationName)
		else:
			return None
		row = self.conn.execute(query).fetchone()
		tags = self.get_tags(stationId=stationId)
		if not row:
			return None
		return StationInfo(
			stationId or row["pk"],
			row["name"],
			row["displayName"],
			list(tags)
		)

	def save_tag(
		self,
		tagName: str,
		tagId: Optional[int]=None,
		userId: Optional[int]=None
	) -> Tag:
		if not tagName and not tagId:
			return Tag(-1, "")
		upsert = update if tagId else insert
		savedName = SavedNameString(tagName)
		stmt = upsert(tags_tbl).values(
			name = str(savedName),
			lastModifiedByUserFk = userId,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		if tagId:
			stmt = stmt.where(tg.pk == tagId)
		try:
			res = self.conn.execute(stmt)

			affectedPk: int = tagId if tagId else res.lastrowid
			return Tag(affectedPk, str(savedName))
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{tagName} is already used.", "tagName"
				)]
			)

	def delete_tag(self, tagId: int) -> int:
		stmt = delete(tags_tbl).where(tg.pk == tagId)
		res = self.conn.execute(stmt)
		return cast(int, res.rowcount) or 0


	def save_station(
		self,
		station: StationCreationInfo,
		stationId: Optional[int]=None,
		userId: Optional[int]=None
	) -> Optional[StationInfo]:
		if not station:
			return self.get_station_for_edit(stationId)
		upsert = update if stationId else insert
		savedName = SavedNameString(station.stationName)
		savedDisplayName = SavedNameString(station.displayName)
		stmt = upsert(stations_tbl).values(
			name = str(savedName),
			displayName = str(savedDisplayName),
			lastModifiedByUserFk = userId,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		if stationId:
			stmt = stmt.where(st.pk == stationId)
		res = self.conn.execute(stmt)

		affectedPk: int = stationId if stationId else res.lastrowid
		resultTags = self.add_tags_to_station(affectedPk, station.tags, userId)
		return StationInfo(
			affectedPk,
			str(savedName),
			str(savedDisplayName),
			list(resultTags)
		)
