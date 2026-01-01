from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	RulePriorityLevel,
	StationAlbumTuple,
	StationInfo,
)
from musical_chairs_libs.tables import (
	albums as albums_tbl, ab_pk,
	songs as songs_tbl, sg_pk, sg_albumFk, sg_deletedTimstamp,
	stations_albums as stations_albums_tbl,
	stab_albumFk, stab_stationFk,
	stations as stations_tbl, st_pk, st_name, st_displayName, st_procId, 
	st_ownerFk, st_typeid, st_bitrate, st_requestSecurityLevel, 
	st_viewSecurityLevel,
	users as user_tbl, u_pk, u_username, u_displayName
)
from sqlalchemy import (
	select,
	insert,
	delete,
	Integer,
	func
)
from sqlalchemy.sql.expression import case
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.engine import Connection
from sqlalchemy.sql.expression import (
	Tuple as dbTuple,
)
from .current_user_provider import CurrentUserProvider
from .station_service import StationService
from typing import (
	Any,
	cast,
	Collection,
	Iterable,
	Iterator,
	Optional,
	Tuple,
	Union
)

class StationsAlbumsService:

	def __init__(
		self,
		conn: Connection,
		stationService: StationService,
		currentUserProvider: CurrentUserProvider,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")

		self.conn = conn
		self.get_datetime = get_datetime
		self.station_service = stationService
		self.current_user_provider = currentUserProvider


	def get_station_albums(
		self,
		albumIds: Union[int, Iterable[int], None]=None,
		stationIds: Union[int, Iterable[int], None]=None,
	) -> Iterable[StationAlbumTuple]:
		query = select(
			stab_albumFk,
			stab_stationFk
		)\
			.join(albums_tbl, stab_albumFk == ab_pk)

		if type(albumIds) == int:
			query = query.where(stab_albumFk == albumIds)
		elif isinstance(albumIds, Iterable):
			query = query.where(stab_albumFk.in_(albumIds))
		if type(stationIds) == int:
			query = query.where(stab_stationFk == stationIds)
		elif isinstance(stationIds, Iterable):
			query = query.where(stab_stationFk.in_(stationIds))
		query = query.order_by(stab_albumFk)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (StationAlbumTuple(
				cast(int, row[0]),
				cast(int, row[1]),
				True
			)
			for row in records)


	def remove_album_for_stations(
		self,
		stationSongs: Union[
			Iterable[Union[StationAlbumTuple, Tuple[int, int]]],
			None
		]=None,
		albumIds: Union[int, Iterable[int], None]=None
	) -> int:
		if stationSongs is None and albumIds is None:
			raise ValueError("stationSongs or songIds must be provided")
		delStmt = delete(stations_albums_tbl)
		if isinstance(stationSongs, Iterable):
			delStmt = delStmt\
				.where(dbTuple(stab_albumFk, stab_stationFk).in_(stationSongs))
		elif isinstance(albumIds, Iterable):
			delStmt = delStmt.where(stab_albumFk.in_(albumIds))
		elif type(albumIds) is int:
			delStmt = delStmt.where(stab_albumFk == albumIds)
		else:
			return 0
		return self.conn.execute(delStmt).rowcount


	def validate_stations_albums(
		self,
		stationAlbums: Iterable[StationAlbumTuple]
	) -> Iterable[StationAlbumTuple]:
		if not stationAlbums:
			return iter([])
		stationAlbumSet = set(stationAlbums)
		albumQuery = select(ab_pk)\
			.where(
				ab_pk.in_((s.albumid for s in stationAlbumSet))
			)
		stationQuery = select(st_pk).where(
			st_pk.in_((s.stationid for s in stationAlbumSet))
		)

		albumRecords = self.conn.execute(albumQuery).fetchall()
		stationRecords = self.conn.execute(stationQuery).fetchall()\
			or [None] * len(albumRecords)
		yield from (t for t in (StationAlbumTuple(
			cast(int, albumRow[0]),
			cast(Optional[int], stationRow[0] if stationRow else None)
		) for albumRow in albumRecords 
			for stationRow in stationRecords
		) if t in stationAlbumSet)

	def link_albums_with_stations(
		self,
		stationSongs: Iterable[StationAlbumTuple],
	) -> Iterable[StationAlbumTuple]:
		if not stationSongs:
			return []
		uniquePairs = set(self.validate_stations_albums(stationSongs))
		if not uniquePairs:
			return []
		existingPairs = set(self.get_station_albums(
			albumIds={st.albumid for st in uniquePairs}
		))
		outPairs = existingPairs - uniquePairs
		inPairs = uniquePairs - existingPairs
		self.remove_album_for_stations(outPairs)
		if not inPairs: #if no songs - stations have been linked
			return existingPairs - outPairs
		userId = self.current_user_provider.current_user().id
		params: list[dict[str, Any]] = [{
			"albumfk": p.albumid,
			"stationfk": p.stationid,
			"lastmodifiedbyuserfk": userId,
			"lastmodifiedtimestamp": self.get_datetime().timestamp()
		} for p in inPairs if p.stationid]
		if params:
			stmt = insert(stations_albums_tbl)
			self.conn.execute(stmt, params)
		return self.get_station_albums(
			albumIds={st.albumid for st in uniquePairs}
		)
	
	def get_stations_by_album(
		self,
		albumId: int,
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
			st_viewSecurityLevel,
			st_typeid,
			st_bitrate,
		).select_from(stations_tbl)\
		.join(user_tbl, st_ownerFk == u_pk, isouter=True)\
		.join(stations_albums_tbl, stab_stationFk == st_pk)\
		.where(stab_albumFk == albumId)

		if self.current_user_provider.is_loggedIn():
			query = self.station_service.__attach_user_joins__(query, scopes)
		else:
			if scopes:
				return
			query = query.where(
				coalesce(st_viewSecurityLevel, 0) == 0
			)

		query = query.order_by(st_pk)
		records = self.conn.execute(query).mappings()

		if self.current_user_provider.is_loggedIn():
			yield from self.station_service.__generate_station_and_rules_from_rows__(
				records,
				scopes
			)
		else:
			for row in records:
				yield self.station_service.__row_to_station__(row)

	def get_station_song_counts(
		self,
		stationIds: Union[int, Iterable[int], None]=None,
		ownerId: Union[int, None]=None,
	) -> Iterator[Tuple[int, int]]:
		query = select(stab_stationFk, func.count(sg_pk))\
			.join(albums_tbl, stab_albumFk == ab_pk)\
			.join(songs_tbl, stab_albumFk == sg_albumFk)\
			.where(sg_deletedTimstamp.is_(None))

		if type(stationIds) == int:
			query = query.where(stab_stationFk == stationIds)
		elif isinstance(stationIds, Iterable):
			query = query.where(stab_stationFk.in_(stationIds))

		if type(ownerId) == int:
			query = query.join(stations_tbl, st_pk == stab_stationFk)\
				.where(st_ownerFk == ownerId)
		records = self.conn.execute(query)
		for row in records:
			yield cast(int,row[0]), cast(int,row[1])