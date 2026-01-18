from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	RulePriorityLevel,
	StationPlaylistTuple,
	StationInfo,
)
from musical_chairs_libs.tables import (
	songs as songs_tbl, sg_pk, sg_deletedTimstamp,
	playlists_songs as playlists_songs_tbl, plsg_songFk, plsg_playlistFk,
	playlists as playlists_tbl, pl_pk, 
	stab_albumFk,
	stations_playlists as stations_playlists_tbl,
	stpl_playlistFk, stpl_stationFk,
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

class StationsPlaylistsService:

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


	def get_station_playlists(
		self,
		playlistsIds: Union[int, Iterable[int], None]=None,
		stationIds: Union[int, Iterable[int], None]=None,
	) -> Iterable[StationPlaylistTuple]:
		query = select(
			stpl_playlistFk,
			stpl_stationFk
		)\
			.join(playlists_tbl, stpl_playlistFk == pl_pk)

		if type(playlistsIds) == int:
			query = query.where(stpl_playlistFk == playlistsIds)
		elif isinstance(playlistsIds, Iterable):
			query = query.where(stpl_playlistFk.in_(playlistsIds))
		if type(stationIds) == int:
			query = query.where(stpl_stationFk == stationIds)
		elif isinstance(stationIds, Iterable):
			query = query.where(stpl_stationFk.in_(stationIds))
		query = query.order_by(stpl_playlistFk)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (StationPlaylistTuple(
				cast(int, row[0]),
				cast(int, row[1]),
				True
			)
			for row in records)


	def remove_playlist_for_stations(
		self,
		stationPlaylists: Union[
			Iterable[Union[StationPlaylistTuple, Tuple[int, int]]],
			None
		]=None,
		playlistsIds: Union[int, Iterable[int], None]=None
	) -> int:
		if stationPlaylists is None and playlistsIds is None:
			raise ValueError("stationPlaylists or playlistsIds must be provided")
		delStmt = delete(stations_playlists_tbl)
		if isinstance(stationPlaylists, Iterable):
			delStmt = delStmt\
				.where(dbTuple(stpl_playlistFk, stpl_stationFk).in_(stationPlaylists))
		elif isinstance(playlistsIds, Iterable):
			delStmt = delStmt.where(stab_albumFk.in_(playlistsIds))
		elif type(playlistsIds) is int:
			delStmt = delStmt.where(stab_albumFk == playlistsIds)
		else:
			return 0
		return self.conn.execute(delStmt).rowcount


	def validate_stations_playlists(
		self,
		stationPlaylists: Iterable[StationPlaylistTuple]
	) -> Iterable[StationPlaylistTuple]:
		if not stationPlaylists:
			return iter([])
		stationPlaylistSet = set(stationPlaylists)
		playlistQuery = select(pl_pk)\
			.where(
				pl_pk.in_((s.playlistid for s in stationPlaylistSet))
			)
		stationQuery = select(st_pk).where(
			st_pk.in_((s.stationid for s in stationPlaylistSet))
		)

		playlistRecords = self.conn.execute(playlistQuery).fetchall()
		stationRecords = self.conn.execute(stationQuery).fetchall()\
			or [None] * len(playlistRecords)
		yield from (t for t in (StationPlaylistTuple(
			cast(int, playlistRow[0]),
			cast(Optional[int], stationRow[0] if stationRow else None)
		) for playlistRow in playlistRecords 
			for stationRow in stationRecords
		) if t in stationPlaylistSet)

	def link_playlists_with_stations(
		self,
		stationPlaylists: Iterable[StationPlaylistTuple]
	) -> Iterable[StationPlaylistTuple]:
		if not stationPlaylists:
			return []
		uniquePairs = set(self.validate_stations_playlists(stationPlaylists))
		if not uniquePairs:
			return []
		existingPairs = set(self.get_station_playlists(
			playlistsIds={st.playlistid for st in uniquePairs}
		))
		outPairs = existingPairs - uniquePairs
		inPairs = uniquePairs - existingPairs
		self.remove_playlist_for_stations(outPairs)
		if not inPairs: #if no songs - stations have been linked
			return existingPairs - outPairs
		userId = self.current_user_provider.current_user().id
		params: list[dict[str, Any]] = [{
			"playlistfk": p.playlistid,
			"stationfk": p.stationid,
			"lastmodifiedbyuserfk": userId,
			"lastmodifiedtimestamp": self.get_datetime().timestamp()
		} for p in inPairs if p.stationid]
		if params:
			stmt = insert(stations_playlists_tbl)
			self.conn.execute(stmt, params)
		return self.get_station_playlists(
			playlistsIds={st.playlistid for st in uniquePairs}
		)
	
	def get_stations_by_playlist(
		self,
		playlistId: int,
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
		.join(stations_playlists_tbl, stpl_stationFk == st_pk)\
		.where(stpl_playlistFk == playlistId)

		if self.current_user_provider.is_loggedIn():
			query = self.station_service.__build_user_rule_filters__(query, scopes)
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
		query = select(stpl_stationFk, func.count(sg_pk))\
			.join(playlists_songs_tbl, plsg_playlistFk == stpl_playlistFk)\
			.join(songs_tbl, plsg_songFk == sg_pk)\
			.where(sg_deletedTimstamp.is_(None))

		if type(stationIds) == int:
			query = query.where(stpl_stationFk == stationIds)
		elif isinstance(stationIds, Iterable):
			query = query.where(stpl_stationFk.in_(stationIds))

		if type(ownerId) == int:
			query = query.join(stations_tbl, st_pk == stpl_stationFk)\
				.where(st_ownerFk == ownerId)
		records = self.conn.execute(query)
		for row in records:
			yield cast(int,row[0]), cast(int,row[1])