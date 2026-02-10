import musical_chairs_libs.dtos_and_utilities as dtos
from .current_user_provider import CurrentUserProvider
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	StationSongTuple
)
from musical_chairs_libs.tables import (
	songs as songs_tbl, sg_pk, sg_deletedTimstamp,
	stations_songs as stations_songs_tbl,
	stsg_songFk, stsg_stationFk,
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

class StationsSongsService:

	def __init__(
		self,
		conn: Connection,
		currentUserProvider: CurrentUserProvider,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime
		self.current_user_provider = currentUserProvider


	def get_station_songs(
		self,
		songIds: int | Iterable[int] | None=None,
		stationIds: int | Iterable[int] | None=None,
	) -> list[StationSongTuple]:
		with dtos.open_transaction(self.conn):
			query = select(
				stsg_songFk,
				stsg_stationFk
			)\
				.join(songs_tbl, stsg_songFk == sg_pk)\
				.where(sg_deletedTimstamp.is_(None))

			if type(songIds) == int:
				query = query.where(stsg_songFk == songIds)
			elif isinstance(songIds, Iterable):
				query = query.where(stsg_songFk.in_(songIds))
			if type(stationIds) == int:
				query = query.where(stsg_stationFk == stationIds)
			elif isinstance(stationIds, Iterable):
				query = query.where(stsg_stationFk.in_(stationIds))
			query = query.order_by(stsg_songFk)
			with dtos.open_transaction(self.conn):
				records = self.conn.execute(query).fetchall()
				return [StationSongTuple(
						cast(int, row[0]),
						cast(int, row[1]),
						True
					)
					for row in records]


	def __remove_songs_for_stations_in_trx__(
		self,
		stationSongs: Union[
			Iterable[Union[StationSongTuple, Tuple[int, int]]],
			None
		]=None,
		songIds: Union[int, Iterable[int], None]=None
	) -> int:
		if stationSongs is None and songIds is None:
			raise ValueError("stationSongs or songIds must be provided")
		delStmt = delete(stations_songs_tbl)
		if isinstance(stationSongs, Iterable):
			delStmt = delStmt\
				.where(dbTuple(stsg_songFk, stsg_stationFk).in_(stationSongs))
		elif isinstance(songIds, Iterable):
			delStmt = delStmt.where(stsg_songFk.in_(songIds))
		elif type(songIds) is int:
			delStmt = delStmt.where(stsg_songFk == songIds)
		else:
			return 0
		return self.conn.execute(delStmt).rowcount


	def validate_stations_songs(
		self,
		stationSongs: Iterable[StationSongTuple]
	) -> list[StationSongTuple]:
		if not stationSongs:
			return []
		stationSongSet = set(stationSongs)
		songQuery = select(sg_pk)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(
				sg_pk.in_((s.songid for s in stationSongSet))
			)
		stationQuery = select(st_pk).where(
			st_pk.in_((s.stationid for s in stationSongSet))
		)

		with dtos.open_transaction(self.conn):
			songRecords = self.conn.execute(songQuery).fetchall()
			stationRecords = self.conn.execute(stationQuery).fetchall()\
				or [None] * len(songRecords)
			return [t for t in (StationSongTuple(
				cast(int, songRow[0]),
				cast(Optional[int], stationRow[0] if stationRow else None)
			) for songRow in songRecords 
				for stationRow in stationRecords
			) if t in stationSongSet]


	def link_songs_with_stations_in_trx(
		self,
		stationSongs: Iterable[StationSongTuple],
	) -> Iterable[StationSongTuple]:
		if not self.conn.in_transaction():
			raise RuntimeError("This method must be called inside a transaction")

		if not stationSongs:
			return []
		uniquePairs = set(self.validate_stations_songs(stationSongs))
		if not uniquePairs:
			return []
		existingPairs = set(self.get_station_songs(
			songIds={st.songid for st in uniquePairs}
		))
		outPairs = existingPairs - uniquePairs
		inPairs = uniquePairs - existingPairs
		self.__remove_songs_for_stations_in_trx__(outPairs)
		if not inPairs: #if no songs - stations have been linked
			return existingPairs - outPairs
		userId = self.current_user_provider.current_user().id
		params: list[dict[str, Any]] = [{
			"songfk": p.songid,
			"stationfk": p.stationid,
			"lastmodifiedbyuserfk": userId,
			"lastmodifiedtimestamp": self.get_datetime().timestamp()
		} for p in inPairs if p.stationid]
		if params:
			stmt = insert(stations_songs_tbl)
			self.conn.execute(stmt, params)
		return self.get_station_songs(
			songIds={st.songid for st in uniquePairs}
		)