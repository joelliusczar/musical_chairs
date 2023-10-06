#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
from typing import (
	Any,
	Callable,
	List,
	Optional,
	Tuple,
	Iterator,
	cast,
	Collection,
	Sequence
)
from sqlalchemy import (
	select,
	desc,
	func,
	insert,
	delete,
	update,
	literal,
	union_all
)
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.sql.functions import coalesce
from .env_manager import EnvManager
from .station_service import StationService
from .accounts_service import AccountsService
from .song_info_service import SongInfoService
from musical_chairs_libs.tables import (
	songs,
	stations,
	stations_songs as stations_songs_tbl, stsg_stationFk, stsg_songFk,
	user_action_history as user_action_history_tbl, uah_pk, uah_queuedTimestamp,
	uah_timestamp, uah_action,
	station_queue, q_userActionHistoryFk, q_songFk, q_stationFk,
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
	StationInfo,
	UserRoleDef
)
from numpy.random import (
	choice as numpy_choice #pyright: ignore [reportUnknownVariableType]
)


def choice(
	items: List[Any],
	sampleSize: int
) -> Collection[Any]:
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
		choiceSelector: Optional[Callable[[List[Any], int], Collection[Any]]]=None,
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

	def get_all_station_song_possibilities(
		self, stationPk: int
	) -> Sequence[RowMapping]:
		query = select(sg_pk, sg_path) \
			.select_from(stations) \
			.join(stations_songs_tbl, st_pk == stsg_stationFk) \
			.join(songs, sg_pk == stsg_songFk) \
			.join(station_queue, (q_stationFk == st_pk) \
				& (q_songFk == sg_pk), isouter=True) \
			.join(user_action_history_tbl, (uah_pk == q_userActionHistoryFk) &
				uah_timestamp.isnot(None),
				isouter=True
			)\
			.where(st_pk == stationPk) \
			.group_by(sg_pk, sg_path) \
			.order_by(desc(func.max(uah_queuedTimestamp))) \
			.order_by(desc(func.max(uah_timestamp)))

		rows = self.conn.execute(query).mappings().fetchall()
		return rows

	def get_random_songIds(
		self,
		stationId: int,
		deficitSize: int
	) -> Collection[int]:
		rows = self.get_all_station_song_possibilities(stationId)
		sampleSize = deficitSize if deficitSize < len(rows) else len(rows)
		songIds = [r[sg_pk] for r in rows]
		if not songIds:
			raise RuntimeError("No song possibilities were found")
		selection = self.choice(songIds, sampleSize)
		return selection

	def fil_up_queue(self, stationId: int, queueSize: int) -> None:
		queryQueueSize = select(func.count(1)).select_from(station_queue)\
			.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
			.where(uah_action == UserRoleDef.STATION_REQUEST.value)\
			.where(uah_timestamp.is_(None))\
			.where(q_stationFk == stationId)
		countRes = self.conn.execute(queryQueueSize).scalar()
		count = countRes if countRes else 0
		deficitSize = queueSize - count
		if deficitSize < 1:
			return
		songIds = self.get_random_songIds(stationId, deficitSize)
		timestamp = self.get_datetime().timestamp()
		insertedIds: list[int] = []
		for _ in songIds:
			historyInsert = insert(user_action_history_tbl)
			insertedId = self.conn.execute(historyInsert, {
					"queuedtimestamp": timestamp,
					"action": UserRoleDef.STATION_REQUEST.value,
				}).inserted_primary_key
			if insertedId:
				insertedIds.append(cast(int,insertedId[0]))
		params = [{
			"stationfk": stationId,
			"songfk": s[0],
			"useractionhistoryfk": s[1]
		} for s in zip(songIds,insertedIds)]
		queueInsert = insert(station_queue)
		self.conn.execute(queueInsert, params)

	def move_from_queue_to_history(
		self,
		stationId: int,
		songId: int,
		queueTimestamp: float
	) -> None:

		query = select(uah_pk)\
			.join(station_queue, uah_pk == q_userActionHistoryFk)\
			.where(q_stationFk == stationId)\
			.where(q_songFk == songId)\
			.where(uah_queuedTimestamp == queueTimestamp)\
			.where(uah_action == UserRoleDef.STATION_REQUEST.value)
		userActionId = self.conn.execute(query).scalar_one()
		currentTime = self.get_datetime().timestamp()

		histUpdateStmt = update(user_action_history_tbl) \
			.values(timestamp = currentTime) \
			.where(uah_pk == userActionId)
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
				uah_queuedTimestamp
			).select_from(station_queue)\
				.join(user_action_history_tbl,uah_pk == q_userActionHistoryFk)\
				.join(songs, sg_pk == q_songFk)\
				.join(albums, sg_albumFk == ab_pk, isouter=True)\
				.join(song_artist, sg_pk == sgar_songFk, isouter=True)\
				.join(artists, sgar_artistFk == ar_pk, isouter=True)\
				.join(subq, subq.c.pk == coalesce(sgar_pk, -1))\
				.where(uah_action == UserRoleDef.STATION_REQUEST.value)\
				.where(q_stationFk == stationId)\
				.where(uah_timestamp.is_(None))\
				.order_by(uah_queuedTimestamp)

		records = self.conn.execute(query).mappings()
		for row in records:
			yield SongListDisplayItem(
				id=row[sg_pk],
				name=row[sg_name],
				album=row["album"],
				artist=row["artist"],
				path=row[sg_path],
				queuedTimestamp=row[uah_queuedTimestamp]
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
		songId: int,
		stationId: int,
		userId: int
	) -> int:
		timestamp = self.get_datetime().timestamp()

		stmt = insert(user_action_history_tbl).values(
			queuedtimestamp = timestamp,
			requestedtimestamp = timestamp,
			userfk = userId,
			action = UserRoleDef.STATION_REQUEST.value,
		)
		insertedPk = self.conn.execute(stmt).inserted_primary_key
		if insertedPk:
			stmt = insert(station_queue).values(
				stationfk = stationId,
				songfk = songId,
				useractionhistoryfk = insertedPk[0]
			)
			return self.conn.execute(stmt).rowcount
		else:
			return 0

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
		query = select(func.count(1)).select_from(station_queue)\
			.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)
		if stationId:
			query = query.where(q_stationFk == stationId)
		elif stationName:
			query.join(stations, st_pk == q_stationFk)\
				.where(func.format_name_for_search(st_name)
					== SearchNameString.format_name_for_search(stationName))
		else:
			raise ValueError("Either stationName or id must be provided")
		query = query.where(uah_timestamp.is_(None))
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

		query = select(uah_pk)\
			.join(station_queue, uah_pk == q_userActionHistoryFk)\
			.where(q_stationFk == stationId)\
			.where(q_songFk == songId)\
			.where(uah_queuedTimestamp == queuedTimestamp)\
			.where(uah_action == UserRoleDef.STATION_REQUEST.value)
		userActionId = self.conn.execute(query).scalar_one()

		stmt = delete(station_queue).where(q_userActionHistoryFk == userActionId)
		delCount = self.conn.execute(stmt).rowcount
		stmt = delete(user_action_history_tbl).where(uah_pk == userActionId)
		delCount += self.conn.execute(stmt).rowcount
		return delCount == 2

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
			uah_queuedTimestamp.label("queuedtimestamp"),
			sg_name.label("name"),
			ab_name.label("album"),
			ar_name.label("artist"),
			sg_path.label("path"),
		).select_from(station_queue) \
			.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
			.join(songs, q_songFk == sg_pk) \
			.join(albums, sg_albumFk == ab_pk, isouter=True) \
			.join(song_artist, sg_pk == sgar_songFk, isouter=True) \
			.join(artists, sgar_artistFk == ar_pk, isouter=True) \
			.where(uah_timestamp.isnot(None))\
			.where(q_stationFk == stationId)\
			.order_by(desc(uah_queuedTimestamp)) \
			.offset(offset)\
			.limit(limit)
		records = self.conn.execute(query).mappings()
		for row in records:
			rules = []
			if pathRuleTree:
				rules = list(pathRuleTree.valuesFlat(cast(str, row["path"])))
			yield SongListDisplayItem(**row, rules=rules) #pyright: ignore [reportUnknownArgumentType]

	def history_count(
		self,
		stationId: int
	) -> int:
		query = select(func.count(1)).select_from(station_queue)\
			.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
			.where(q_stationFk == stationId)
		query = query.where(uah_timestamp.isnot(None))
		count = self.conn.execute(query).scalar() or 0
		return count


if __name__ == "__main__":
	pass