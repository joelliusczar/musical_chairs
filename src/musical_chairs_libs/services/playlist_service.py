
from typing import (
	Iterator,
	Optional,
	Union,
	cast,
	Iterable,
	Tuple,
	Collection
)
from musical_chairs_libs.dtos_and_utilities import (
	SavedNameString,
	get_datetime,
	PlaylistInfo,
	PlaylistCreationInfo,
	AlreadyUsedError,
	AccountInfo,
	OwnerInfo,
	SongsPlaylistInfo,
	SongListDisplayItem,
	DictDotMap,
	normalize_opening_slash,
	RulePriorityLevel,
	UserRoleDomain,
	get_playlist_owner_roles,
	UserRoleDef,
	build_placeholder_select,
	StationPlaylistTuple,
)
from .current_user_provider import CurrentUserProvider
from .path_rule_service import PathRuleService
from .stations_playlists_service import StationsPlaylistsService
from sqlalchemy import (
	select,
	Select,
	insert,
	update,
	Integer,
	func,
	Float,
	delete,
	literal as dbLiteral,
	String,
	and_,
	or_,
	true,
	false,
	union_all,
)
from sqlalchemy.sql.expression import (
	case,
	CompoundSelect,
	Update,
	cast as dbCast,
)
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.schema import Column
from musical_chairs_libs.tables import (
	playlists as playlists_tbl, pl_description, pl_viewSecurityLevel,
	pl_name, pl_pk, pl_ownerFk, plup_count, plup_span, plup_priority,
	ar_name,
	users as user_tbl, u_pk, u_username, u_displayName, 
	ur_userFk, ur_role, ur_count, ur_span, ur_priority,
	sg_pk, sg_name, sg_track, sg_path, sg_internalpath,
	sg_deletedTimstamp,
	playlists_songs as playlists_songs_tbl, plsg_songFk, plsg_playlistFk, 
	song_artist as song_artist_tbl, sgar_songFk, sgar_isPrimaryArtist,
	plup_userFk, plup_playlistFk, plup_role
)

__playlist_permissions_query__ = select(
	plup_userFk.label("rule_userfk"),
	plup_role.label("rule_name"),
	plup_count.label("rule_count"),
	plup_span.label("rule_span"),
	coalesce[Integer](
		plup_priority,
		RulePriorityLevel.STATION_PATH.value
	).label("rule_priority"),
	dbLiteral(UserRoleDomain.Playlist.value).label("rule_domain"),
	plup_playlistFk.label("rule_playlistfk")
)

def build_playlist_rules_query(
	userId: Optional[int]=None
) -> CompoundSelect[Tuple[int, str, float, float, int, str]]:
	user_rules_query = select(
		ur_userFk.label("rule_userfk"),
		ur_role.label("rule_name"),
		ur_count.label("rule_count"),
		ur_span.label("rule_span"),
		coalesce[Integer](
			ur_priority,
			case(
				(ur_role == UserRoleDef.ADMIN.value, RulePriorityLevel.SUPER.value),
				else_=RulePriorityLevel.SITE.value
			)
		).label("rule_priority"),
		dbLiteral(UserRoleDomain.Site.value).label("rule_domain"),
		dbLiteral(None).label("rule_playlistfk")
	).where(or_(
			ur_role.like(f"{UserRoleDomain.Playlist.value}:%"),
			ur_role == UserRoleDef.ADMIN.value
		),
	)
	domain_permissions_query = __playlist_permissions_query__
	placeholder_select = build_placeholder_select(
		UserRoleDomain.Playlist
	).add_columns(
		dbLiteral(None).label("rule_playlistfk")
	)

	if userId is not None:
		domain_permissions_query = \
			domain_permissions_query.where(plup_userFk == userId)
		user_rules_query = user_rules_query.where(ur_userFk == userId)
		
	query = union_all(
		placeholder_select,
		domain_permissions_query,
		user_rules_query,
	)
	return query

class PlaylistService:

	def __init__(
		self,
		conn: Connection,
		currentUserProvider: CurrentUserProvider,
		stationsPlaylistsService: StationsPlaylistsService,
		pathRuleService: Optional[PathRuleService]=None,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		if not pathRuleService:
			pathRuleService = PathRuleService(conn)
		if not stationsPlaylistsService:
			stationsPlaylistsService = StationsPlaylistsService(conn)
		self.conn = conn
		self.get_datetime = get_datetime
		self.path_rule_service = pathRuleService
		self.stations_playlists_service = stationsPlaylistsService
		self.current_user_provider = currentUserProvider


	def __attach_user_joins__(
		self,
		query: Select[
			Tuple[
				Integer,
				Union[String, None],
				Union[String, None],
				String,
				Integer,
				Union[String, None],
				# Union[String, None],
				Integer
			]
		],
		userId: int,
		scopes: Optional[Collection[str]]=None
	) -> Select[
			Tuple[
				Integer,
				Union[String, None],
				Union[String, None],
				String,
				Integer,
				Union[String, None],
				Integer,
			]
		]:
		rulesQuery = build_playlist_rules_query(userId)
		rulesSubquery = rulesQuery.cte(name="rulesQuery")
		canViewQuery= select(
			rulesSubquery.c.rule_playlistfk, #pyright: ignore [reportUnknownMemberType]
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

		ownerScopeSet = set(get_playlist_owner_roles(scopes))

		query = query.join(
			rulesSubquery,
			or_(
				rulesSubquery.c.rule_playlistfk == pl_pk, #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
				rulesSubquery.c.rule_playlistfk == -1, #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
				rulesSubquery.c.rule_playlistfk.is_(None) #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
			)
		).where(
			or_(
				coalesce(
					pl_viewSecurityLevel,
					RulePriorityLevel.INVITED_USER.value
				) < select(coalesce[int](
							func.max(canViewQuery.c.rule_priority), #pyright: ignore [reportUnknownMemberType]
							RulePriorityLevel.NONE.value
						)).where(pl_pk == canViewQuery.c.rule_playlistfk).scalar_subquery(), #pyright: ignore [reportUnknownMemberType]
				and_(
					dbLiteral(UserRoleDomain.Site.value)
						.in_( #pyright: ignore [reportUnknownMemberType]
							select(canViewQuery.c.rule_domain) #pyright: ignore [reportUnknownMemberType]
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
		).where(
				or_(
					rulesSubquery.c.rule_name.in_(scopes) if scopes else true(), #pyright: ignore [reportUnknownMemberType]
					(pl_ownerFk == userId) if scopes and ownerScopeSet else false()
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


	def get_playlists(
		self,
		playlistKeys: Union[int, str, Iterable[int], None]=None,
		ownerId: Union[int, None]=None,
		user: Optional[AccountInfo]=None,
		scopes: Optional[Collection[str]]=None,
		page: int = 0,
		pageSize: Optional[int]=None,
	) -> Iterator[PlaylistInfo]:
		query = select(
			pl_pk,
			pl_name,
			pl_description,
			u_username,
			pl_ownerFk,
			u_displayName,
			pl_viewSecurityLevel
		).select_from(playlists_tbl)\
		.join(user_tbl, pl_ownerFk == u_pk, isouter=True)

		if user:
			query = self.__attach_user_joins__(query, user.id, scopes)
		else:
			if scopes:
				return
			query = query.where(
				coalesce(pl_viewSecurityLevel, 0) == 0
			)
		if type(ownerId) is int:
			query = query.where(pl_ownerFk == ownerId)
		if type(playlistKeys) == int:
			query = query.where(pl_pk == playlistKeys)
		elif isinstance(playlistKeys, Iterable) and not isinstance(playlistKeys, str):
			query = query.where(pl_pk.in_(playlistKeys))
		elif type(playlistKeys) is str:
			lPlaylistKey = playlistKeys.replace("_","\\_").replace("%","\\%")
			query = query\
				.where(pl_name.like(f"%{lPlaylistKey}%"))
		query = query.order_by(pl_pk)
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query).mappings()

		if user:
			yield from PlaylistInfo.generate_playlist_and_rules_from_rows(
				records,
				user.id,
				scopes
			)
		else:
			for row in records:
				yield PlaylistInfo.row_to_playlist(row)


	def get_playlist_owner(self, playlistId: int) -> OwnerInfo:
		query = select(pl_ownerFk, u_username, u_displayName)\
			.select_from(playlists_tbl)\
			.join(user_tbl, u_pk == pl_ownerFk)\
			.where(pl_pk == playlistId)
		data = self.conn.execute(query).mappings().fetchone()
		if not data:
			return OwnerInfo(id=0,username="", displayname="")
		return OwnerInfo(
			id=data[pl_ownerFk],
			username=data[u_username],
			displayname=data[u_displayName]
		)


	def get_playlists_page(
		self,
		page: int = 0,
		playlist: str = "",
		limit: Optional[int]=None,
		user: Optional[AccountInfo]=None
	) -> Tuple[list[PlaylistInfo], int]:
		result = list(self.get_playlists(
			page=page,
			pageSize=limit,
			playlistKeys=playlist
		))
		countQuery = select(func.count(1))\
			.select_from(playlists_tbl)
		count = self.conn.execute(countQuery).scalar() or 0
		return result, count


	def get_playlist(
			self,
			playlistId: int,
			user: Optional[AccountInfo]=None
		) -> Optional[SongsPlaylistInfo]:
		playlistInfo = next(self.get_playlists(playlistKeys=playlistId), None)
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
		songsResult = self.conn.execute(songsQuery).mappings()
		pathRuleTree = None
		if user:
			pathRuleTree = self.path_rule_service.get_rule_path_tree(user)

		songs = [
			SongListDisplayItem(
				**DictDotMap.unflatten(dict(row), omitNulls=True)
			) for row in songsResult
		]
		stations = [
			*self.stations_playlists_service.get_stations_by_playlist(
				playlistId,
				user
			)
		]
		if pathRuleTree:
			for song in songs:
				song.rules = list(pathRuleTree.valuesFlat(
						normalize_opening_slash(song.path))
					)

		return SongsPlaylistInfo(
			**playlistInfo.model_dump(), 
			songs=songs,
			stations=stations
		)


	def save_playlist(
		self,
		playlist: PlaylistCreationInfo,
		playlistId: Optional[int]=None
	) -> PlaylistInfo:
		if not playlist and not playlistId:
			raise ValueError("No playlist info to save")
		user = self.current_user_provider.get_rate_limited_user()
		upsert = update if playlistId else insert
		savedName = SavedNameString(playlist.name)
		stmt = upsert(playlists_tbl).values(
			name = str(savedName),
			description = playlist.description,
			lastmodifiedbyuserfk = user.id,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		owner = user
		if playlistId and isinstance(stmt, Update):
			stmt = stmt.where(pl_pk == playlistId)
			owner = self.get_playlist_owner(playlistId)
		else:
			stmt = stmt.values(ownerfk = user.id)
		try:
			res = self.conn.execute(stmt)

			affectedPk = playlistId if playlistId else res.lastrowid
			self.stations_playlists_service.link_playlists_with_stations(
				(StationPlaylistTuple(affectedPk, t.id if t else None) 
					for t in (playlist.stations or [None])),
				user.id
			)
			self.conn.commit()
			if res.rowcount == 0:
				raise RuntimeError("Failed to create playlist")
			return PlaylistInfo(
				id=affectedPk,
				name=str(savedName),
				owner=owner,
				description=playlist.description
			)
		except IntegrityError:
			raise AlreadyUsedError.build_error(
				f"{playlist.name} is already used for playlist.",
				"body->name"
			)


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