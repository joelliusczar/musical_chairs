
from typing import (
	Optional,
	Union,
	cast,
	Iterable,
	Tuple,
	Callable
)
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	SongArtistTuple,
)
from sqlalchemy import (
	select,
	insert,
	delete,
)
from sqlalchemy.sql.expression import (
	Tuple as dbTuple,
)
from sqlalchemy.engine import Connection
from itertools import groupby
from musical_chairs_libs.tables import (
	song_artist as song_artist_tbl,
	sg_pk, ar_pk,
	sgar_isPrimaryArtist, sgar_songFk, sgar_artistFk,

)



class SongArtistService:

	def __init__(
		self,
		conn: Connection
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime

	def get_song_artists(
		self,
		songIds: Union[int, Iterable[int],None]=None,
		artistIds: Union[int, Iterable[int],None]=None,
	) -> Iterable[SongArtistTuple]:
		query = select(
			sgar_artistFk,
			sgar_songFk,
			sgar_isPrimaryArtist
		)

		if type(songIds) == int:
			query = query.where(sgar_songFk == songIds)
		elif isinstance(songIds, Iterable):
			query = query.where(sgar_songFk.in_(songIds))
		if type(artistIds) == int:
			query = query.where(sgar_artistFk == artistIds)
		elif isinstance(artistIds, Iterable):
			query = query.where(sgar_artistFk.in_(artistIds))
		query = query.order_by(sgar_songFk)
		records = self.conn.execute(query).mappings()
		yield from (SongArtistTuple(
				row[sgar_songFk],
				row[sgar_artistFk],
				row[sgar_isPrimaryArtist]
			)
			for row in records)
		
	def remove_songs_for_artists(
		self,
		songArtists: Iterable[Union[SongArtistTuple, Tuple[int, int]]],
	) -> int:
		songArtists = songArtists or []
		delStmt = delete(song_artist_tbl)\
			.where(dbTuple(sgar_songFk, sgar_artistFk).in_(songArtists))
		count = self.conn.execute(delStmt).rowcount
		return count

	def validate_song_artists(
		self,
		songArtists: Iterable[SongArtistTuple]
	) -> Iterable[SongArtistTuple]:
		if not songArtists:
			return iter([])
		songArtistsSet = set(songArtists)
		primaryArtistId = next(
			(sa.artistid for sa in songArtistsSet if sa.isprimaryartist),
			-1
		)
		songQuery = select(sg_pk).where(
			sg_pk.in_(s.songid for s in songArtistsSet)
		)
		artistsQuery = select(ar_pk).where(
			ar_pk.in_(a.artistid for a in songArtistsSet)
		)
		songRecords = self.conn.execute(songQuery).fetchall()
		artistRecords = self.conn.execute(artistsQuery).fetchall()

		yield from (t for t in (SongArtistTuple(
			songRow[0],
			artistRow[0],
			isprimaryartist=cast(int, artistRow[0]) == primaryArtistId
		) for songRow in songRecords
			for artistRow in artistRecords
		) if t in songArtistsSet)


	def __are_all_primary_artist_single(
		self,
		songArtists: Iterable[SongArtistTuple]
	) -> bool:
		songKey: Callable[[SongArtistTuple],int] = lambda a: a.songid
		artistsGroups = groupby(sorted(songArtists, key=songKey), key=songKey)
		for _, g in artistsGroups:
			if len([sa for sa in g if sa.isprimaryartist]) > 1:
				return False
		return True

	def link_songs_with_artists(
		self,
		songArtists: Iterable[SongArtistTuple],
		userId: Optional[int]=None
	) -> Iterable[SongArtistTuple]:
		if not songArtists:
			return []
		uniquePairs = set(self.validate_song_artists(songArtists))

		if not self.__are_all_primary_artist_single(uniquePairs):
			raise ValueError("Only one artist can be the primary artist")
		existingPairs = set(self.get_song_artists(
			songIds={sa.songid for sa in uniquePairs}
		))
		outPairs = existingPairs - uniquePairs
		inPairs = uniquePairs - existingPairs
		self.remove_songs_for_artists(outPairs)
		if not inPairs: #if no songs - artist have been linked
			return existingPairs - outPairs
		params = [{
			"songfk": p.songid,
			"artistfk": p.artistid,
			"isprimaryartist": p.isprimaryartist,
			"lastmodifiedbyuserfk": userId,
			"lastmodifiedtimestamp": self.get_datetime().timestamp()
		} for p in inPairs]
		stmt = insert(song_artist_tbl)
		self.conn.execute(stmt, params)
		return self.get_song_artists(
			songIds={sa.songid for sa in uniquePairs}
		)