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
from musical_chairs_libs.tables import (
	stations as stations_tbl, st_pk, st_name, st_displayName, st_procId,
	st_ownerFk,
	songs, sg_pk, sg_name, sg_path, sg_albumFk,
	station_queue, q_stationFk, q_requestedTimestamp, q_requestedByUserFk,
	albums, ab_name, ab_pk,
	artists, ar_name, ar_pk,
	song_artist, sgar_songFk, sgar_artistFk,
	stations_songs as stations_songs_tbl, stsg_songFk, stsg_stationFk,
	station_user_permissions as station_user_permissions_tbl, stup_pk,
	stup_role, stup_stationFk, stup_userFk, stup_count, stup_span, stup_priority,
	users as user_tbl, u_username, u_pk
)
from musical_chairs_libs.dtos_and_utilities import (
	StationInfo,
	SongListDisplayItem,
	StationCreationInfo,
	SavedNameString,
	SearchNameString,
	get_datetime,
	build_error_obj,
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
			UserRoleDef.STATION_REQUEST.value:
				self.calc_when_user_can_next_request_song
		}
		self.get_datetime = get_datetime

	def get_station_id(
			self,
			stationName: str,
			userKey: Union[int, str]
		) -> Optional[int]:
		query = select(st_pk) \
			.select_from(stations_tbl) \
			.where(func.lower(st_name) == func.lower(stationName))
		if type(userKey) == int:
			query = query.where(st_ownerFk == userKey)
		elif type(userKey) == str:
			query = query.join(user_tbl, st_ownerFk == u_pk)\
				.where(u_username == userKey)
		row = self.conn.execute(query).fetchone()
		pk: Optional[int] = cast(int,row.pk) if row else None #pyright: ignore [reportGeneralTypeIssues]
		return pk

	def get_stations(
		self,
		stationKeys: Union[int,str, Iterable[int], None]=None,
		ownerKey: Union[int, str, None]=None
	) -> Iterator[StationInfo]:
		query = select(
			st_pk,
			st_name,
			st_displayName,
			st_procId
		).select_from(stations_tbl)
		if type(ownerKey) == int:
			query = query.where(st_ownerFk == ownerKey)
		elif type(ownerKey) == str:
			query = query.join(user_tbl, u_pk == st_ownerFk)\
				.where(u_username == ownerKey)
		if type(stationKeys) == int:
			query = query.where(st_pk == stationKeys)
		elif isinstance(stationKeys, Iterable):
			query = query.where(st_pk.in_(stationKeys))
		elif type(stationKeys) is str and not ownerKey:
			raise ValueError("user must be provided when using station name")
		elif type(stationKeys) is str:
			searchStr = SearchNameString.format_name_for_search(stationKeys)
			query = query\
				.where(func.format_name_for_search(st_name).like(f"%{searchStr}%"))
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
		stationId: int
	) -> Any:
		query = baseQuery\
			.select_from(stations_tbl) \
			.join(stations_songs_tbl, st_pk == stsg_stationFk) \
			.join(songs, sg_pk == stsg_songFk) \
			.join(albums, sg_albumFk == ab_pk, isouter=True) \
			.join(song_artist, sg_pk == sgar_songFk, isouter=True) \
			.join(artists, sgar_artistFk == ar_pk, isouter=True) \
			.where(st_pk == stationId)


		return query

	def song_catalogue_count(
		self,
		stationId: int,
	) -> int:
		baseQuery = select(func.count(1))
		query = self.__attach_catalogue_joins(baseQuery, stationId)
		count = self.conn.execute(query).scalar() or 0
		return count

	def get_station_song_catalogue(
		self,
		stationId: int,
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
		query = self.__attach_catalogue_joins(baseQuery, stationId)\
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
		stationName: SavedNameString,
		userId: int,
	) -> bool:
		queryAny: str = select(st_pk, st_name).select_from(stations_tbl)\
				.where(func.format_name_for_save(st_name) == str(stationName))\
				.where(st_ownerFk == userId)\
				.where(st_pk != id)
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False

	def is_stationName_used(
		self,
		id: Optional[int],
		stationName: str,
		userId: int
	) -> bool:
		cleanedStationName = SavedNameString(stationName)
		if not cleanedStationName:
			return True
		return self.__is_stationName_used(id, cleanedStationName, userId)

	def get_station_for_edit(
		self,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None,
	) -> Optional[StationInfo]:
		query = select(st_pk, st_name, st_displayName)
		if stationId:
			query = query.where(st_pk == stationId)
		elif stationName:
			query = query.where(st_name == stationName)
		else:
			return None
		row = self.conn.execute(query).fetchone()
		if not row:
			return None
		return StationInfo(
			id=stationId or cast(int, row["pk"]),
			name=cast(str, row["name"]),
			displayName=cast(str, row["displayName"])
		)

	def save_station(
		self,
		station: StationCreationInfo,
		user: AccountInfo,
		stationId: Optional[int]=None,
	) -> Optional[StationInfo]:
		if not station:
			return self.get_station_for_edit(stationId)
		upsert = update if stationId else insert
		savedName = SavedNameString(station.name)
		savedDisplayName = SavedNameString(station.displayName)
		stmt = upsert(stations_tbl).values(
			name = str(savedName),
			displayName = str(savedDisplayName),
			lastModifiedByUserFk = user.id,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		if stationId:
			stmt = stmt.where(st_pk == stationId)
		try:
			res = self.conn.execute(stmt)
			affectedId = stationId if stationId else cast(int, res.lastrowid) #pyright: ignore [reportUnknownMemberType]
			self.template_service.create_station_files(
				affectedId,
				str(savedName),
				str(savedDisplayName),
				user.username
			)
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{savedName} is already used.", "name"
				)]
			)

		affectedId: int = stationId if stationId else cast(int,res.lastrowid)
		return StationInfo(
			id=affectedId,
			name=str(savedName),
			displayName=str(savedDisplayName),
		)

	def __get_station_rules(
		self,
		userId: int,
		stationKey: Union[int, str]
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
		if type(stationKey) == int:
			query = query.where(or_(st_pk == stationKey, st_pk.is_(None)))
		elif type(stationKey) == str:
			query = query.where(or_(st_name == stationKey, st_name.is_(None)))
		else:
			return None, iter([])
		query = query.order_by(stup_role, st_pk)
		records = self.conn.execute(query).fetchall()
		fetchedStationId = next(
			(cast(int, row[st_pk]) for row in records if row[st_pk]),
			None
		)
		generator = (ActionRule(
				cast(str, row[stup_role]),
				cast(int, row[stup_span]),
				cast(int, row[stup_count]),
				cast(int,row[stup_priority])
					#if priortity is explict use that
					#otherwise, prefer station specific rule vs non station specific rule
					if row[stup_priority] else 1 if row[st_pk] else 0,
				cast(int, row[stup_pk]),
				UserRoleDomain.Station
			) for row in records)
		return fetchedStationId, generator


	def get_station_user(
		self,
		user: AccountInfo,
		stationKey: Union[int, str]
	) -> StationUserInfo:

		fetchedStationId, rules_generator = self.__get_station_rules(
			user.id,
			stationKey
		)
		roles = [*rules_generator]
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
		stationKey: Union[int, str]
	) -> Iterator[float]:
		currentTimestamp = self.get_datetime().timestamp()
		fromTimestamp = currentTimestamp - selectedRule.span
		query = select(q_requestedTimestamp).select_from(station_queue)\
			.where(q_requestedTimestamp >= fromTimestamp)\
			.where(q_requestedByUserFk == userId)
		if selectedRule.domain == UserRoleDomain.Station:
			if type(stationKey) == int:
				query = query.where(q_stationFk == stationKey)
			elif type(stationKey) == str:
				query.join(stations_tbl, st_pk == q_stationFk)\
					.where(func.format_name_for_search(st_name)
						== SearchNameString.format_name_for_search(stationKey))
			else:
				raise ValueError("Either stationName or id must be provided")
		query = query.order_by(q_requestedTimestamp)\
			.limit(selectedRule.count)
		records = self.conn.execute(query)
		for row in cast(Iterable[Row], records):
			yield cast(float,row[q_requestedTimestamp])

	def __calc_when_user_can_noop(
		self,
		userId: int,
		selectedRule: ActionRule,
		stationKey: Union[int, str]
	) -> float:
		return 0

	def calc_when_user_can_next_request_song(
		self,
		userId: int,
		selectedRule: ActionRule,
		stationKey: Union[int, str]
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
					stationKey
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
		stationKey: Union[int, str]
	) -> float:
		calcWhenFn = self.__security_scope_lookup.get(
			selectedRule.name,
			self.__calc_when_user_can_noop
		)
		return calcWhenFn(userId, selectedRule, stationKey)

