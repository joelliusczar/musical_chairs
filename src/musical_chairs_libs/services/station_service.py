#pyright: reportMissingTypeStubs=false
from typing import (
	Any,
	Iterator,
	Optional,
	cast,
	Iterable,
	Union,
	Collection,
	Tuple
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.engine import Connection
from sqlalchemy.sql.expression import Select, case, true, false
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.schema import Column
from sqlalchemy import (
	select,
	func,
	insert,
	update,
	or_,
	and_,
	literal as dbLiteral,  #pyright: ignore [reportUnknownVariableType]
	delete,
	String,
	Integer,
	Float,
	Update
)
from musical_chairs_libs.tables import (
	stations as stations_tbl, st_pk, st_name, st_displayName, st_procId,
	st_ownerFk, st_requestSecurityLevel, st_viewSecurityLevel,
	songs, sg_pk, sg_name, sg_path, sg_albumFk,
	albums, ab_name, ab_pk,
	artists, ar_name, ar_pk,
	song_artist, sgar_songFk, sgar_artistFk,
	stations_songs as stations_songs_tbl, stsg_songFk, stsg_stationFk,
	station_user_permissions as station_user_permissions_tbl, stup_userFk,
	stup_stationFk, stup_role,
	users as user_tbl, u_username, u_pk, u_displayName, u_email, u_dirRoot,
	u_disabled
)
from musical_chairs_libs.dtos_and_utilities import (
	StationInfo,
	SongListDisplayItem,
	StationCreationInfo,
	SavedNameString,
	get_datetime,
	build_error_obj,
	AccountInfo,
	ActionRule,
	StationActionRule,
	UserRoleDef,
	AlreadyUsedError,
	UserRoleDomain,
	get_station_owner_rules,
	RulePriorityLevel,
	OwnerInfo,
	MinItemSecurityLevel,
	build_rules_query,
	row_to_action_rule,
	generate_user_and_rules_from_rows,
	normalize_opening_slash
)
from .template_service import TemplateService
from .song_info_service import SongInfoService
from .process_service import ProcessService


class StationService:

	def __init__(
		self,
		conn: Optional[Connection]=None,
		templateService: Optional[TemplateService]=None,
		songInfoService: Optional[SongInfoService]=None,
	):
		if not conn:
			raise RuntimeError("No connection provided")
		if not templateService:
			templateService = TemplateService()
		if not songInfoService:
			songInfoService = SongInfoService(conn)
		self.conn = conn
		self.template_service = templateService
		self.song_info_service = songInfoService
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

	def __attach_user_joins__(
		self,
		query: Select[
			Tuple[
				Integer,
				String,
				String,
				Integer,
				Integer,
				String,
				Union[String, None],
				int,
				Integer
			]
		],
		userId: int,
		scopes: Optional[Collection[str]]=None
	) -> Select[
			Tuple[
				Integer,
				String,
				String,
				Integer,
				Integer,
				String,
				Union[String, None],
				int,
				Integer
			]
		]:
		rulesQuery = build_rules_query(UserRoleDomain.Station, userId)
		rulesSubquery = rulesQuery.cte(name="rulesQuery")
		canViewQuery= select(
			rulesSubquery.c.rule_stationfk, #pyright: ignore [reportUnknownMemberType]
			rulesSubquery.c.rule_priority, #pyright: ignore [reportUnknownMemberType]
			rulesSubquery.c.rule_domain #pyright: ignore [reportUnknownMemberType]
		).where(
			rulesSubquery.c.rule_name.in_(scopes) if scopes else true(), #pyright: ignore [reportUnknownMemberType]
		).cte(name="canviewquery")

		topSiteRule = select(
			coalesce[int](
				func.max(canViewQuery.c.rule_priority), #pyright: ignore [reportUnknownMemberType]
				RulePriorityLevel.NONE.value
			).label("max")
		).where(
			canViewQuery.c.rule_domain == UserRoleDomain.Site.value
		).cte("topsiterule")

		ownerScopeSet = set(get_station_owner_rules(scopes))

		query = query.join(
			rulesSubquery,
			or_(
				rulesSubquery.c.rule_stationfk == st_pk, #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
				rulesSubquery.c.rule_stationfk == -1, #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
				rulesSubquery.c.rule_stationfk.is_(None) #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
			)
		).where(
			or_(
				coalesce(
					st_viewSecurityLevel,
					MinItemSecurityLevel.INVITED_USER.value
				) < select(coalesce[int](
							func.max(canViewQuery.c.rule_priority), #pyright: ignore [reportUnknownMemberType]
							RulePriorityLevel.NONE.value
						)).where(st_pk == canViewQuery.c.rule_stationfk).scalar_subquery(), #pyright: ignore [reportUnknownMemberType]
				and_(
					dbLiteral(UserRoleDomain.Site.value)
						.in_( #pyright: ignore [reportUnknownMemberType]
							select(canViewQuery.c.rule_domain) #pyright: ignore [reportUnknownMemberType]
						),
					coalesce(
						st_viewSecurityLevel,
						MinItemSecurityLevel.RULED_USER.value
					) < select(topSiteRule.c.max).scalar_subquery() #pyright: ignore [reportUnknownMemberType]
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
			),
		).where(
				or_(
					rulesSubquery.c.rule_name.in_(scopes) if scopes else true(), #pyright: ignore [reportUnknownMemberType]
					(st_ownerFk == userId) if scopes and ownerScopeSet else false()
				)
			)

		query = query.add_columns(
			cast(Column[String], rulesSubquery.c.rule_name),
			cast(Column[Float[float]], rulesSubquery.c.rule_count),
			cast(Column[Float[float]], rulesSubquery.c.rule_span),
			cast(Column[Integer], rulesSubquery.c.rule_priority),
			cast(Column[String], rulesSubquery.c.rule_domain)
		)
		return query

	def __row_to_station__(self, row: RowMapping) -> StationInfo:
		return StationInfo(
			id=row[st_pk],
			name=row[st_name],
			displayname=row[st_displayName],
			isrunning=bool(row[st_procId]),
			owner=OwnerInfo(
				row[st_ownerFk],
				row[u_username],
				row[u_displayName]
			),
			requestsecuritylevel=row["requestsecuritylevel"],
			viewsecuritylevel=row[st_viewSecurityLevel] \
				or MinItemSecurityLevel.PUBLIC.value,
		)

	def __generate_station_and_rules_from_rows__(
		self,
		rows: Iterable[RowMapping],
		userId: Optional[int],
		scopes: Optional[Collection[str]]=None
	) -> Iterator[StationInfo]:
		currentStation = None
		for row in rows:
			if not currentStation or currentStation.id != cast(int,row[st_pk]):
				if currentStation:
					stationOwner = currentStation.owner
					if stationOwner and stationOwner.id == userId:
						currentStation.rules.extend(get_station_owner_rules(scopes))
					currentStation.rules = ActionRule.sorted(currentStation.rules)
					yield currentStation
				currentStation = self.__row_to_station__(row)
				if cast(str,row["rule_domain"]) != "shim":
					currentStation.rules.append(row_to_action_rule(row))
			elif cast(str,row["rule_domain"]) != "shim":
				currentStation.rules.append(row_to_action_rule(row))
		if currentStation:
			stationOwner = currentStation.owner
			if stationOwner and stationOwner.id == userId:
				currentStation.rules.extend(get_station_owner_rules(scopes))
			currentStation.rules = ActionRule.sorted(currentStation.rules)
			yield currentStation

	def get_stations(
		self,
		stationKeys: Union[int,str, Iterable[int], None]=None,
		ownerId: Union[int, None]=None,
		user: Optional[AccountInfo]=None,
		scopes: Optional[Collection[str]]=None
	) -> Iterator[StationInfo]:
		query = select(
			st_pk,
			st_name,
			st_displayName,
			st_procId,
			st_ownerFk,
			u_username,
			u_displayName,
			coalesce[int](
				st_requestSecurityLevel,
				case(
					(st_viewSecurityLevel == MinItemSecurityLevel.PUBLIC.value, None),
					else_=st_viewSecurityLevel
				),
				MinItemSecurityLevel.ANY_USER.value
			).label("requestsecuritylevel"), #pyright: ignore [reportUnknownMemberType]
			st_viewSecurityLevel
		).select_from(stations_tbl)\
		.join(user_tbl, st_ownerFk == u_pk, isouter=True)

		if user:
			query = self.__attach_user_joins__(query, user.id, scopes)
		else:
			if scopes:
				return
			query = query.where(
				coalesce(st_viewSecurityLevel, 0) == 0
			)
		if type(ownerId) is int:
			query = query.where(st_ownerFk == ownerId)
		if type(stationKeys) == int:
			query = query.where(st_pk == stationKeys)
		elif isinstance(stationKeys, Iterable) and not isinstance(stationKeys, str):
			query = query.where(st_pk.in_(stationKeys))
		elif type(stationKeys) is str and not ownerId:
			raise ValueError("user must be provided when using station name")
		elif type(stationKeys) is str:
			query = query\
				.where(st_name.like(f"%{stationKeys}%"))
		query = query.order_by(st_pk)
		records = self.conn.execute(query).mappings()

		if user:
			yield from self.__generate_station_and_rules_from_rows__(
				records,
				user.id,
				scopes
			)
		else:
			for row in records:
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
			ab_name.label("album"),
			ar_name.label("artist"),
		)
		query = self.__attach_catalogue_joins(baseQuery, stationId)\
			.offset(offset)\
			.limit(limit)
		records = self.conn.execute(query).mappings()
		for row in records:
			rules = []
			if pathRuleTree:
				rules = list(pathRuleTree.valuesFlat(
					normalize_opening_slash(cast(str, row[sg_path])))
				)
			yield SongListDisplayItem(
				id=cast(int,row[sg_pk]),
				path=cast(str, row[sg_path]),
				name=cast(str, row[sg_name]),
				album=cast(str, row["album"]),
				artist=cast(str, row["artist"]),
				queuedtimestamp=0,
				rules=rules
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
		queryAny = select(st_pk, st_name).select_from(stations_tbl)\
				.where(st_name == str(stationName))\
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

	def __create_initial_owner_rules__(self, stationId: int, userId: int):
		rules = [{
				"userfk": userId,
				"stationfk": stationId,
				"role": UserRoleDef.STATION_FLIP.value,
				"span":3600,
				"count":3,
				"priority": None,
				"creationtimestamp": self.get_datetime().timestamp()
			},
			{
				"userfk": userId,
				"stationfk": stationId,
				"role": UserRoleDef.STATION_REQUEST.value,
				"span":300,
				"count":1,
				"priority": None,
				"creationtimestamp": self.get_datetime().timestamp()
			},
			{
				"userfk": userId,
				"stationfk": stationId,
				"role": UserRoleDef.STATION_SKIP.value,
				"span":900,
				"count":1,
				"priority": None,
				"creationtimestamp": self.get_datetime().timestamp()
			}
		]
		stmt = insert(station_user_permissions_tbl)
		self.conn.execute(stmt, rules) #pyright: ignore [reportUnknownMemberType]

	def save_station(
		self,
		station: StationCreationInfo,
		user: AccountInfo,
		stationId: Optional[int]=None,
	) -> Optional[StationInfo]:
		if not station:
			return next(self.get_stations(stationId), None)
		upsert = update if stationId else insert
		savedName = SavedNameString(station.name)
		savedDisplayName = SavedNameString(station.displayname)
		stmt = upsert(stations_tbl).values(
			name = str(savedName),
			displayname = str(savedDisplayName),
			lastmodifiedbyuserfk = user.id,
			lastmodifiedtimestamp = self.get_datetime().timestamp(),
			viewsecuritylevel = station.viewsecuritylevel,
			requestsecuritylevel = station.requestsecuritylevel
		)
		if stationId and isinstance(stmt, Update):
			stmt = stmt.where(st_pk == stationId)
		else:
			stmt = stmt.values(ownerfk = user.id)
		try:
			res = self.conn.execute(stmt)
			affectedId = stationId if stationId else res.lastrowid
			self.template_service.create_station_files(
				affectedId,
				str(savedName),
				str(savedDisplayName),
				user.username
			)
			if not stationId:
				self.__create_initial_owner_rules__(affectedId, user.id)
			self.conn.commit()
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{savedName} is already used.", "body->name"
				)]
			)

		affectedId: int = stationId if stationId else res.lastrowid
		return StationInfo(
			id=affectedId,
			name=str(savedName),
			displayname=str(savedDisplayName),
			owner=user,
			viewsecuritylevel=station.viewsecuritylevel,
			requestsecuritylevel=station.requestsecuritylevel
		)

	def get_station_users(
		self,
		station: StationInfo,
		userId: Optional[int]=None
	) -> Iterator[AccountInfo]:
		rulesQuery = build_rules_query(UserRoleDomain.Station).cte()
		query = select(
			u_pk,
			u_username,
			u_displayName,
			u_email,
			u_dirRoot,
			rulesQuery.c.rule_userfk,
			rulesQuery.c.rule_name,
			rulesQuery.c.rule_count,
			rulesQuery.c.rule_span,
			rulesQuery.c.rule_priority,
			rulesQuery.c.rule_domain
		).select_from(user_tbl).join(
			rulesQuery,
			or_(
				and_(
					(u_pk == station.owner.id) if station.owner else false(),
					rulesQuery.c.rule_userfk == 0
				),
				and_(
					rulesQuery.c.rule_userfk == u_pk,
					rulesQuery.c.rule_stationfk == station.id
				),
			),
			isouter=True
		).where(or_(u_disabled.is_(None), u_disabled == False))\
		.where(
			or_(
				coalesce(
					rulesQuery.c.rule_priority,
					RulePriorityLevel.SITE.value
				) > MinItemSecurityLevel.INVITED_USER.value,
				(u_pk == station.owner.id) if station.owner else false()
			)
		)
		if userId is not None:
			query = query.where(u_pk == userId)
		query = query.order_by(u_username)
		records = self.conn.execute(query).mappings()
		yield from generate_user_and_rules_from_rows(
			records,
			UserRoleDomain.Station,
			station.owner.id if station.owner else None
		)

	def add_user_rule_to_station(
		self,
		addedUserId: int,
		stationId: int,
		rule: ActionRule
	) -> StationActionRule:
		stmt = insert(station_user_permissions_tbl).values(
			userfk = addedUserId,
			stationfk = stationId,
			role = rule.name,
			span = rule.span,
			count = rule.count,
			priority = None,
			creationtimestamp = self.get_datetime().timestamp()
		)
		self.conn.execute(stmt)
		self.conn.commit()
		return StationActionRule(
			rule.name,
			rule.span,
			rule.count,
			RulePriorityLevel.STATION_PATH.value
		)

	def remove_user_rule_from_station(
		self,
		userId: int,
		stationId: int,
		ruleName: Optional[str]
	):
		delStmt = delete(station_user_permissions_tbl)\
			.where(stup_userFk == userId)\
			.where(stup_stationFk == stationId)
		if ruleName:
			delStmt = delStmt.where(stup_role == ruleName)
		self.conn.execute(delStmt) #pyright: ignore [reportUnknownMemberType]

	def get_station_song_counts(
		self,
		stationIds: Union[int, Iterable[int], None]=None,
		ownerId: Union[int, None]=None,
	) -> Iterator[Tuple[int, int]]:
		query = select(stsg_stationFk, func.count(stsg_songFk))

		if type(stationIds) == int:
			query = query.where(stsg_stationFk == stationIds)
		elif isinstance(stationIds, Iterable):
			query = query.where(stsg_stationFk.in_(stationIds))

		if type(ownerId) == int:
			query = query.join(stations_tbl, st_pk == stsg_stationFk)\
				.where(st_ownerFk == ownerId)
		records = self.conn.execute(query)
		for row in records:
			yield cast(int,row[0]), cast(int,row[1])

	def set_station_proc(self, stationId: int) -> None:
		pid = ProcessService.get_pid()
		stmt = update(stations_tbl)\
			.values(procid = pid) \
				.where(st_pk == stationId)
		self.conn.execute(stmt)


	def unset_station_procs(
		self,
		procIds: Optional[Iterable[int]]=None,
		stationIds: Union[int,Iterable[int], None]=None,
	) -> None:
		stmt = update(stations_tbl)\
			.values(procid = None)

		if isinstance(procIds, Iterable):
			stmt = stmt.where(st_procId.in_(procIds))
		elif type(stationIds) == int:
			stmt = stmt.where(st_pk == stationIds)
		elif isinstance(stationIds, Iterable):
			stmt = stmt.where(st_pk.in_(stationIds))
		else:
			raise ValueError("procIds, stationIds, or stationNames must be provided.")
		self.conn.execute(stmt)


	def __noop_startup__(self, stationName: str) -> None:
		#for normal operations, this is handled in the ices process

		pid = ProcessService.get_pid()
		stmt = update(stations_tbl)\
				.values(procid = pid) \
				.where(func.lower(st_name) == func.lower(stationName))
		self.conn.execute(stmt)

	def enable_stations(self,
		stations: Collection[StationInfo],
		owner: AccountInfo,
		includeAll: bool = False
	) -> Iterator[StationInfo]:
		stationsEnabled: Iterator[StationInfo] = iter([])
		if includeAll:
			canBeEnabled = {s[0] for s in  \
				self.get_station_song_counts(ownerId=owner.id) \
				if s[1] > 0
			}
			stationsEnabled = self.get_stations(
				stationKeys=canBeEnabled,
				ownerId=owner.id
			)
		else:
			canBeEnabled = {s[0] for s in  \
				self.get_station_song_counts(
					stationIds=(s.id for s in stations)
				) \
				if s[1] > 0
			}
			stationsEnabled = (s for s in stations if s.id in canBeEnabled)
		for station in stationsEnabled:
			if ProcessService.noop_mode():
				self.__noop_startup__(station.name)
			else:
				ProcessService.start_station_external_process(
					station.name,
					owner.username
				)
			yield station
		self.conn.commit()

	def disable_stations(
		self,
		stationIds: Iterable[int],
		ownerKey: Union[int, str, None],
		includeAll: bool = False
	) -> None:
		query = select(st_procId).where(st_procId.is_not(None))
		if includeAll:
			if type(ownerKey) == int:
				query = query.where(st_ownerFk == ownerKey)
			elif type(ownerKey) == str:
				query = query.join(user_tbl, u_pk == st_ownerFk)\
					.where(u_username == ownerKey)
		else:
			query = query.where(st_pk.in_(stationIds))

		rows = self.conn.execute(query)
		pids = [cast(int, row[st_procId]) for row in rows]
		for pid in pids:
			ProcessService.end_process(pid)
		self.unset_station_procs(pids)
		self.conn.commit()