import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.tables as tbl
from typing import (
	Any,
	Optional,
	Union,
	cast,
	Iterable,
	Tuple,
	Collection
)
from musical_chairs_libs.dtos_and_utilities import (
	build_base_rules_query,
	generate_owned_and_rules_from_rows,
	get_playlist_owner_roles,
	SavedNameString,
	get_datetime,
	PlaylistInfo,
	PlaylistCreationInfo,
	AlreadyUsedError,
	SongsPlaylistInfo,
	SongListDisplayItem,
	DictDotMap,
	OwnerType,
	normalize_opening_slash,
	RulePriorityLevel,
	SimpleQueryParameters,
	StationPlaylistTuple,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	UserRoleSphere
)
from .current_user_provider import CurrentUserProvider
from .path_rule_service import PathRuleService
from .stations_playlists_service import StationsPlaylistsService
from sqlalchemy import (
	select,
	insert,
	update,
	Integer,
	func,
	Label,
	Float,
	delete,
	literal as dbLiteral,
	String,
	and_,
	or_,
	true,
	false,
)
from sqlalchemy.sql.expression import (
	CTE,
	cast as dbCast,
)
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.schema import Column
from musical_chairs_libs.tables import (
	playlists as playlists_tbl, pl_displayname, pl_viewSecurityLevel,
	pl_name, pl_pk, pl_ownerFk,
	ar_name,
	users as user_tbl, u_pk, u_username, u_displayName, 
	sg_pk, sg_name, sg_track, sg_path, sg_internalpath,
	sg_deletedTimstamp,
	playlists_songs as playlists_songs_tbl, plsg_songFk, plsg_playlistFk, 
	song_artist as song_artist_tbl, sgar_songFk, sgar_isPrimaryArtist,
)


class PlaylistService:

	def __init__(
		self,
		conn: Connection,
		currentUserProvider: CurrentUserProvider,
		stationsPlaylistsService: StationsPlaylistsService,
		pathRuleService: PathRuleService,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		if not stationsPlaylistsService:
			stationsPlaylistsService = StationsPlaylistsService(conn)
		self.conn = conn
		self.get_datetime = get_datetime
		self.path_rule_service = pathRuleService
		self.stations_playlists_service = stationsPlaylistsService
		self.current_user_provider = currentUserProvider

	def base_select_columns(self) -> list[Label[Any]]:
		return [
			pl_pk.label("id"),
			pl_name.label("name"),
			pl_displayname.label("displayname"),
			pl_ownerFk.label("owner>id"),
			u_username.label("owner>username"),
			u_displayName.label("owner>displayname"),
			tbl.u_publictoken.label("owner>publictoken"),
			pl_viewSecurityLevel.label("viewsecuritylevel"),
		]

	def playlist_base_query(
		self,
		ownerId: Optional[int]=None,
		playlistKeys: Union[int, str, Iterable[int], None]=None,
	):
		query = playlists_tbl.outerjoin(user_tbl, pl_ownerFk == u_pk).select()
		if type(ownerId) is int:
			query = query.where(pl_ownerFk == ownerId)
		if type(playlistKeys) == int:
			query = query.where(pl_pk == playlistKeys)
		elif isinstance(playlistKeys, Iterable) and not isinstance(playlistKeys, str):
			query = query.where(pl_pk.in_(playlistKeys))
		elif type(playlistKeys) is str and not ownerId:
			raise ValueError("user must be provided when using station name")
		elif type(playlistKeys) is str:
			lPlaylistKey = playlistKeys.replace("_","\\_").replace("%","\\%")
			query = query\
				.where(pl_name.like(f"%{lPlaylistKey}%"))
		
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

		ownerScopeSet = set(get_playlist_owner_roles(scopes))

		filters = [
			or_(
				coalesce(
					pl_viewSecurityLevel,
					RulePriorityLevel.REQUIRES_INVITE.value
				) < select(coalesce[int](
							func.max(canViewQuery.c["rule>priority"]), #pyright: ignore [reportUnknownMemberType]
							RulePriorityLevel.NONE.value
						)).where(pl_pk == canViewQuery.c["rule>keypath"]).scalar_subquery(), #pyright: ignore [reportUnknownMemberType]
				and_(
					dbLiteral(UserRoleSphere.Site.value)
						.in_( #pyright: ignore [reportUnknownMemberType]
							select(canViewQuery.c["rule>sphere"]) #pyright: ignore [reportUnknownMemberType]
						),
					coalesce(
						pl_viewSecurityLevel,
						RulePriorityLevel.RULED_USER.value
					) < select(topSiteRule.c.max).scalar_subquery() #pyright: ignore [reportUnknownMemberType]
				),
				coalesce(
					pl_viewSecurityLevel,
					RulePriorityLevel.ANY_USER.value
				) < RulePriorityLevel.USER.value,
				and_(
					pl_ownerFk == userId,
					coalesce(
						pl_viewSecurityLevel,
						RulePriorityLevel.OWENER_USER.value
					) < RulePriorityLevel.OWNER.value
				)
			),
			or_(
				rulesSubquery.c["rule>name"].in_(scopes) if scopes else true(), #pyright: ignore [reportUnknownMemberType]
				(pl_ownerFk == userId) if scopes and ownerScopeSet else false()
			)
		]

		return filters


	def get_secured_playlist_query(
		self,
		playlistKeys: Union[int, str, Iterable[int], None]=None,
		ownerId: Union[int, None]=None,
		scopes: Optional[Collection[str]]=None
	):
		query = self.playlist_base_query(ownerId=ownerId, playlistKeys=playlistKeys)
		user = self.current_user_provider.current_user()
		rulesSubquery = build_base_rules_query(
			UserRoleSphere.Playlist,
			user.id
		).cte(name="rulesQuery")
		filters = self.__build_user_rule_filters__(rulesSubquery, scopes)
		query = query.join(rulesSubquery, or_(
			rulesSubquery.c["rule>keypath"] == pl_pk, #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
			rulesSubquery.c["rule>keypath"] == -1, #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
			rulesSubquery.c["rule>keypath"].is_(None) #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
		))\
		.where(*filters)\
		.order_by(pl_pk)\
			.with_only_columns(
				pl_pk.label("id"),
				pl_name.label("name"),
				pl_displayname.label("displayname"),
				pl_ownerFk.label("owner>id"),
				u_username.label("owner>username"),
				u_displayName.label("owner>displayname"),
				tbl.u_publictoken.label("owner>publictoken"),
				pl_viewSecurityLevel.label("viewsecuritylevel"),
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


	def get_playlists(
		self,
		playlistKeys: int | str | Iterable[int] | None=None,
		ownerId: int | None=None,
		scopes: Collection[str] | None=None,
		page: int = 0,
		pageSize: int | None=None,
	) -> list[PlaylistInfo]:
		userId = self.current_user_provider.optional_user_id()
		with self.conn.begin():
			if userId:
				query = self.get_secured_playlist_query(
					ownerId=ownerId,
					playlistKeys=playlistKeys,
					scopes=scopes
				)

				records = self.conn.execute(query).mappings().fetchall()

				return [*generate_owned_and_rules_from_rows(
					records,
					PlaylistInfo.row_to_playlist,
					get_playlist_owner_roles,
					scopes,
					userId,
				)]
			else:
				if scopes:
					return []
				query = self.playlist_base_query(
					ownerId=ownerId,
					playlistKeys=playlistKeys,
				)\
				.where(
					coalesce(pl_viewSecurityLevel, 0) == 0
				)\
				.with_only_columns(*self.base_select_columns())

				records = self.conn.execute(query).mappings().fetchall()

				return [PlaylistInfo.row_to_playlist(row) for row in records]


	def get_playlist_owner(self, playlistId: int) -> dtos.User:
		query = select(pl_ownerFk, u_username, u_displayName, tbl.u_publictoken)\
			.select_from(playlists_tbl)\
			.join(user_tbl, u_pk == pl_ownerFk)\
			.where(pl_pk == playlistId)
		data = self.conn.execute(query).mappings().fetchone()
		if not data:
			return dtos.User(id=0,username="", displayname="", publictoken="")
		return dtos.User(
			id=data[pl_ownerFk],
			username=data[u_username],
			displayname=data[u_displayName],
			publictoken=data[tbl.u_publictoken]
		)


	def get_playlists_page(
		self,
		queryParams: SimpleQueryParameters,
		playlist: str | None = None,
		owner: Optional[OwnerType]=None
	) -> Tuple[list[PlaylistInfo], int]:
		result = list(self.get_playlists(
			page=queryParams.page,
			pageSize=queryParams.limit,
			playlistKeys=playlist,
			ownerId=owner.id if owner else None
		))
		countQuery = select(func.count(1))\
			.select_from(playlists_tbl)
		count = self.conn.execute(countQuery).scalar() or 0
		return result, count


	def get_playlist(
			self,
			playlistId: int
		) -> Optional[SongsPlaylistInfo]:
		playlistInfo = next(iter(self.get_playlists(playlistKeys=playlistId)), None)
		if not playlistInfo:
			return None
		songsQuery = select(
			sg_pk.label("id"),
			sg_name,
			sg_path,
			sg_internalpath,
			sg_track,
			coalesce[String](ar_name, "").label("artist"),
			dbLiteral(0).label("queuedtimestamp"),
			dbLiteral(playlistInfo.name).label("playlist")
		)\
			.join(
				song_artist_tbl,
				and_(sgar_songFk == sg_pk, sgar_isPrimaryArtist == 1),
				isouter=True
			)\
			.join(
				playlists_songs_tbl,
				plsg_songFk == sg_pk,
				isouter=True
			)\
			.where(plsg_playlistFk == playlistId)\
			.where(sg_deletedTimstamp.is_(None))\
			.order_by(dbCast(sg_track, Integer))
		songsResult = self.conn.execute(songsQuery).mappings().fetchall()
		pathRuleTree = None
		if self.current_user_provider.is_loggedIn():
			pathRuleTree = self.path_rule_service.get_rule_path_tree()

		songs = [
			SongListDisplayItem(
				**DictDotMap.unflatten(dict(row), omitNulls=True)
			) for row in songsResult
		]
		stations = [
			*self.stations_playlists_service.get_stations_by_playlist(
				playlistId,
			)
		]
		if pathRuleTree:
			for song in songs:
				song.rules = list(pathRuleTree.values_flat(
						normalize_opening_slash(song.treepath))
					)

		return SongsPlaylistInfo(
			**playlistInfo.model_dump(), 
			songs=songs,
			stations=stations
		)
	
	def add_playlist(self, playlist: PlaylistCreationInfo) -> PlaylistInfo:
		user = self.current_user_provider.current_user()
		savedName = SavedNameString(playlist.name)
		stmt = insert(playlists_tbl).values(
			name = str(savedName),
			displayname = playlist.displayname,
			lastmodifiedbyuserfk = user.id,
			lastmodifiedtimestamp = self.get_datetime().timestamp(),
			ownerfk = user.id
		)
		with self.conn.begin() as transaction:
			try:
				res = self.conn.execute(stmt)

				affectedPk = res.lastrowid
				self.stations_playlists_service.link_playlists_with_stations_in_trx(
					(StationPlaylistTuple(affectedPk, t.decoded_id() if t else None) 
						for t in (playlist.stations or [None])),
				)
				transaction.commit()

				owner = user.to_user()
				return PlaylistInfo(
					id=dtos.encode_playlist_id(affectedPk),
					name=str(savedName),
					owner=owner,
					displayname=playlist.displayname
				)
			except IntegrityError:
				raise AlreadyUsedError.build_error(
					f"{playlist.name} is already used for playlist.",
					"body->name"
				)
			

	def update_playlist(
		self,
		playlist: PlaylistCreationInfo,
		playlistId: int
	) -> PlaylistInfo:
		user = self.current_user_provider.current_user()
		savedName = SavedNameString(playlist.name)
		stmt = update(playlists_tbl).values(
			name = str(savedName),
			displayname = playlist.displayname,
			lastmodifiedbyuserfk = user.id,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		try:
			with self.conn.begin() as transaction:
				res = self.conn.execute(stmt)

				affectedPk = playlistId if playlistId else res.lastrowid
				self.stations_playlists_service.link_playlists_with_stations_in_trx(
					(StationPlaylistTuple(affectedPk, t.decoded_id() if t else None) 
						for t in (playlist.stations or [None])),
				)
				owner = self.get_playlist_owner(playlistId)
				transaction.commit()
				return PlaylistInfo(
					id=dtos.encode_playlist_id(affectedPk),
					name=str(savedName),
					owner=owner,
					displayname=playlist.displayname
				)
		except IntegrityError:
			raise AlreadyUsedError.build_error(
				f"{playlist.name} is already used for playlist.",
				"body->name"
			)


	def save_playlist(
		self,
		playlist: PlaylistCreationInfo,
		playlistId: int | None=None
	) -> PlaylistInfo:
		if not playlist and not playlistId:
			raise ValueError("No playlist info to save")
		if playlistId:
			return self.update_playlist(playlist, playlistId)
		else:
			return self.add_playlist(playlist)


	def delete_playlist(self, playlistkey: int) -> int:
		if not playlistkey:
			return 0
		delStmt = delete(playlists_tbl).where(pl_pk == playlistkey)
		delCount = self.conn.execute(delStmt).rowcount
		self.conn.commit()
		return delCount


	def __is_playlistName_used__(
		self,
		id: Optional[int],
		playlistName: SavedNameString,
	) -> bool:
		userId = self.current_user_provider.current_user().id
		queryAny = select(func.count(1)).select_from(playlists_tbl)\
				.where(pl_name == str(playlistName))\
				.where(pl_ownerFk == userId)\
				.where(pl_pk != id)
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False


	def is_playlistName_used(
		self,
		id: Optional[int],
		playlistName: str,
	) -> bool:
		cleanedPlaylistName = SavedNameString(playlistName)
		if not cleanedPlaylistName:
			return True
		return self.__is_playlistName_used__(id, cleanedPlaylistName)