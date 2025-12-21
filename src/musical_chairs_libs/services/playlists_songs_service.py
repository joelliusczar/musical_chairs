from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	DictDotMap,
	get_datetime,
	normalize_opening_slash,
	SongPlaylistTuple,
	SongListDisplayItem,
	calc_order_between,
	calc_order_next
)
from musical_chairs_libs.tables import (
	artists as artists_tbl, ar_name, ar_pk,
	albums as album_tbl, ab_pk, ab_name,
	songs as songs_tbl, sg_pk, sg_deletedTimstamp, sg_name, sg_path,
	sg_internalpath, sg_trackNum, sg_albumFk,
	song_artist as song_artist_tbl, sgar_songFk, sgar_isPrimaryArtist, 
	sgar_artistFk,
	playlists_songs as playlists_songs_tbl,
	plsg_songFk, plsg_playlistFk, plsg_lexorder, plsg_lastmodifiedtimestamp,
	st_pk
)
from .path_rule_service import PathRuleService
from sqlalchemy import (
	and_,
	select,
	insert,
	delete,
	literal as dbLiteral,
	String,
	update,
)
from sqlalchemy.engine import Connection
from sqlalchemy.sql.expression import (
	Tuple as dbTuple,
)
from sqlalchemy.sql.functions import coalesce
from typing import (
	Any,
	cast,
	Iterable,
	Iterator,
	Optional,
	Tuple,
	Union
)

class PlaylistsSongsService:

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

	def get_songs(
			self,
			playlistId: int,
			user: Optional[AccountInfo]=None
		) -> Iterator[SongListDisplayItem]:
		
		songsQuery = select(
			sg_pk.label("id"),
			sg_name,
			sg_path,
			sg_internalpath,
			sg_trackNum.label("track"),
			coalesce[String](ar_name, "").label("artist"),
			coalesce(ab_name, "").label("album"),
			dbLiteral(0).label("queuedtimestamp"),
		)\
			.join(
				song_artist_tbl,
				and_(sgar_songFk == sg_pk, sgar_isPrimaryArtist == 1),
				isouter=True
			)\
			.join(artists_tbl, sgar_artistFk == ar_pk, isouter=True)\
			.join(album_tbl, ab_pk == sg_albumFk, isouter=True)\
			.join(
				playlists_songs_tbl,
				plsg_songFk == sg_pk,
				isouter=True
			)\
			.where(plsg_playlistFk == playlistId)\
			.where(sg_deletedTimstamp.is_(None))\
			.order_by(plsg_lexorder, plsg_lastmodifiedtimestamp)
		songsResult = self.conn.execute(songsQuery).mappings()
		pathRuleTree = None
		if user:
			pathRuleTree = self.path_rule_service.get_rule_path_tree(user)

		for row in songsResult:

			song = SongListDisplayItem(
				**DictDotMap.unflatten(dict(row), omitNulls=True)
			) 
			if pathRuleTree:
				song.rules = list(pathRuleTree.valuesFlat(
					normalize_opening_slash(song.path))
				)
			yield song



	def get_playlist_songs(
		self,
		songIds: Union[int, Iterable[int], None]=None,
		playlistIds: Union[int, Iterable[int], None]=None,
	) -> Iterable[SongPlaylistTuple]:
		query = select(
			plsg_songFk,
			plsg_playlistFk,
			plsg_lexorder
		)\
			.join(songs_tbl, plsg_songFk == sg_pk)\
			.where(sg_deletedTimstamp.is_(None))

		if type(songIds) == int:
			query = query.where(plsg_songFk == songIds)
		elif isinstance(songIds, Iterable):
			query = query.where(plsg_songFk.in_(songIds))
		if type(playlistIds) == int:
			query = query.where(plsg_playlistFk == playlistIds)
		elif isinstance(playlistIds, Iterable):
			query = query.where(plsg_playlistFk.in_(playlistIds))
		query = query.order_by(plsg_lexorder, plsg_lastmodifiedtimestamp)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (SongPlaylistTuple(
				cast(int, row[0]),
				cast(int, row[1]),
				row[2].decode()
			)
			for row in records)


	def __remove_songs_for_playlists__(
		self,
		songsPlaylists: Union[
			Iterable[Union[SongPlaylistTuple, Tuple[int, int]]],
			None
		]
	) -> int:
		if songsPlaylists is None:
			raise ValueError("songsPlaylists must be provided")
		delStmt = delete(playlists_songs_tbl)\
			.where(dbTuple(plsg_songFk, plsg_playlistFk).in_(songsPlaylists))
		return self.conn.execute(delStmt).rowcount


	def remove_songs_for_playlists(
		self,
		songsPlaylists: Union[
			Iterable[Union[SongPlaylistTuple, Tuple[int, int]]],
			None
		]
	) -> int:
		res = self.__remove_songs_for_playlists__(songsPlaylists)
		self.conn.commit()
		return res

	def validate_songs_playlists(
		self,
		songsPlaylists: Iterable[SongPlaylistTuple]
	) -> Iterable[SongPlaylistTuple]:
		if not songsPlaylists:
			return iter([])
		songsPlaylistsSet = set(songsPlaylists)
		songQuery = select(sg_pk)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(
				sg_pk.in_((s.songid for s in songsPlaylistsSet))
			)
		playlistQuery = select(st_pk).where(
			st_pk.in_((s.playlistid for s in songsPlaylistsSet))
		)

		songRecords = self.conn.execute(songQuery)
		playlistRecords = self.conn.execute(playlistQuery)
		yield from (t for t in (SongPlaylistTuple(
			cast(int, songRow[0]),
			cast(int, playlistRow[0])
		) for songRow in songRecords 
			for playlistRow in playlistRecords
		) if t in songsPlaylistsSet)

	def link_songs_with_playlists(
		self,
		songsPlaylists: Iterable[SongPlaylistTuple],
		userId: Optional[int]=None
	) -> Iterable[SongPlaylistTuple]:
		if not songsPlaylists:
			return []
		uniquePairs = set(self.validate_songs_playlists(songsPlaylists))
		if not uniquePairs:
			return []
		existingPairs = set(self.get_playlist_songs(
			songIds={st.songid for st in uniquePairs}
		))
		outPairs = existingPairs - uniquePairs
		inPairs = uniquePairs - existingPairs
		self.__remove_songs_for_playlists__(outPairs)
		if not inPairs: #if no songs - stations have been linked
			return existingPairs - outPairs
		startOrder = max((p.lexorder for p in existingPairs), default="0")
		params: list[dict[str, Any]] = []
		for p in inPairs:
			startOrder = calc_order_next(startOrder)
			params.append({
				"songfk": p.songid,
				"playlistfk": p.playlistid,
				"lexorder": startOrder.encode(),
				"lastmodifiedbyuserfk": userId,
				"lastmodifiedtimestamp": self.get_datetime().timestamp()
			})
		
		stmt = insert(playlists_songs_tbl)
		self.conn.execute(stmt, params)
		return self.get_playlist_songs(
			songIds={st.songid for st in uniquePairs}
		)
	
	def move_song(self, playlistid: int, songid: int, order: int):
		query = select(plsg_songFk, plsg_lexorder)\
			.where(plsg_playlistFk == playlistid)\
			.order_by(plsg_lexorder, plsg_lastmodifiedtimestamp)
		
		if order > 1:
			query = query.offset(order - 2).limit(2)
		else:
			query = query.limit(1)
		
		records = self.conn.execute(query).fetchall()
		if not any(records):
			raise RuntimeError("There are no songs in this playlist")
		if any(r[0] == songid and r[1] == order for r in records):
			return
		
		upper = records[1][1] if len(records) > 1 else records[0][1]
		lower = records[0][1] if len(records) > 1 else b""
		mid = calc_order_between(lower.strip().decode(), upper.strip().decode())
		stmt = update(playlists_songs_tbl).values(lexorder = mid.encode())\
			.where(plsg_playlistFk == playlistid)\
			.where(plsg_songFk == songid)
		self.conn.execute(stmt)
		self.conn.commit()



		