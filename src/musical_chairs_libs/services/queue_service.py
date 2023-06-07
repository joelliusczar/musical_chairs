#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
from typing import (
	Any,
	Callable,
	List,
	Optional,
	Tuple,
	Iterator,
	cast
)
from collections.abc import Iterable
from sqlalchemy import (
	select,
	desc,
	func,
	insert,
	delete,
	update,
	literal, #pyright: ignore [reportUnknownVariableType]
	union_all
)
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import Row
from sqlalchemy.sql.functions import coalesce
from .env_manager import EnvManager
from .station_service import StationService
from .accounts_service import AccountsService
from .song_info_service import SongInfoService
from musical_chairs_libs.tables import (
	songs,
	stations,
	stations_songs as stations_songs_tbl, stsg_stationFk, stsg_songFk,
	station_queue, q_songFk, q_queuedTimestamp, q_stationFk, q_playedTimestamp,
	albums,
	artists,
	song_artist,
	sgar_pk, sgar_songFk, sgar_artistFk, sgar_isPrimaryArtist,
	sg_pk, sg_name, sg_path, sg_albumFk,
	st_pk, st_name,
	ar_pk, ar_name,
	ab_pk, ab_name
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	SongListDisplayItem,
	CurrentPlayingInfo,
	get_datetime,
	SearchNameString,
	StationInfo
)
from numpy.random import (
	choice as numpy_choice #pyright: ignore [reportUnknownVariableType]
)


def choice(
	items: List[Any],
	sampleSize: int
) -> Iterable[Any]:
	aSize = len(items)
	pSize = len(items) + 1
	# the sum of weights needs to equal 1
	weights = [2 * (float(n) / (pSize * aSize)) for n in range(1, pSize)]
	return numpy_choice(items, sampleSize, p = weights, replace=False).tolist()

class QueueService:

	def __init__(
		self,
		conn: Optional[Connection]=None,
		stationService: Optional[StationService]=None,
		accountService: Optional[AccountsService]=None,
		songInfoService: Optional[SongInfoService]=None,
		choiceSelector: Optional[Callable[[List[Any], int], Iterable[Any]]]=None,
		envManager: Optional[EnvManager]=None
	) -> None:
			if not conn:
				if not envManager:
					envManager = EnvManager()
				conn = envManager.get_configured_db_connection()
			if not stationService:
				stationService = StationService(conn)
			if not accountService:
				accountService = AccountsService(conn, envManager)
			if not songInfoService:
				songInfoService = SongInfoService(conn)
			if not choiceSelector:
				choiceSelector = choice
			self.conn = conn
			self.station_service = stationService
			self.account_service = accountService
			self.song_info_service = songInfoService
			self.choice = choiceSelector
			self.get_datetime = get_datetime

	def get_all_station_song_possibilities(self, stationPk: int) -> List[Row]:
		query = select(sg_pk, sg_path) \
			.select_from(stations) \
			.join(stations_songs_tbl, st_pk == stsg_stationFk) \
			.join(songs, sg_pk == stsg_songFk) \
			.join(station_queue, (q_stationFk == st_pk) \
				& (q_songFk == sg_pk) & q_playedTimestamp.isnot(None), isouter=True) \
			.where(st_pk == stationPk) \
			.group_by(sg_pk, sg_path) \
			.order_by(desc(func.max(q_queuedTimestamp))) \
			.order_by(desc(func.max(q_playedTimestamp)))

		rows: List[Row] = self.conn.execute(query).fetchall()
		return rows

	def get_random_songIds(
		self,
		stationId: int,
		deficitSize: int
	) -> Iterable[int]:
		rows = self.get_all_station_song_possibilities(stationId)
		sampleSize = deficitSize if deficitSize < len(rows) else len(rows)
		songIds = [r["pk"] for r in rows]
		if not songIds:
			raise RuntimeError("No song possibilities were found")
		selection = self.choice(songIds, sampleSize)
		return selection

	def fil_up_queue(self, stationId: int, queueSize: int) -> None:
		queryQueueSize: str = select(func.count(1)).select_from(station_queue)\
			.where(q_playedTimestamp.is_(None))\
			.where(q_stationFk == stationId)
		countRes = self.conn.execute(queryQueueSize).scalar()
		count: int = countRes if countRes else 0
		deficitSize = queueSize - count
		if deficitSize < 1:
			return
		songIds = self.get_random_songIds(stationId, deficitSize)
		timestamp = self.get_datetime().timestamp()
		params = [{
			"stationFk": stationId,
			"songFk": s,
			"queuedTimestamp": timestamp
		} for s in songIds]
		queueInsert = insert(station_queue)
		self.conn.execute(queueInsert, params)

	def move_from_queue_to_history(
		self,
		stationId: int,
		songId: int,
		queueTimestamp: float
	) -> None:

		currentTime = self.get_datetime().timestamp()

		histUpdateStmt = update(station_queue) \
			.values(playedTimestamp = currentTime) \
			.where(q_stationFk == stationId) \
			.where(q_songFk== songId) \
			.where(q_queuedTimestamp== queueTimestamp)
		self.conn.execute(histUpdateStmt)

	def is_queue_empty(self, stationId: int) -> bool:
		res = self.queue_count(stationId)
		return res < 1

	def get_queue_for_station(
		self,
		stationId: int,
		limit: Optional[int]=None
	) -> Iterator[SongListDisplayItem]:
		primaryArtistGroupQuery = select(
			func.max(sgar_pk).label("pk"),
			func.max(sgar_isPrimaryArtist).label("isPrimary"),
			sgar_songFk.label("songFk")
		).group_by(sgar_songFk)
		#have a default row for songs without any songArtists to match against
		defaultRow = select(literal(-1), literal(None), literal(None))

		subq = union_all(primaryArtistGroupQuery, defaultRow).subquery()

		query = select(
				sg_pk,
				sg_path,
				sg_name,
				ab_name.label("album"),
				ar_name.label("artist"),
				q_queuedTimestamp
			).select_from(station_queue)\
				.join(songs, sg_pk == q_songFk)\
				.join(albums, sg_albumFk == ab_pk, isouter=True)\
				.join(song_artist, sg_pk == sgar_songFk, isouter=True)\
				.join(artists, sgar_artistFk == ar_pk, isouter=True)\
				.join(subq, subq.c.pk == coalesce(sgar_pk, -1))\
				.where(q_stationFk == stationId)\
				.where(q_playedTimestamp.is_(None))\
				.order_by(q_queuedTimestamp)

		records = self.conn.execute(query).fetchall()
		for row in cast(Iterable[Row],records):
			yield SongListDisplayItem(
				id=cast(int,row[sg_pk]),
				name=cast(str,row[sg_name]),
				album=cast(str,row["album"]),
				artist=cast(str,row["artist"]),
				path=cast(str,row[sg_path]),
				queuedTimestamp=cast(float,row[q_queuedTimestamp])
			)

	def pop_next_queued(
		self,
		stationId: int,
		queueSize: int=50
	) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
		if not stationId:
			raise ValueError("Station Id must be provided")
		if self.is_queue_empty(stationId):
			self.fil_up_queue(stationId, queueSize + 1)
		results = self.get_queue_for_station(stationId, limit=1)
		queueItem = next(results)
		self.move_from_queue_to_history(
			stationId,
			queueItem.id,
			queueItem.queuedTimestamp
		)
		self.fil_up_queue(stationId, queueSize)
		return (
			queueItem.path,
			queueItem.name,
			queueItem.album,
			queueItem.artist
		)

	def _add_song_to_queue(
		self,
		songPk: int,
		stationPk: int,
		userPk: int
	) -> int:
		timestamp = self.get_datetime().timestamp()

		stmt = insert(station_queue).values(
			stationFk = stationPk,
			songFk = songPk,
			queuedTimestamp = timestamp,
			requestedTimestamp = timestamp,
			requestedByUserFk = userPk
		)
		return self.conn.execute(stmt).rowcount #pyright: ignore [reportUnknownVariableType]

	def add_song_to_queue(self,
		songId: int,
		station: StationInfo,
		user: AccountInfo
	):
		songInfo = self.song_info_service.song_info(songId)
		songName = songInfo.name if songInfo else "Song"
		if station and\
			self.station_service.can_song_be_queued_to_station(
				songId,
				station.id
			):
			self._add_song_to_queue(songId, station.id, user.id)
			return
		raise LookupError(f"{songName} cannot be added to {station.name}")

	def queue_count(
		self,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None
	) -> int:
		query = select(func.count(1)).select_from(station_queue)
		if stationId:
			query = query.where(q_stationFk == stationId)
		elif stationName:
			query.join(stations, st_pk == q_stationFk)\
				.where(func.format_name_for_search(st_name)
					== SearchNameString.format_name_for_search(stationName))
		else:
			raise ValueError("Either stationName or id must be provided")
		query = query.where(q_playedTimestamp.is_(None))
		count = self.conn.execute(query).scalar() or 0
		return count

	def get_now_playing_and_queue(
		self,
		stationId: int,
		user: Optional[AccountInfo]=None
	) -> CurrentPlayingInfo:
		pathRuleTree = None
		if user:
			pathRuleTree = self.song_info_service.get_rule_path_tree(user)
		queue = []
		for song in self.get_queue_for_station(stationId):
			if pathRuleTree:
				song.rules = list(pathRuleTree.valuesFlat(song.path))
			queue.append(song)
		playing = next(self.get_history_for_station(stationId, limit=1), None)
		if pathRuleTree and playing:
				playing.rules = list(pathRuleTree.valuesFlat(playing.path))
		return CurrentPlayingInfo(
			nowPlaying=playing,
			items=queue,
			totalRows=self.queue_count(stationId),
			stationRules=[]
		)

	def _remove_song_from_queue(self,
		songId: int,
		queuedTimestamp: float,
		stationId: int
	) -> bool:
		stmt = delete(station_queue)

		if type(stationId) == int:
			stmt = stmt
		else:
			raise ValueError("Either station id must be provided")

		stmt = stmt.where(q_songFk == songId)\
			.where(q_queuedTimestamp == queuedTimestamp)\
			.where(q_stationFk == stationId)
		return cast(int, self.conn.execute(stmt).rowcount) > 0

	def remove_song_from_queue(self,
		songId: int,
		queuedTimestamp: float,
		stationId: int
	) -> Optional[CurrentPlayingInfo]:
		if not self._remove_song_from_queue(
			songId,
			queuedTimestamp,
			stationId
		):
			return None
		return self.get_now_playing_and_queue(stationId)

	def get_history_for_station(
		self,
		stationId: int,
		page: int = 0,
		limit: Optional[int]=50,
		user: Optional[AccountInfo]=None
	) -> Iterator[SongListDisplayItem]:
		offset = page * limit if limit else 0
		pathRuleTree = None
		if user:
			pathRuleTree = self.song_info_service.get_rule_path_tree(user)

		query = select(
			sg_pk.label("id"),
			q_queuedTimestamp.label("queuedTimestamp"),
			sg_name.label("name"),
			ab_name.label("album"),
			ar_name.label("artist"),
			sg_path.label("path"),
		).select_from(station_queue) \
			.join(songs, q_songFk == sg_pk) \
			.join(albums, sg_albumFk == ab_pk, isouter=True) \
			.join(song_artist, sg_pk == sgar_songFk, isouter=True) \
			.join(artists, sgar_artistFk == ar_pk, isouter=True) \
			.where(q_playedTimestamp.isnot(None))\
			.where(q_stationFk == stationId)\
			.order_by(desc(q_queuedTimestamp)) \
			.offset(offset)\
			.limit(limit)
		records = self.conn.execute(query)
		for row in records: #pyright: ignore [reportUnknownVariableType]
			rules = []
			if pathRuleTree:
				rules = list(pathRuleTree.valuesFlat(cast(str, row["path"])))
			yield SongListDisplayItem(**row, rules=rules) #pyright: ignore [reportUnknownArgumentType]

	def history_count(
		self,
		stationId: int
	) -> int:
		query = select(func.count(1)).select_from(station_queue)\
			.where(q_stationFk == stationId)
		query = query.where(q_playedTimestamp.isnot(None))
		count = self.conn.execute(query).scalar() or 0
		return count


if __name__ == "__main__":
	pass