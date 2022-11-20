#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
from typing import\
	Any,\
	Iterator,\
	Optional,\
	cast,\
	Iterable,\
	Union,\
	Sequence
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
	stations as stations_tbl, st_pk, st_name, st_displayName, st_procId,\
	songs, \
	albums, \
	artists, \
	song_artist,\
	stations_songs as stations_songs_tbl, stsg_songFk, stsg_stationFk
from musical_chairs_libs.dtos_and_utilities import\
	StationInfo, \
	SongListDisplayItem,\
	StationCreationInfo,\
	SavedNameString,\
	SearchNameString,\
	get_datetime,\
	build_error_obj,\
	Sentinel,\
	missing
from musical_chairs_libs.errors import AlreadyUsedError
from .env_manager import EnvManager
from .template_service import TemplateService
from .process_service import ProcessService

sg: ColumnCollection = songs.columns
st: ColumnCollection = stations_tbl.columns
sgar: ColumnCollection = song_artist.columns
ab: ColumnCollection = albums.columns
ar: ColumnCollection = artists.columns


class StationService:

	def __init__(self,
		conn: Optional[Connection]=None,
		envManager: Optional[EnvManager]=None,
		processManager: Optional[ProcessService]=None,
		templateService: Optional[TemplateService]=None
	):
		if not conn:
			if not envManager:
				envManager = EnvManager()
			conn = envManager.get_configured_db_connection()
		if not processManager:
			processManager = ProcessService()
		if not templateService:
			templateService = TemplateService()
		self.conn = conn
		self.process_manager = processManager
		self.template_service = templateService
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

	def _unset_station_procs(self, procIds: Iterable[int]) -> None:
		stmt = update(stations_tbl)\
			.values(procId = None) \
			.where(st_procId.in_(procIds))
		self.conn.execute(stmt)

	def disable_stations(
		self,
		stationIds: Optional[Iterable[int]],
		stationNames: Optional[Sequence[str]]=None
	) -> None:
		query = select(st_procId).where(st_procId.is_not(None))
		if isinstance(stationIds, Iterable):
			query = query.where(st_pk.in_(stationIds))
		elif isinstance(stationNames, Iterable):
			if len(stationNames) > 1 or stationNames[0] != "*":
				query = query\
					.where(func.format_name_for_search(st_name).in_(
							str(SearchNameString.format_name_for_search(s)) for s
							in stationNames
						))
		rows = self.conn.execute(query)
		pids = [cast(int, row[st_procId]) for row in cast(Iterable[Row], rows)]
		for pid in pids:
			self.process_manager.end_process(pid)
		self._unset_station_procs(pids)


	#deprecated. use disable_stations instead
	def end_all_stations(self) -> None:
		query = select(st.procId).select_from(stations_tbl)\
			.where(st.procId != None)
		for row in self.conn.execute(query).fetchall():
			pid: int = row.procId  #pyright: ignore [reportGeneralTypeIssues]
			self.process_manager.end_process(pid)
		stmt = update(stations_tbl).values(procId = None)
		self.conn.execute(stmt)

	def get_station_id(self, stationName: str) -> Optional[int]:
		query = select(st.pk) \
			.select_from(stations_tbl) \
			.where(func.lower(st.name) == func.lower(stationName))
		row = self.conn.execute(query).fetchone()
		pk: Optional[int] = row.pk if row else None #pyright: ignore [reportGeneralTypeIssues]
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
		self.template_service.create_station_files(stationName, displayName)
		return True

	def remove_station(self, stationName: str) -> None:
		stationId = self.get_station_id(stationName)
		assignedTagsDel = delete(stations_songs_tbl)\
			.where(stsg_stationFk == stationId)
		self.conn.execute(assignedTagsDel)
		stationDel = delete(stations_tbl).where(st.stationPk == stationId)
		self.conn.execute(stationDel)

	def get_stations(
		self,
		stationId: Union[Optional[int], Sentinel]=missing,
		stationName: Union[Optional[str], Sentinel]=missing,
		#sentinel is only needed for id because None and 0 are both legit values
		stationIds: Optional[Iterable[int]]=None,
		stationNames: Optional[Iterable[str]]=None
	) -> Iterator[StationInfo]:
		query = select(
			st_pk,
			st_name,
			st_displayName,
			st_procId
		).select_from(stations_tbl)
		if stationId:
			query = query.where(st_pk == stationId)
		elif stationName and type(stationName) is str:
			searchStr = SearchNameString.format_name_for_search(stationName)
			query = query\
				.where(func.format_name_for_search(st_name).like(f"%{searchStr}%"))
		elif isinstance(stationIds, Iterable):
			query = query.where(st_pk.in_(stationIds))
		elif isinstance(stationNames, Iterable):
				query = query\
					.where(func.format_name_for_search(st_name).in_(
						str(SearchNameString.format_name_for_search(s)) for s
						in stationNames
					))
		records = self.conn.execute(query)
		for row in cast(Iterable[Row], records):
			yield StationInfo(
				id=cast(int,row[st_pk]),
				name=cast(str,row[st_name]),
				displayName=cast(str,row[st_displayName]),
				isRunning=bool(row[st_procId])
			)

	def _attach_catalogue_joins(
		self,
		baseQuery: Any,
		stationPk: Optional[int]=None,
		stationName: Optional[str]=None
	) -> Any:
		appended_query = baseQuery\
			.select_from(stations_tbl) \
			.join(stations_songs_tbl, st.pk == stsg_stationFk) \
			.join(songs, sg.pk == stsg_songFk) \
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
	) -> Iterator[SongListDisplayItem]:
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
			yield SongListDisplayItem(
				id=cast(int,row.pk),
				name=cast(str, row.song),
				album=cast(str, row.album),
				artist=cast(str, row.artist)
			)

	def can_song_be_queued_to_station(self, songId: int, stationId: int) -> bool:
		query = select(func.count(1)).select_from(stations_songs_tbl)\
			.where(stsg_songFk == songId)\
			.where(stsg_stationFk == stationId)
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False

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
		if not row:
			return None
		return StationInfo(
			id=stationId or row["pk"],
			name=row["name"],
			displayName=row["displayName"]
		)

	def save_station(
		self,
		station: StationCreationInfo,
		stationId: Optional[int]=None,
		userId: Optional[int]=None
	) -> Optional[StationInfo]:
		if not station:
			return self.get_station_for_edit(stationId)
		upsert = update if stationId else insert
		savedName = SavedNameString(station.name)
		savedDisplayName = SavedNameString(station.displayName)
		stmt = upsert(stations_tbl).values(
			name = str(savedName),
			displayName = str(savedDisplayName),
			lastModifiedByUserFk = userId,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		if stationId:
			stmt = stmt.where(st.pk == stationId)
		try:
			res = self.conn.execute(stmt)
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{savedName} is already used.", "name"
				)]
			)

		affectedPk: int = stationId if stationId else res.lastrowid
		return StationInfo(
			id=affectedPk,
			name=str(savedName),
			displayName=str(savedDisplayName),
		)

	def enable_stations(self,
		stationIds: Optional[Iterable[int]],
		stationNames: Optional[Sequence[str]]
	) -> None:
		stations: list[StationInfo] = []
		if stationNames and len(stationNames) == 1 and stationNames[0] == "*":
			stations = list(self.get_stations())
		else:
			stations = list(self.get_stations(
				stationIds=stationIds,
				stationNames=stationNames
			))
		for station in stations:
			self.process_manager.startup_station(station.name)