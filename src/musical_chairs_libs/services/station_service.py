#pyright: reportMissingTypeStubs=false
import musical_chairs_libs.dtos_and_utilities.logging as logging
from typing import (
	Any,
	Iterator,
	Optional,
	cast,
	Iterable,
	Union,
	Collection,
	Tuple,
	Sequence,
	overload
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
	st_ownerFk, st_requestSecurityLevel, st_viewSecurityLevel, st_typeid,
	songs, sg_pk,
	sg_deletedTimstamp,
	albums, ab_name, ab_pk, ab_albumArtistFk, ab_year, ab_versionnote,
	artists, ar_name, ar_pk,
	stations_songs as stations_songs_tbl, stsg_songFk, stsg_stationFk,
	stations_albums as stations_albums_tbl, stab_albumFk, stab_stationFk,
	station_user_permissions as station_user_permissions_tbl,
	stup_stationFk,
	users as user_tbl, u_username, u_pk, u_displayName, 
	station_queue, q_stationFk,
	last_played, lp_stationFk
)
from musical_chairs_libs.dtos_and_utilities import (
	StationInfo,
	SongListDisplayItem,
	StationCreationInfo,
	SavedNameString,
	get_datetime,
	AccountInfo,
	ActionRule,
	UserRoleDef,
	AlreadyUsedError,
	UserRoleDomain,
	get_station_owner_rules,
	RulePriorityLevel,
	OwnerInfo,
	build_station_rules_query,
	row_to_action_rule,
	clean_search_term_for_like,
	AlbumListDisplayItem,
	Lost
)
from musical_chairs_libs.dtos_and_utilities.constants import StationTypes
from .path_rule_service import PathRuleService
from .template_service import TemplateService
from .song_info_service import SongInfoService
from .process_service import ProcessService


class StationService:

	def __init__(
		self,
		conn: Optional[Connection]=None,
		templateService: Optional[TemplateService]=None,
		songInfoService: Optional[SongInfoService]=None,
		pathRuleService: Optional[PathRuleService]=None
	):
		if not conn:
			raise RuntimeError("No connection provided")
		if not templateService:
			templateService = TemplateService()
		if not songInfoService:
			songInfoService = SongInfoService(conn)
		if not pathRuleService:
			pathRuleService = PathRuleService(conn)
		self.conn = conn
		self.template_service = templateService
		self.song_info_service = songInfoService
		self.path_rule_service = pathRuleService
		self.get_datetime = get_datetime

	def get_station_id(
			self,
			stationName: str,
			ownerKey: Union[int, str]
		) -> Optional[int]:
		query = select(st_pk) \
			.select_from(stations_tbl) \
			.where(func.lower(st_name) == func.lower(stationName))
		if type(ownerKey) == int:
			query = query.where(st_ownerFk == ownerKey)
		elif type(ownerKey) == str:
			query = query.join(user_tbl, st_ownerFk == u_pk)\
				.where(u_username == ownerKey)
		row = self.conn.execute(query).fetchone()
		pk: Optional[int] = cast(int,row[0]) if row else None
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
				Integer,
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
				Integer,
				Integer
			]
		]:
		rulesQuery = build_station_rules_query(userId)
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
					RulePriorityLevel.INVITED_USER.value
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
						RulePriorityLevel.RULED_USER.value
					) < select(topSiteRule.c.max).scalar_subquery() #pyright: ignore [reportUnknownMemberType]
				),
				coalesce(
					st_viewSecurityLevel,
					RulePriorityLevel.ANY_USER.value
				) < RulePriorityLevel.USER.value,
				and_(
					st_ownerFk == userId,
					coalesce(
						st_viewSecurityLevel,
						RulePriorityLevel.OWENER_USER.value
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
				id=row[st_ownerFk],
				username=row[u_username],
				displayname=row[u_displayName]
			),
			requestsecuritylevel=row["requestsecuritylevel"],
			viewsecuritylevel=row[st_viewSecurityLevel] \
				or RulePriorityLevel.PUBLIC.value,
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
		stationKeys: Union[int, str, Iterable[int], None]=None,
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
			coalesce[Integer](
				st_requestSecurityLevel,
				case(
					(st_viewSecurityLevel == RulePriorityLevel.PUBLIC.value, None),
					else_=st_viewSecurityLevel
				),
				RulePriorityLevel.ANY_USER.value
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
			lStationKey = stationKeys.replace("_","\\_").replace("%","\\%")
			query = query\
				.where(st_name.like(f"%{lStationKey}%"))
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



	def get_station_song_catalogue(
		self,
		stationId: int,
		page: int = 0,
		song: str = "",
		album: str = "",
		artist: str = "",
		limit: Optional[int]=None,
		user: Optional[AccountInfo]=None
	) -> Tuple[list[SongListDisplayItem], int]:
		data, count = self.song_info_service.get_song_catalogue(
			stationId,
			page,
			song,
			album,
			artist,
			limit,
			user
		)
		return (data,count)


	def get_album_catalogue(
		self,
		stationId: int,
		page: int = 0,
		album: str = "",
		artist: str = "",
		limit: Optional[int]=None,
		user: Optional[AccountInfo]=None
	) -> Tuple[list[AlbumListDisplayItem], int]:
		offset = page * limit if limit else 0
		lalbum = clean_search_term_for_like(album)
		lartist = clean_search_term_for_like(artist)

		query = select(
			ab_pk.label("id"),
			ab_name.label("name"),
			ar_name.label("albumartist"),
			ab_year.label("year"),
			ab_versionnote.label("versionnote")
		)\
			.select_from(stations_tbl) \
			.join(stations_songs_tbl, st_pk == stab_stationFk) \
			.join(albums, stab_albumFk == ab_pk) \
			.join(artists, ab_albumArtistFk == ar_pk, isouter=True) \
			.where(st_pk == stationId)
		
		if lalbum:
			query = query.where(ab_name.like(f"%{lalbum}%"))

		if lartist:
			query = query.where(ar_name.like(f"%{lartist}%"))

		limitedQuery = query\
			.offset(offset)\
			.limit(limit)

		records = self.conn.execute(limitedQuery).mappings()

		result = [AlbumListDisplayItem(**r) for r in records]
		countQuery = select(func.count(1))\
			.select_from(cast(Any, query))
		count = self.conn.execute(countQuery).scalar() or 0
		return result, count

	def can_song_be_queued_to_station(self, songId: int, stationId: int) -> bool:
		query = select(func.count(1)).select_from(stations_songs_tbl)\
			.join(songs, stsg_songFk == sg_pk)\
			.join(stations_tbl, st_pk == stsg_stationFk)\
			.where(st_typeid == StationTypes.DEFAULT.value)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(stsg_songFk == songId)\
			.where(stsg_stationFk == stationId)
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False
	
	def can_album_be_queued_to_station(
		self,
		albumId: int,
		stationId: int
	) -> bool:
		query = select(func.count(1)).select_from(stations_albums_tbl)\
			.join(stations_tbl, stab_stationFk == st_pk)\
			.where(st_typeid == StationTypes.ALBUM.value)\
			.where(stab_albumFk == albumId)\
			.where(stab_stationFk == stationId)
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False

	def __is_stationName_used__(
		self,
		id: Optional[int],
		stationName: SavedNameString,
		userId: int,
	) -> bool:
		queryAny = select(func.count(1)).select_from(stations_tbl)\
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
		return self.__is_stationName_used__(id, cleanedStationName, userId)

	def __create_initial_owner_rules__(
		self,
		stationId: int,
		userId: int
	) -> list[ActionRule]:
		rules = [
			ActionRule(
				domain=UserRoleDomain.Station.value,
				name=UserRoleDef.STATION_FLIP.value,
				span=3600,
				count=3,
				priority=None
			),
			ActionRule(
				domain=UserRoleDomain.Station.value,
				name=UserRoleDef.STATION_REQUEST.value,
				span=300,
				count=1,
				priority=None
			),
			ActionRule(
				domain=UserRoleDomain.Station.value,
				name=UserRoleDef.STATION_SKIP.value,
				span=900,
				count=1,
				priority=None
			)
		]
		params: list[dict[str, Any]] = [
			{
				**rule.model_dump(exclude={"name", "domain"}),
				"role": rule.name,
				"userfk": userId,
				"stationfk": stationId,
				"creationtimestamp": self.get_datetime().timestamp()
			} for rule in rules
		]
		stmt = insert(station_user_permissions_tbl)
		self.conn.execute(stmt, params) #pyright: ignore [reportUnknownMemberType]
		return rules

	@overload
	def save_station(
		self,
		station: StationCreationInfo,
		user: AccountInfo,
		stationId: int,
	) -> Optional[StationInfo]:
		...

	@overload
	def save_station(
		self,
		station: StationCreationInfo,
		user: AccountInfo,
	) -> StationInfo:
		...

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
			rules = []
			if not stationId:
				rules = list({
						*self.__create_initial_owner_rules__(affectedId, user.id),
						*get_station_owner_rules()
					})
			self.conn.commit()
		except IntegrityError:
			raise AlreadyUsedError.build_error(
				f"{savedName} is already used.", "body->name"
			)

		affectedId: int = stationId if stationId else res.lastrowid
		return StationInfo(
			id=affectedId,
			name=str(savedName),
			displayname=str(savedDisplayName),
			owner=user,
			viewsecuritylevel=station.viewsecuritylevel,
			requestsecuritylevel=station.requestsecuritylevel,
			rules=rules
		)


	def get_station_song_counts(
		self,
		stationIds: Union[int, Iterable[int], None]=None,
		ownerId: Union[int, None]=None,
	) -> Iterator[Tuple[int, int]]:
		query = select(stsg_stationFk, func.count(stsg_songFk))\
			.join(songs, stsg_songFk == sg_pk)\
			.where(sg_deletedTimstamp.is_(None))

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
		self.conn.commit()

	def unset_station_procs(
		self,
		procIds: Optional[Iterable[int]]=None,
		stationIds: Union[int,Sequence[int], None, Lost]=Lost(),
	) -> None:
		stmt = update(stations_tbl)\
			.values(procid = None)

		if isinstance(procIds, Iterable):
			stmt = stmt.where(st_procId.in_(procIds))
		elif type(stationIds) == int:
			stmt = stmt.where(st_pk == stationIds)
		elif isinstance(stationIds, Iterable):
			stmt = stmt.where(st_pk.in_(stationIds))
		elif stationIds is Lost():
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
		try:
			for station in stationsEnabled:
				try:
					if ProcessService.noop_mode():
						self.__noop_startup__(station.name)
					else:
						if not self.conn.engine.url.database:
							raise RuntimeError("db Name is missing")
						
						if not self.template_service.does_station_config_exist(
							station.name,
							owner.username
						):
							self.template_service.create_station_files(
								station.id,
								station.name,
								station.displayname,
								owner.username
							)

						ProcessService.start_song_queue_process(
							self.conn.engine.url.database,
							station.name,
							owner.username
						)
					yield station
				except RuntimeError:
					self.unset_station_procs(stationIds=station.id)
					raise
		finally:
			self.conn.commit()

	def disable_stations(
		self,
		stationIds: Optional[Iterable[int]],
		ownerKey: Union[int, str, None]=None
	) -> None:
		#explicitly checking that stationIds is not null rather
		#simply if stationIds because we want want [] to trigger the all case
		stationIds = list(stationIds) if stationIds is not None else None
		logging.radioLogger.debug(
			f"disable {stationIds if stationIds is not None else 'All'}"
		)
		query = select(st_procId).where(st_procId.is_not(None))
		if ownerKey:
			if type(ownerKey) == int:
				query = query.where(st_ownerFk == ownerKey)
			elif type(ownerKey) == str:
				query = query.join(user_tbl, u_pk == st_ownerFk)\
					.where(u_username == ownerKey)
		else:
			if stationIds is not None:
				query = query.where(st_pk.in_(stationIds))
			

		rows = self.conn.execute(query)
		pids = [cast(int, row[0]) for row in rows]
		for pid in pids:
			logging.radioLogger.debug(f"send signal to {pid}")
			ProcessService.end_process(pid)
		self.unset_station_procs(stationIds=stationIds)
		self.conn.commit()

	def delete_station(self, stationId: int, clearStation: bool=False) -> int:
		if not stationId:
			return 0
		delCount = 0
		if clearStation:
			delCount = self.clear_station(stationId)
		delStmt = delete(station_user_permissions_tbl)\
			.where(stup_stationFk == stationId)
		delCount += self.conn.execute(delStmt).rowcount
		delStmt = delete(station_queue).where(q_stationFk == stationId)
		delCount += self.conn.execute(delStmt).rowcount
		delStmt = delete(last_played).where(lp_stationFk == stationId)
		delCount += self.conn.execute(delStmt).rowcount
		delStmt = delete(stations_tbl).where(st_pk == stationId)
		delCount += self.conn.execute(delStmt).rowcount
		self.conn.commit()
		return delCount

	def clear_station(self, stationId: int) -> int:
		if not stationId:
			return 0
		delCount = 0
		delStmt = delete(stations_songs_tbl).where(stsg_stationFk == stationId)
		delCount += self.conn.execute(delStmt).rowcount
		self.conn.commit()
		return delCount
		
	def copy_station(
		self, 
		stationId: int, 
		copy: StationCreationInfo,
		user: AccountInfo,
	) -> Optional[StationInfo]:
		songIdsQuery = select(stsg_songFk).where(stsg_stationFk == stationId)
		rows = self.conn.execute(songIdsQuery)
		songIds = [cast(int,row[0]) for row in rows]
		if not any(songIds):
			return None
		created = self.save_station(copy, user)
		params = [{
			"stationfk": created.id,
			"songfk": s
		} for s in songIds]
		insertStmt = insert(stations_songs_tbl)
		self.conn.execute(insertStmt, params)
		self.conn.commit()
		return created

