from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	SongPlaylistTuple
)
from musical_chairs_libs.tables import (
	songs as songs_tbl, sg_pk, sg_deletedTimstamp,
	playlists_songs as playlists_songs_tbl,
	plsg_songFk, plsg_playlistFk,
	st_pk
)
from sqlalchemy import (
	select,
	insert,
	delete,
)
from sqlalchemy.engine import Connection
from sqlalchemy.sql.expression import (
	Tuple as dbTuple,
)
from typing import (
	Any,
	cast,
	Iterable,
	Optional,
	Tuple,
	Union
)

class PlaylistsSongsService:

	def __init__(
		self,
		conn: Connection
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime

	def get_playlist_songs(
		self,
		songIds: Union[int, Iterable[int], None]=None,
		playlistIds: Union[int, Iterable[int], None]=None,
	) -> Iterable[SongPlaylistTuple]:
		query = select(
			plsg_songFk,
			plsg_playlistFk
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
		query = query.order_by(plsg_songFk)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (SongPlaylistTuple(
				cast(int, row[0]),
				cast(int, row[1]),
				True
			)
			for row in records)


	def remove_songs_for_playlists(
		self,
		songsPlaylists: Union[
			Iterable[Union[SongPlaylistTuple, Tuple[int, int]]],
			None
		]=None,
		songIds: Union[int, Iterable[int], None]=None
	) -> int:
		if songsPlaylists is None and songIds is None:
			raise ValueError("stationSongs or songIds must be provided")
		delStmt = delete(playlists_songs_tbl)
		if isinstance(songsPlaylists, Iterable):
			delStmt = delStmt\
				.where(dbTuple(plsg_songFk, plsg_playlistFk).in_(songsPlaylists))
		elif isinstance(songIds, Iterable):
			delStmt = delStmt.where(plsg_songFk.in_(songIds))
		elif type(songIds) is int:
			delStmt = delStmt.where(plsg_songFk == songIds)
		else:
			return 0
		return self.conn.execute(delStmt).rowcount


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

		songRecords = self.conn.execute(songQuery).fetchall()
		playlistRecords = self.conn.execute(playlistQuery).fetchall()
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
		self.remove_songs_for_playlists(outPairs)
		if not inPairs: #if no songs - stations have been linked
			return existingPairs - outPairs
		params: list[dict[str, Any]] = [{
			"songfk": p.songid,
			"playlistfk": p.playlistid,
			"lastmodifiedbyuserfk": userId,
			"lastmodifiedtimestamp": self.get_datetime().timestamp()
		} for p in inPairs]
		stmt = insert(playlists_songs_tbl)
		self.conn.execute(stmt, params)
		return self.get_playlist_songs(
			songIds={st.songid for st in uniquePairs}
		)