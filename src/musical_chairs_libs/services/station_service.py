#pyright: reportMissingTypeStubs=false
from typing import (
	Any,
	Iterator,
	Optional,
	cast,
	Iterable,
	Union,
	Tuple,
	overload
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import Row
from sqlalchemy.engine import Connection
from sqlalchemy.sql.expression import Select, CTE
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.schema import Column
from sqlalchemy import (
	select,
	func,
	insert,
	update,
	or_,
	and_,
	union_all,
	literal as dbLiteral  #pyright: ignore [reportUnknownVariableType]
)
from musical_chairs_libs.tables import (
	stations as stations_tbl, st_pk, st_name, st_displayName, st_procId,
	st_ownerFk, st_requestSecurityLevel, st_viewSecurityLevel,
	songs, sg_pk, sg_name, sg_path, sg_albumFk,
	station_queue, q_stationFk, q_requestedTimestamp, q_requestedByUserFk,
	albums, ab_name, ab_pk,
	artists, ar_name, ar_pk,
	song_artist, sgar_songFk, sgar_artistFk,
	stations_songs as stations_songs_tbl, stsg_songFk, stsg_stationFk,
	station_user_permissions as station_user_permissions_tbl, stup_pk,
	stup_role, stup_stationFk, stup_userFk, stup_count, stup_span, stup_priority,
	users as user_tbl, u_username, u_pk, u_displayName,
	ur_userFk, ur_role, ur_count, ur_span, ur_priority
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
	ActionRule,
	IllegalOperationError,
	UserRoleDef,
	AlreadyUsedError,
	UserRoleDomain,
	get_station_owner_rules,
	RulePriorityLevel,
	OwnerInfo,
	MinItemSecurityLevel
)
from .env_manager import EnvManager
from .template_service import TemplateService
from .song_info_service import SongInfoService


class StationService:

	def __init__(
		self,
		conn: Optional[Connection]=None,
		envManager: Optional[EnvManager]=None,
		templateService: Optional[TemplateService]=None,
		songInfoService: Optional[SongInfoService]=None,
	):
		if not conn:
			if not envManager:
				envManager = EnvManager()
			conn = envManager.get_configured_db_connection()
		if not templateService:
			templateService = TemplateService()
		if not songInfoService:
			songInfoService = SongInfoService(conn)
		self.conn = conn
		self.template_service = templateService
		self.song_info_service = songInfoService
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
		row = self.conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
		pk: Optional[int] = cast(int,row[st_pk]) if row else None #pyright: ignore [reportGeneralTypeIssues]
		return pk

	def __build_rules_query__(self, userId: int) -> Select:
		return union_all(
			select(
				stup_stationFk.label("rule_stationFk"), #pyright: ignore [reportUnknownMemberType]
				stup_role.label("rule_name"), #pyright: ignore [reportUnknownMemberType]
				stup_count.label("rule_count"), #pyright: ignore [reportUnknownMemberType]
				stup_span.label("rule_span"), #pyright: ignore [reportUnknownMemberType]
				coalesce(
					stup_priority, #pyright: ignore [reportUnknownMemberType]
					RulePriorityLevel.STATION_PATH.value
				).label("rule_priority"),
				dbLiteral(UserRoleDomain.Station.value).label("rule_domain") #pyright: ignore [reportUnknownMemberType]
			).where(stup_userFk == userId),
			select(
				dbLiteral(-1).label("rule_stationFk"), #pyright: ignore [reportUnknownMemberType]
				ur_role.label("rule_name"), #pyright: ignore [reportUnknownMemberType]
				ur_count.label("rule_count"), #pyright: ignore [reportUnknownMemberType]
				ur_span.label("rule_span"), #pyright: ignore [reportUnknownMemberType]
				coalesce(
					ur_priority, #pyright: ignore [reportUnknownMemberType]
					RulePriorityLevel.SITE.value
				).label("rule_priority"),
				dbLiteral(UserRoleDomain.Site.value).label("rule_domain") #pyright: ignore [reportUnknownMemberType]
			).where(ur_userFk == userId),
			select(
				dbLiteral(None).label("rule_stationFk"), #pyright: ignore [reportUnknownMemberType]
				dbLiteral("shim").label("rule_name"), #pyright: ignore [reportUnknownMemberType]
				dbLiteral(0).label("rule_count"), #pyright: ignore [reportUnknownMemberType]
				dbLiteral(0).label("rule_span"), #pyright: ignore [reportUnknownMemberType]
				dbLiteral(0).label("rule_priority"), #pyright: ignore [reportUnknownMemberType]
				dbLiteral("").label("rule_domain") #pyright: ignore [reportUnknownMemberType]
			)
		)


	def __attach_user_joins__(
		self,
		query: Select,
		userId: int
	) -> Select:

		rulesQuery = self.__build_rules_query__(userId)
		rulesSubquery = cast(CTE, rulesQuery.cte()) #pyright: ignore [reportUnknownMemberType]
		canViewQuery= cast(CTE, select(
			rulesSubquery.c.rule_stationFk, #pyright: ignore [reportUnknownMemberType]
			rulesSubquery.c.rule_priority, #pyright: ignore [reportUnknownMemberType]
			rulesSubquery.c.rule_domain #pyright: ignore [reportUnknownMemberType]
		).where(
			or_(
				rulesSubquery.c.rule_name == UserRoleDef.STATION_VIEW.value, #pyright: ignore [reportUnknownMemberType]
				rulesSubquery.c.rule_name == "shim" #pyright: ignore [reportUnknownMemberType]
			)
		).cte())

		topSiteRule = cast(CTE, select(
			coalesce(
				func.max(canViewQuery.c.rule_priority), #pyright: ignore [reportUnknownMemberType]
				RulePriorityLevel.NONE.value
			).label("max")
		).where(
			canViewQuery.c.rule_domain == UserRoleDomain.Site.value #pyright: ignore [reportUnknownMemberType]
		).cte())

		query = query.join( #pyright: ignore [reportUnknownMemberType]
			rulesSubquery,
			rulesSubquery.c.rule_stationFk == st_pk, #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
			isouter=True
		).where(
			or_(
				st_pk.in_(select(canViewQuery.c.rule_stationFk).subquery()), #pyright: ignore [reportUnknownMemberType]
				and_(
					dbLiteral(UserRoleDomain.Site.value).in_( #pyright: ignore [reportUnknownMemberType]
						select(canViewQuery.c.rule_domain).subquery() #pyright: ignore [reportUnknownMemberType]
					),
					coalesce(
						st_viewSecurityLevel,
						MinItemSecurityLevel.RULED_USER.value
					) < select(topSiteRule.c.max).subquery() #pyright: ignore [reportUnknownMemberType]
				),
				coalesce(
					st_viewSecurityLevel,
					MinItemSecurityLevel.ANY_USER.value
				) < RulePriorityLevel.USER.value,
				and_(
					st_ownerFk == userId,
					coalesce(
						st_viewSecurityLevel,
						MinItemSecurityLevel.OWENER_USER.value
					) < RulePriorityLevel.OWNER.value
				)
			)
		)

		query = query.add_columns( #pyright: ignore [reportUnknownMemberType]
			cast(Column, rulesSubquery.c.rule_name), #pyright: ignore [reportUnknownMemberType]
			cast(Column, rulesSubquery.c.rule_count), #pyright: ignore [reportUnknownMemberType]
			cast(Column, rulesSubquery.c.rule_span), #pyright: ignore [reportUnknownMemberType]
			cast(Column, rulesSubquery.c.rule_priority) #pyright: ignore [reportUnknownMemberType]
		)
		return query

	def __row_to_station__(self, row: Row) -> StationInfo:
		return StationInfo(
			id=cast(int,row[st_pk]),
			name=cast(str,row[st_name]),
			displayName=cast(str,row[st_displayName]),
			isRunning=bool(row[st_procId]),
			owner=OwnerInfo(
				cast(int,row[st_ownerFk]),
				cast(str,row[u_username]),
				cast(str,row[u_displayName])
			),
			requestSecurityLevel=cast(int,row[st_requestSecurityLevel]),
			viewSecurityLevel=cast(int,row[st_viewSecurityLevel]),
		)

	def __row_to_action_rule__(self, row: Row) -> ActionRule:
		return ActionRule(
			cast(str,row["rule_name"]),
			cast(int,row["rule_span"]),
			cast(int,row["rule_count"]),
			#if priortity is explict use that
			#otherwise, prefer station specific rule vs non station specific rule
			cast(int,row["rule_priority"]) if row["rule_priority"] \
				else RulePriorityLevel.STATION_PATH.value,
			domain=UserRoleDomain.Station
		)

	def __generate_station_and_rules_from_rows__(
		self,
		rows: Iterable[Row],
		userId: Optional[int]
	) -> Iterator[StationInfo]:
		currentStation = None
		for row in rows:
			if not currentStation or currentStation.id != cast(int,row[st_pk]):
				if currentStation:
					stationOwner = currentStation.owner
					if stationOwner and stationOwner.id == userId:
						currentStation.rules.extend(get_station_owner_rules())
					yield currentStation
				currentStation = self.__row_to_station__(row)
				if row["rule_name"]:
					currentStation.rules.append(self.__row_to_action_rule__(row))
			else:
				currentStation.rules.append(self.__row_to_action_rule__(row))
		if currentStation:
			stationOwner = currentStation.owner
			if stationOwner and stationOwner.id == userId:
				currentStation.rules.extend(get_station_owner_rules())
			yield currentStation

	def get_stations(
		self,
		stationKeys: Union[int,str, Iterable[int], None]=None,
		ownerId: Union[int, None]=None,
		includeRules: bool=False,
		user: Optional[AccountInfo]=None
	) -> Iterator[StationInfo]:
		query = select(
			st_pk,
			st_name,
			st_displayName,
			st_procId,
			st_ownerFk,
			u_username,
			u_displayName,
			st_requestSecurityLevel,
			st_viewSecurityLevel
		).select_from(stations_tbl)\
		.join(user_tbl, st_ownerFk == u_pk, isouter=True)


		if user:
			query = self.__attach_user_joins__(query, user.id)
		else:
			query = query.where( #pyright: ignore [reportUnknownMemberType]
				coalesce(st_viewSecurityLevel, 0) == 0
			)
		if type(ownerId) is int:
			query = query.where(st_ownerFk == ownerId) #pyright: ignore [reportUnknownMemberType]
		if type(stationKeys) == int:
			query = query.where(st_pk == stationKeys) #pyright: ignore [reportUnknownMemberType]
		elif isinstance(stationKeys, Iterable) and not isinstance(stationKeys, str):
			query = query.where(st_pk.in_(stationKeys)) #pyright: ignore [reportUnknownMemberType]
		elif type(stationKeys) is str and not ownerId:
			raise ValueError("user must be provided when using station name")
		elif type(stationKeys) is str:
			searchStr = SearchNameString.format_name_for_search(stationKeys)
			query = query\
				.where(func.format_name_for_search(st_name).like(f"%{searchStr}%")) #pyright: ignore [reportUnknownMemberType]
		query = query.order_by(st_pk) #pyright: ignore [reportUnknownMemberType]
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]

		if user and includeRules:
			yield from self.__generate_station_and_rules_from_rows__(
				records,
				user.id
			)
		else:
			for row in cast(Iterable[Row],records):
				yield self.__row_to_station__(row)

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
		count = self.conn.execute(query).scalar() or 0 #pyright: ignore [reportUnknownMemberType]
		return count

	def get_station_song_catalogue(
		self,
		stationId: int,
		page: int = 0,
		limit: Optional[int]=None,
		user: Optional[AccountInfo]=None
	) -> Iterator[SongListDisplayItem]:
		offset = page * limit if limit else 0
		pathRuleTree = None
		if user:
			pathRuleTree = self.song_info_service.get_rule_path_tree(user)

		baseQuery = select(
			sg_pk,
			sg_path,
			sg_name,
			ab_name.label("album"), #pyright: ignore [reportUnknownMemberType]
			ar_name.label("artist"), #pyright: ignore [reportUnknownMemberType]
		)
		query = self.__attach_catalogue_joins(baseQuery, stationId)\
			.offset(offset)\
			.limit(limit)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		for row in records: #pyright: ignore [reportUnknownVariableType]
			rules = []
			if pathRuleTree:
				rules = list(pathRuleTree.valuesFlat(cast(str, row[sg_path])))
			yield SongListDisplayItem(
				id=cast(int,row[sg_pk]),
				path=cast(str, row[sg_path]),
				name=cast(str, row[sg_name]),
				album=cast(str, row["album"]),
				artist=cast(str, row["artist"]),
				queuedTimestamp=0,
				rules=rules
			)

	def can_song_be_queued_to_station(self, songId: int, stationId: int) -> bool:
		query = select(func.count(1)).select_from(stations_songs_tbl)\
			.where(stsg_songFk == songId)\
			.where(stsg_stationFk == stationId)
		countRes = self.conn.execute(query).scalar() #pyright: ignore [reportUnknownMemberType]
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
		countRes = self.conn.execute(queryAny).scalar() #pyright: ignore [reportUnknownMemberType]
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
		stationKey: Union[int, str, None]
	) -> Optional[StationInfo]:
		query = select(st_pk, st_name, st_displayName, st_ownerFk)
		if type(stationKey) is int:
			query = query.where(st_pk == stationKey)
		elif type(stationKey) is str:
			query = query.where(st_name == stationKey)
		else:
			return None
		row = self.conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
		if not row:
			return None
		return StationInfo(
			id=cast(int, row[st_pk]),
			name=cast(str, row[st_name]),
			displayName=cast(str, row[st_displayName]),
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
		else:
			stmt = stmt.values(ownerFk = user.id)
		try:
			res = self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]
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

		affectedId: int = stationId if stationId else cast(int,res.lastrowid) #pyright: ignore [reportUnknownMemberType]
		return StationInfo(
			id=affectedId,
			name=str(savedName),
			displayName=str(savedDisplayName)
		)

	@overload
	def get_station_rules(
		self,
		userId: int,
		stationKeys: Union[int, str],
		scopes: Union[str, Iterable[str], None]=None,
	) -> Iterator[ActionRule]:
		...

	@overload
	def get_station_rules(
		self,
		userId: int,
		stationKeys: Iterable[int],
		scopes: Union[str, Iterable[str], None]=None,
	) -> Iterator[Tuple[ActionRule, int]]:
		...

	def get_station_rules(
		self,
		userId: int,
		stationKeys: Union[int, str, Iterable[int]],
		scopes: Union[str, Iterable[str], None]=None,
	) -> Union[Iterator[ActionRule], Iterator[Tuple[ActionRule, int]]]:
		query = select(
			st_pk.label("rule_stationFk"), #pyright: ignore [reportUnknownMemberType],
			stup_role.label("rule_name"), #pyright: ignore [reportUnknownMemberType]
			stup_span.label("rule_span"), #pyright: ignore [reportUnknownMemberType]
			stup_count.label("rule_count"), #pyright: ignore [reportUnknownMemberType]
			stup_priority.label("rule_priority"), #pyright: ignore [reportUnknownMemberType]
			stup_pk
		).select_from(station_user_permissions_tbl)\
			.join(stations_tbl, stup_stationFk == st_pk,isouter=True)\
			.where(stup_userFk == userId)
		if type(stationKeys) is int:
			query = query.where(or_(st_pk == stationKeys, st_pk.is_(None)))
		elif isinstance(stationKeys, Iterable) and not type(stationKeys) is str:
			query = query.where(or_(st_pk.in_(stationKeys), st_pk.is_(None)))
		elif type(stationKeys) is str:
			query = query.where(or_(st_name == stationKeys, st_name.is_(None)))
		else:
			return iter([])
		if type(scopes) is str:
			query = query.where(stup_role == scopes)
		elif isinstance(scopes, Iterable):
			query = query.where(stup_role.in_(scopes))
		query = query.order_by(stup_role, st_pk)
		records = self.conn.execute(query).fetchall() #pyright: ignore [reportUnknownMemberType]
		if isinstance(stationKeys, Iterable) and not type(stationKeys) is str:
			yield from ((self.__row_to_action_rule__(row), cast(int, row[st_pk]))\
				for row in records
			)
		else:
			yield from (self.__row_to_action_rule__(row) for row in records)


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
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
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

