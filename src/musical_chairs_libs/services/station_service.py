#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
from typing import (
	Any,
	Iterator,
	Optional,
	cast,
	Iterable,
	Union,
	Tuple
)
from dataclasses import asdict
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import Row
from sqlalchemy.engine import Connection
from sqlalchemy import (
	select,
	func,
	insert,
	update,
	or_
)
from sqlalchemy.sql import ColumnCollection
from itertools import chain
from musical_chairs_libs.tables import (
	stations as stations_tbl, st_pk, st_name, st_displayName, st_procId,
	songs, sg_pk, sg_name, sg_path,
	station_queue, q_stationFk, q_requestedTimestamp, q_requestedByUserFk,
	albums, ab_name,
	artists, ar_name,
	song_artist,
	stations_songs as stations_songs_tbl, stsg_songFk, stsg_stationFk,
	station_user_permissions as station_user_permissions_tbl, stup_pk,
	stup_role, stup_stationFk, stup_userFk, stup_count, stup_span, stup_priority
)
from musical_chairs_libs.dtos_and_utilities import (
	StationInfo,
	SongListDisplayItem,
	StationCreationInfo,
	SavedNameString,
	SearchNameString,
	get_datetime,
	build_error_obj,
	Sentinel,
	missing,
	AccountInfo,
	StationUserInfo,
	ActionRule,
	IllegalOperationError,
	UserRoleDef,
	AlreadyUsedError,
	UserRoleDomain
)
from .env_manager import EnvManager
from .template_service import TemplateService

sg: ColumnCollection = songs.columns
st: ColumnCollection = stations_tbl.columns
sgar: ColumnCollection = song_artist.columns
ab: ColumnCollection = albums.columns
ar: ColumnCollection = artists.columns


class StationService:

	def __init__(
		self,
		conn: Optional[Connection]=None,
		envManager: Optional[EnvManager]=None,
		templateService: Optional[TemplateService]=None
	):
		if not conn:
			if not envManager:
				envManager = EnvManager()
			conn = envManager.get_configured_db_connection()
		if not templateService:
			templateService = TemplateService()
		self.conn = conn
		self.template_service = templateService
		self.__security_scope_lookup = {
			UserRoleDef.StationRequest.value: self.calc_when_user_can_next_request_song
		}
		self.get_datetime = get_datetime

	def get_station_id(self, stationName: str) -> Optional[int]:
		query = select(st.pk) \
			.select_from(stations_tbl) \
			.where(func.lower(st.name) == func.lower(stationName))
		row = self.conn.execute(query).fetchone()
		pk: Optional[int] = cast(int,row.pk) if row else None #pyright: ignore [reportGeneralTypeIssues]
		return pk

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

	def __attach_catalogue_joins(
		self,
		baseQuery: Any,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None
	) -> Any:
		appended_query = baseQuery\
			.select_from(stations_tbl) \
			.join(stations_songs_tbl, st.pk == stsg_stationFk) \
			.join(songs, sg.pk == stsg_songFk) \
			.join(albums, sg.albumFk == ab.pk, isouter=True) \
			.join(song_artist, sg.pk == sgar.songFk, isouter=True) \
			.join(artists, sgar.artistFk == ar.pk, isouter=True) \

		if stationId:
			query = appended_query.where(st.pk == stationId)
		elif stationName:
			query = appended_query.where(func.lower(st.name) == func.lower(stationName))
		else:
			raise ValueError("Either stationName or pk must be provided")
		return query

	def song_catalogue_count(
		self,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None
	) -> int:
		baseQuery = select(func.count(1))
		query = self.__attach_catalogue_joins(baseQuery, stationId, stationName)
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
			sg_pk,
			sg_path,
			sg_name,
			ab_name.label("album"),
			ar_name.label("artist"),
		)
		query = self.__attach_catalogue_joins(baseQuery, stationPk, stationName)\
			.offset(offset)\
			.limit(limit)
		records = self.conn.execute(query)
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield SongListDisplayItem(
				id=cast(int,row[sg_pk]),
				path=cast(str, row[sg_path]),
				name=cast(str, row[sg_name]),
				album=cast(str, row["album"]),
				artist=cast(str, row["artist"]),
				queuedTimestamp=0
			)

	def can_song_be_queued_to_station(self, songId: int, stationId: int) -> bool:
		query = select(func.count(1)).select_from(stations_songs_tbl)\
			.where(stsg_songFk == songId)\
			.where(stsg_stationFk == stationId)
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False

	def __is_stationName_used(
		self,
		id: Optional[int],
		stationName: SavedNameString
	) -> bool:
		queryAny: str = select(st_pk, st_name).select_from(stations_tbl)\
				.where(func.format_name_for_save(st.name) == str(stationName))\
				.where(st_pk != id)
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False

	def is_stationName_used(self, id: Optional[int], stationName: str) -> bool:
		cleanedStationName = SavedNameString(stationName)
		if not cleanedStationName:
			return True
		return self.__is_stationName_used(id, cleanedStationName)

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
			self.template_service.create_station_files(
				str(savedName),
				str(savedDisplayName)
			)
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{savedName} is already used.", "name"
				)]
			)

		affectedPk: int = stationId if stationId else cast(int,res.lastrowid)
		return StationInfo(
			id=affectedPk,
			name=str(savedName),
			displayName=str(savedDisplayName),
		)

	def __get_station_rules(
		self,
		userId: int,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None,
	) -> Tuple[Optional[int],Iterator[ActionRule]]:
		query = select(
			st_pk,
			stup_role,
			stup_span,
			stup_count,
			stup_priority,
			stup_pk
		).select_from(station_user_permissions_tbl)\
			.join(stations_tbl, stup_stationFk == st_pk,isouter=True)\
			.where(stup_userFk == userId)
		if stationId:
			query = query.where(or_(st_pk == stationId, st_pk.is_(None)))
		elif stationName:
			query = query.where(or_(st_name == stationName, st_name.is_(None)))
		else:
			return None, iter([])
		query = query.order_by(stup_role, st_pk)
		records = self.conn.execute(query).fetchall()
		fetchedStationId = next(
			(row[st_pk] for row in records if row[st_pk]),
			None
		)
		generator = (ActionRule(
				row[stup_role],
				row[stup_span],
				row[stup_count],
				row[stup_priority] if row[stup_priority] else 1 if row[st_pk] else 0,
				row[stup_pk],
				UserRoleDomain.Station
			) for row in records)
		return fetchedStationId, generator


	def get_station_user(
		self,
		user: AccountInfo,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None,
	) -> StationUserInfo:

		fetchedStationId, rules_generator = self.__get_station_rules(
			user.id,
			stationId,
			stationName
		)
		roles = sorted(chain(
			user.roles,
			ActionRule.best_rules_generator(rules_generator)
		), key=lambda r: r.name)
		userDict = asdict(user)
		userDict["roles"] = roles
		return StationUserInfo(
			**userDict,
			stationId=fetchedStationId
		)

	def get_user_request_history(
		self,
		userId: int,
		selectedRule: ActionRule,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None
	) -> Iterator[float]:
		currentTimestamp = self.get_datetime().timestamp()
		fromTimestamp = currentTimestamp - selectedRule.span
		query = select(q_requestedTimestamp).select_from(station_queue)\
			.where(q_requestedTimestamp >= fromTimestamp)\
			.where(q_requestedByUserFk == userId)
		if selectedRule.domain == UserRoleDomain.Station:
			if stationId:
				query = query.where(q_stationFk == stationId)
			elif stationName:
				query.join(stations_tbl, st_pk == q_stationFk)\
					.where(func.format_name_for_search(st_name)
						== SearchNameString.format_name_for_search(stationName))
			else:
				raise ValueError("Either stationName or id must be provided")
		query = query.order_by(q_requestedTimestamp)\
			.limit(selectedRule.count)
		records = self.conn.execute(query)
		for row in cast(Iterable[Row], records):
			yield row[q_requestedTimestamp]

	def __calc_when_user_can_noop(
		self,
		userId: int,
		selectedRule: ActionRule,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None,
	) -> float:
		return 0

	def calc_when_user_can_next_request_song(
		self,
		userId: int,
		selectedRule: ActionRule,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None,
	) -> float:
		if selectedRule.noLimit:
			return 0
		if selectedRule.blocked:
			raise IllegalOperationError(
				f"{userId} cannot make requests on this station"
			)
		prevRequestTimestamps = [
				r for r in
				self.get_user_request_history(
					userId,
					selectedRule,
					stationId,
					stationName
				)
			]
		if len(prevRequestTimestamps) == 0:
			return 0
		if len(prevRequestTimestamps) == selectedRule.count:
			return prevRequestTimestamps[0] + selectedRule.span
		return 0

	def calc_when_user_can_next_do_action(
		self,
		userId: int,
		selectedRule: ActionRule,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None,
	) -> float:
		calcWhenFn = self.__security_scope_lookup.get(
			selectedRule.name,
			self.__calc_when_user_can_noop
		)
		return calcWhenFn(userId, selectedRule, stationId, stationName)

