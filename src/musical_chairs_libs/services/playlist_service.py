
from typing import (
	Iterator,
	Optional,
	Union,
	cast,
	Iterable,
	Tuple
)
from musical_chairs_libs.dtos_and_utilities import (
	SavedNameString,
	SearchNameString,
	get_datetime,
	PlaylistInfo,
	PlaylistCreationInfo,
	AlreadyUsedError,
	AccountInfo,
	OwnerInfo,
	SongsPlaylistInfo,
	SongListDisplayItem,
	DictDotMap,
	normalize_opening_slash
)
from .path_rule_service import PathRuleService
from sqlalchemy import (
	select,
	insert,
	update,
	Integer,
	func,
	delete,
	literal,
	String,
	and_
)
from sqlalchemy.sql.expression import (
	Update,
	cast as dbCast,
)
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.schema import Column
from musical_chairs_libs.tables import (
	playlists as playlists_tbl,
	pl_name, pl_pk, pl_ownerFk,
	ar_name,
	users as user_tbl, u_pk, u_username, u_displayName,
	sg_pk, sg_name, sg_track, sg_path, sg_internalpath,
	sg_deletedTimstamp,
	song_playlist as song_playlist_tbl, sgpl_songFk, sgpl_playlistFk, 
	song_artist as song_artist_tbl, sgar_songFk, sgar_isPrimaryArtist
)



class PlaylistService:

	def __init__(
		self,
		conn: Connection,
		pathRuleService: Optional[PathRuleService]=None
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		if not pathRuleService:
			pathRuleService = PathRuleService(conn)
		self.conn = conn
		self.get_datetime = get_datetime
		self.path_rule_service = pathRuleService

	def get_playlists(
		self,
		page: int = 0,
		pageSize: Optional[int]=None,
		playlistKeys: Union[int, str, Iterable[int], None]=None,
		userId: Optional[int]=None,
		exactStrMatch: bool=False
	) -> Iterator[PlaylistInfo]:
		playlist_owner = user_tbl.alias("playlistowner")
		playlistOwnerId = cast(Column[Integer], playlist_owner.c.pk)
		query = select(
			pl_pk.label("id"),
			pl_name.label("name"),
			pl_ownerFk.label("playlist.ownerid"),
			playlist_owner.c.username.label("playlist.ownername"),
			playlist_owner.c.displayname.label("playlist.ownerdisplayname"),
		).select_from(playlists_tbl)\
			.join(playlist_owner, playlistOwnerId == pl_ownerFk, isouter=True)
		if type(playlistKeys) == int:
			query = query.where(pl_pk == playlistKeys)
		elif type(playlistKeys) is str:
			if playlistKeys:
				searchStr = SearchNameString.format_name_for_search(playlistKeys)
				if exactStrMatch:
					query = query\
						.where(pl_name == searchStr)
				else:
					query = query\
						.where(pl_name.like(f"%{searchStr}%"))
		elif isinstance(playlistKeys, Iterable):
			query = query.where(pl_pk.in_(playlistKeys))

		if userId:
			query = query.where(pl_ownerFk == userId)
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query).mappings()
		yield from (PlaylistInfo(
			id=row["id"],
			name=row["name"],
			owner=OwnerInfo(
				id=row["playlist.ownerid"],
				username=row["playlist.ownername"],
				displayname=row["playlist.ownerdisplayname"]
			)
		) for row in records)

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
		result = list(self.get_playlists(page, limit, playlist))
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
			literal(0).label("queuedtimestamp"),
			literal(playlistInfo.name).label("playlist")
		)\
			.join(
				song_artist_tbl,
				and_(sgar_songFk == sg_pk, sgar_isPrimaryArtist == 1),
				isouter=True
			)\
			.join(
				song_playlist_tbl,
				sgpl_songFk == sg_pk,
				isouter=True
			)\
			.where(sgpl_playlistFk == playlistId)\
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
		if pathRuleTree:
			for song in songs:
				song.rules = list(pathRuleTree.valuesFlat(
						normalize_opening_slash(song.path))
					)

		return SongsPlaylistInfo(**playlistInfo.model_dump(), songs=songs)


	def save_playlist(
		self,
		playlist: PlaylistCreationInfo,
		user: AccountInfo,
		playlistId: Optional[int]=None
	) -> Optional[PlaylistInfo]:
		if not playlist and not playlistId:
			raise ValueError("No playlist info to save")
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

			self.conn.commit()
			if res.rowcount == 0:
				return None
			return PlaylistInfo(
				id=affectedPk,
				name=str(savedName),
				owner=owner,
				description=playlist.description
			)
		except IntegrityError:
			raise AlreadyUsedError.build_error(
				f"{playlist.name} is already used for artist.",
				"body->name"
			)
		
	def delete_playlist(self, playlistkey: int) -> int:
		if not playlistkey:
			return 0
		delStmt = delete(playlists_tbl).where(pl_pk == playlistkey)
		delCount = self.conn.execute(delStmt).rowcount
		self.conn.commit()
		return delCount
