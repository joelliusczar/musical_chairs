#pyright: reportMissingTypeStubs=false

from typing import (
	Any,
	Iterator,
	Optional,
	cast,
	Iterable,
	Union,
	Collection,
	Tuple,
	overload
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Connection
from sqlalchemy.sql.expression import (
	case,
	cast as dbCast,
	CTE,
	true,
	false
)
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.functions import coalesce
from sqlalchemy import (
	Label,
	Float,
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
)
from musical_chairs_libs.tables import (
	stations as stations_tbl, st_pk, st_name, st_displayName, st_procId,
	st_ownerFk, st_requestSecurityLevel, st_viewSecurityLevel, st_typeid, 
	st_bitrate, st_playnum,
	songs, sg_pk,
	sg_deletedTimstamp,
	stations_songs as stations_songs_tbl, stsg_songFk, stsg_stationFk,
	users as user_tbl, u_username, u_pk, u_displayName, 
	stations_albums as stations_albums_tbl, stab_albumFk, stab_stationFk,
	stations_playlists as stations_playlists_tbl, stpl_playlistFk,stpl_stationFk,
	userRoles as user_roles_tbl, ur_keypath, ur_sphere
)
from musical_chairs_libs.dtos_and_utilities import (
	ActionRule,
	build_base_rules_query,
	generate_owned_and_rules_from_rows,
	get_station_owner_rules,
	StationInfo,
	StationCreationInfo,
	SearchNameString,
	SavedNameString,
	NotFoundError,
	get_datetime,
	UserRoleDef,
	AlreadyUsedError,
	RulePriorityLevel,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	UserRoleSphere
)
from musical_chairs_libs.dtos_and_utilities.constants import StationTypes
from musical_chairs_libs.protocols import UserProvider
from .path_rule_service import PathRuleService
from .template_service import TemplateService
import musical_chairs_libs.dtos_and_utilities as dtos
import sqlalchemy as sa
import musical_chairs_libs.tables as tbl


class StationService:

	def __init__(
		self,
		conn: Connection,
		currentUserProvider: UserProvider,
		pathRuleService: PathRuleService,
		templateService: Optional[TemplateService]=None,
	):
		if not conn:
			raise RuntimeError("No connection provided")
		if not templateService:
			templateService = TemplateService()
		self.conn = conn
		self.template_service = templateService
		self.path_rule_service = pathRuleService
		self.get_datetime = get_datetime
		self.current_user_provider = currentUserProvider


	def base_select_columns(self) -> list[Label[Any]]:
		return [
			tbl.st_pk.label("id"),
			tbl.st_name.label("name"),
			tbl.st_displayName.label("displayname"),
			tbl.st_procId.label("procid"),
			tbl.st_ownerFk.label("owner>id"),
			tbl.u_username.label("owner>username"),
			tbl.u_displayName.label("owner>displayname"),
			tbl.u_publictoken.label("owner>publictoken"),
			coalesce[Integer](
				tbl.st_requestSecurityLevel,
				case(
					(tbl.st_viewSecurityLevel == RulePriorityLevel.PUBLIC.value, None),
					else_=tbl.st_viewSecurityLevel
				),
				RulePriorityLevel.ANY_USER.value
			).label("requestsecuritylevel"), #pyright: ignore [reportUnknownMemberType]
			tbl.st_viewSecurityLevel.label("viewsecuritylevel"),
			tbl.st_typeid.label("typeid"),
			tbl.st_bitrate.label("bitrate"),
			tbl.st_playnum.label("playnum")
		]


	def station_base_query(
		self,
		ownerKey: int | str | None =None,
		stationKeys: int | str | Iterable[int] | None=None,
		exactStrMatch: bool=False
	):
		query = stations_tbl.outerjoin(user_tbl, st_ownerFk == u_pk).select()
		if type(ownerKey) is int:
			query = query.where(st_ownerFk == ownerKey)
		elif type(ownerKey) == str:
			query = query.where(u_username == ownerKey)
		if type(stationKeys) == int:
			query = query.where(st_pk == stationKeys)
		elif isinstance(stationKeys, Iterable) and not isinstance(stationKeys, str):
			query = query.where(st_pk.in_(stationKeys))
		elif type(stationKeys) is str and not ownerKey:
			raise ValueError("user must be provided when using station name")
		elif type(stationKeys) is str:
			if exactStrMatch:
				query = query.where(
					st_name == SearchNameString.format_name_for_search(stationKeys)
				)
			else:
				lStationKey = stationKeys.replace("_","\\_").replace("%","\\%")
				query = query\
					.where(st_name.like(f"%{lStationKey}%", escape="\\"))
		
		return query


	def __build_user_rule_filters__(
		self,
		rulesSubquery: CTE,
		scopes: Optional[Collection[str]]=None,
	):
		userId = self.current_user_provider.optional_user_id()
		canViewQuery= select(
			rulesSubquery.c["rule>keypath"], #pyright: ignore [reportUnknownMemberType]
			rulesSubquery.c["rule>priority"], #pyright: ignore [reportUnknownMemberType]
			rulesSubquery.c["rule>sphere"] #pyright: ignore [reportUnknownMemberType]
		).where(
			rulesSubquery.c["rule>name"].in_(scopes) if scopes else true(), #pyright: ignore [reportUnknownMemberType]
		).cte(name="canviewquery")

		topSiteRule = select(
			coalesce[int](
				func.max(canViewQuery.c["rule>priority"]), #pyright: ignore [reportUnknownMemberType]
				RulePriorityLevel.NONE.value
			).label("max")
		).where(
			canViewQuery.c["rule>sphere"] == UserRoleSphere.Site.value
		).cte("topsiterule")

		ownerScopeSet = set(get_station_owner_rules(scopes))

		filters = [
			or_(
				coalesce(
					st_viewSecurityLevel,
					RulePriorityLevel.REQUIRES_INVITE.value
				) < select(coalesce[int](
							func.max(canViewQuery.c["rule>priority"]), #pyright: ignore [reportUnknownMemberType]
							RulePriorityLevel.NONE.value
						)).where(st_pk == canViewQuery.c["rule>keypath"]).scalar_subquery(), #pyright: ignore [reportUnknownMemberType]
				and_(
					dbLiteral(UserRoleSphere.Site.value)
						.in_( #pyright: ignore [reportUnknownMemberType]
							select(canViewQuery.c["rule>sphere"]) #pyright: ignore [reportUnknownMemberType]
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
			or_(
				rulesSubquery.c["rule>name"].in_(scopes) if scopes else true(), #pyright: ignore [reportUnknownMemberType]
				(st_ownerFk == userId) if scopes and ownerScopeSet else false()
			)
		]

		return filters


	def get_stations_unsecured(
		self,
		stationKeys: Union[int, str, Iterable[int], None]=None,
		ownerId: Union[int, None]=None,
	) -> Iterator[StationInfo]:
		query = self.station_base_query(stationKeys=stationKeys)\
			.with_only_columns(
				*self.base_select_columns()
			)

		with dtos.open_transaction(self.conn):
			records = self.conn.execute(query).mappings().fetchall()
			for row in records:
				yield StationInfo.row_to_station(row)


	def get_secured_station_query(
		self,
		stationKeys: Union[int, str, Iterable[int], None]=None,
		ownerKey: int | str | None=None,
		scopes: Optional[Collection[str]]=None,
		exactStrMatch: bool=False
	):
		query = self.station_base_query(
			ownerKey=ownerKey,
			stationKeys=stationKeys,
			exactStrMatch=exactStrMatch
		)
		user = self.current_user_provider.current_user()
		rulesSubquery = build_base_rules_query(
			UserRoleSphere.Station,
			user.id
		).cte(name="rulesQuery")
		filters = self.__build_user_rule_filters__(rulesSubquery, scopes)
		query = query.join(rulesSubquery, or_(
			rulesSubquery.c["rule>keypath"] == dbCast(st_pk, String), #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
			rulesSubquery.c["rule>keypath"] == "-1", #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
			rulesSubquery.c["rule>keypath"].is_(None) #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
		))\
		.where(*filters)\
		.order_by(st_pk)\
			.with_only_columns(
				st_pk.label("id"),
				st_name.label("name"),
				st_displayName.label("displayname"),
				st_procId.label("procid"),
				st_ownerFk.label("owner>id"),
				u_username.label("owner>username"),
				u_displayName.label("owner>displayname"),
				tbl.u_publictoken.label("owner>publictoken"),
				coalesce[Integer](
					st_requestSecurityLevel,
					case(
						(st_viewSecurityLevel == RulePriorityLevel.PUBLIC.value, None),
						else_=st_viewSecurityLevel
					),
					RulePriorityLevel.ANY_USER.value
				).label("requestsecuritylevel"), #pyright: ignore [reportUnknownMemberType]
				st_viewSecurityLevel.label("viewsecuritylevel"),
				st_typeid.label("typeid"),
				st_bitrate.label("bitrate"),
				st_playnum.label("playnum"),
				cast(Column[String], rulesSubquery.c["rule>name"]).label("rule>name"),
				cast(
					Column[Float[float]],
					rulesSubquery.c["rule>quota"]
				).label("rule>quota"),
				cast(
					Column[Float[float]],
					rulesSubquery.c["rule>span"]
				).label("rule>span"),
				cast(
					Column[Integer], rulesSubquery.c["rule>priority"]
				).label("rule>priority"),
				cast(
					Column[String], rulesSubquery.c["rule>sphere"]
				).label("rule>sphere")
			)
		
		return query


	def get_stations(
		self,
		stationKeys: int | str | Iterable[int]| None=None,
		ownerKey: int | str | None=None,
		scopes: Collection[str] | None=None,
		exactStrMatch: bool=False
	) -> list[StationInfo]:
		
		userId = self.current_user_provider.optional_user_id()
		if userId:
			query = self.get_secured_station_query(
				ownerKey=ownerKey,
				stationKeys=stationKeys,
				scopes=scopes,
				exactStrMatch=exactStrMatch,
			)

			with dtos.open_transaction(self.conn):
				records = self.conn.execute(query).mappings().fetchall()

				return [s for s in generate_owned_and_rules_from_rows(
					records,
					StationInfo.row_to_station,
					get_station_owner_rules,
					scopes,
					userId
				)]
		else:
			if scopes:
				return []
			query = self.station_base_query(
				ownerKey=ownerKey,
				stationKeys=stationKeys,
				exactStrMatch=exactStrMatch,
			)\
			.where(
				coalesce(st_viewSecurityLevel, 0) == 0
			)\
			.with_only_columns(*self.base_select_columns())

			with dtos.open_transaction(self.conn):
				records = self.conn.execute(query).mappings().fetchall()

				return [
					s for s in (StationInfo.row_to_station(row) for row in records)
				]


	def __is_stationName_used__(
		self,
		id: Optional[int],
		stationName: SavedNameString,
	) -> bool:
		userId = self.current_user_provider.current_user().id
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
	) -> bool:
		cleanedStationName = SavedNameString(stationName)
		if not cleanedStationName:
			return True
		with dtos.open_transaction(self.conn):
			return self.__is_stationName_used__(id, cleanedStationName)


	def __create_initial_owner_rules__(
		self,
		stationId: int,
	) -> list[ActionRule]:
		rules = [
			ActionRule(
				sphere=UserRoleSphere.Station.value,
				name=UserRoleDef.STATION_FLIP.value,
				span=3600,
				quota=3,
				priority=None
			),
			ActionRule(
				sphere=UserRoleSphere.Station.value,
				name=UserRoleDef.STATION_REQUEST.value,
				span=300,
				quota=1,
				priority=None
			),
			ActionRule(
				sphere=UserRoleSphere.Station.value,
				name=UserRoleDef.STATION_SKIP.value,
				span=900,
				quota=1,
				priority=None
			)
		]
		userId = self.current_user_provider.current_user().id
		params: list[dict[str, Any]] = [
			{
				**rule.model_dump(),
				"role": rule.name,
				"userfk": userId,
				"keypath": stationId,
				"creationtimestamp": self.get_datetime().timestamp()
			} for rule in rules
		]
		stmt = insert(user_roles_tbl)
		self.conn.execute(stmt, params) #pyright: ignore [reportUnknownMemberType]
		return rules


	def __build_station_values__(
		self,
		station: StationCreationInfo
	) -> dict[Any, Any]:
		user = self.current_user_provider.current_user(optional=True)
		savedName = SavedNameString(station.name)
		savedDisplayName = SavedNameString(station.displayname)

		obj: dict[Any, Any] = {
			"name": str(savedName),
			"displayname": str(savedDisplayName),
			"lastmodifiedtimestamp": self.get_datetime().timestamp(),
			"viewsecuritylevel": station.viewsecuritylevel,
			"requestsecuritylevel": station.requestsecuritylevel,
			"typeid": station.typeid,
			"bitratekps": station.bitratekps,
			"playnum": station.playnum
		}

		if user:
			obj["lastmodifiedbyuserfk"] = user.id

		return obj
		

	def update_station(
		self,
		station: StationCreationInfo,
		stationId: int,
	) -> int:
		stmt = update(stations_tbl).values(
			**self.__build_station_values__(station)
		).where(st_pk == stationId)
		self.conn.execute(stmt)

		return stationId


	def add_station(
		self,
		station: StationCreationInfo
	) -> int:
		user = self.current_user_provider.current_user()
		savedName = SavedNameString(station.name)
		savedDisplayName = SavedNameString(station.displayname)

		stmt = insert(stations_tbl).values(
			**self.__build_station_values__(station)
		)\
		.values(ownerfk = user.id)
		
		try:
			res = self.conn.execute(stmt)
			affectedId = res.lastrowid
			self.template_service.create_station_files(
				affectedId,
				str(savedName),
				str(savedDisplayName),
				user.username,
				station.bitratekps or 128
			)
			self.__create_initial_owner_rules__(affectedId)
		except IntegrityError:
			raise AlreadyUsedError.build_error(
				f"{savedName} is already used.", "body->name"
			)
		return affectedId

	@overload
	def save_station(
		self,
		station: StationCreationInfo,
		stationId: int,
	) -> StationInfo:
		...

	@overload
	def save_station(
		self,
		station: StationCreationInfo,
		stationId: None = None,
	) -> StationInfo:
		...


	def save_station(
		self,
		station: StationCreationInfo,
		stationId: Optional[int]=None
	) -> StationInfo:
		with self.conn.begin() as transaction:
			if not station:
				try:
					return next(self.get_stations(stationId), None)
				except StopIteration:
					raise NotFoundError(f"{stationId} not found")

			stationId = self.update_station(station, stationId)\
				if stationId else self.add_station(station)
			transaction.commit()
		return next(iter(self.get_stations(stationId)))


	def get_station_song_counts(
		self,
		stationIds: Union[int, Iterable[int], None]=None,
		ownerId: Union[int, None]=None,
	) -> list[Tuple[int, int]]:
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
		with dtos.open_transaction(self.conn):
			records = self.conn.execute(query).fetchall()
			return [(cast(int,row[0]), cast(int,row[1])) for row in records]


	def delete_station(self, stationId: int) -> int:
		if not stationId:
			return 0
		delCount = 0
		with self.conn.begin() as transaction:
			delStmt = delete(user_roles_tbl)\
				.where(ur_sphere == UserRoleSphere.Station.value)\
				.where(ur_keypath == stationId)
			delStmt = delete(stations_tbl).where(st_pk == stationId)
			delCount = self.conn.execute(delStmt).rowcount
			transaction.commit()
			return delCount



	def copy_station(
		self, 
		stationId: int, 
		copy: StationCreationInfo
	) -> StationInfo:
		copy.playnum = 1
		with self.conn.begin() as transation:
			createdId = self.add_station(copy)
			if copy.typeid == StationTypes.SONGS_ONLY.value:
				query = select(stsg_songFk).where(stsg_stationFk == stationId)
				rows = self.conn.execute(query).fetchall()
				itemIds = [cast(int,row[0]) for row in rows]
				if any(itemIds):
					params = [{
						"stationfk": createdId,
						"songfk": s,
					} for s in itemIds]
					insertStmt = insert(stations_songs_tbl)
					self.conn.execute(insertStmt, params)
			if copy.typeid == StationTypes.ALBUMS_AND_PLAYLISTS.value:
				query = select(stab_albumFk).where(stab_stationFk == stationId)
				rows = self.conn.execute(query).fetchall()
				itemIds = [cast(int,row[0]) for row in rows]
				if any(itemIds):
					params = [{
						"stationfk": createdId,
						"albumfk": s
					} for s in itemIds]
					insertStmt = insert(stations_albums_tbl)
					self.conn.execute(insertStmt, params)

				query = select(stpl_playlistFk).where(stpl_stationFk == stationId)
				rows = self.conn.execute(query).fetchall()
				itemIds = [cast(int,row[0]) for row in rows]
				if any(itemIds):
					params = [{
						"stationfk": createdId,
						"playlistfk": s
					} for s in itemIds]
					insertStmt = insert(stations_playlists_tbl)
					self.conn.execute(insertStmt, params)

			transation.commit()
			return next(iter(self.get_stations(createdId)))
		
	
	def copy_station_as_songs(
		self, 
		stationId: int, 
		copy: StationCreationInfo
	) -> StationInfo:
		copy.playnum = 1
		oldTypeId = copy.typeid
		copy.typeid = StationTypes.SONGS_ONLY.value
		with self.conn.begin() as transation:
			createdId = self.add_station(copy)
			if oldTypeId == StationTypes.SONGS_ONLY.value:
				query = select(stsg_songFk).where(stsg_stationFk == stationId)
				rows = self.conn.execute(query).fetchall()
				itemIds = [cast(int,row[0]) for row in rows]
				if any(itemIds):
					params = [{
						"stationfk": createdId,
						"songfk": s,
					} for s in itemIds]
					insertStmt = insert(stations_songs_tbl)
					self.conn.execute(insertStmt, params)
			if oldTypeId == StationTypes.ALBUMS_AND_PLAYLISTS.value:
				query = select(sa.distinct(tbl.sg_pk))\
					.join(tbl.songs, tbl.sg_albumFk == tbl.stab_albumFk)\
					.where(stab_stationFk == stationId)
				rows = self.conn.execute(query).fetchall()
				if any(rows):
					params: list[dict[str, Any]] = [{
						"stationfk": createdId,
						"songfk": r[0]
					} for r in rows]
					insertStmt = insert(tbl.stations_songs)
					self.conn.execute(insertStmt, params)

				query = select(sa.distinct(tbl.plsg_songFk))\
				.join(tbl.playlists_songs, tbl.stpl_playlistFk == tbl.plsg_playlistFk)\
				.where(tbl.stpl_stationFk == stationId)
				rows = self.conn.execute(query).fetchall()
				if any(rows):
					params = [{
						"stationfk": createdId,
						"playlistfk": r[0]
					} for r in rows]
					insertStmt = insert(tbl.stations_songs)
					self.conn.execute(insertStmt, params)
				
				transation.commit()
		return next(iter(self.get_stations(createdId)))
