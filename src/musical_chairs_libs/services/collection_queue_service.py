from collections import defaultdict
from itertools import groupby
from musical_chairs_libs.dtos_and_utilities import (
	ActionRule,
	clean_search_term_for_like,
	get_datetime,
	logging,
	StationInfo,
	UserRoleDef,
	RulePriorityLevel,
	CatalogueItem,
	CurrentPlayingInfo,
	OwnerInfo,
	QueueMetrics,
	QueuePossibility,
	SimpleQueryParameters,
	UserRoleSphere,
	StationTypes,
	StreamQueuedItem,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	StationsSongsActions,
	StationRequestTypes,
)
from musical_chairs_libs.protocols import SongPopper, RadioPusher
from musical_chairs_libs.tables import (
	albums as albums_tbl, ab_pk, ab_name, ab_year, ab_albumArtistFk, ab_ownerFk,
	artists as artists_tbl, ar_pk, ar_name,
	songs as songs_tbl, sg_name, sg_disc, sg_pk, sg_albumFk, sg_deletedTimstamp, sg_path, 
	sg_internalpath,
	stations as stations_tbl, st_pk, st_typeid, st_playnum,
	station_queue as station_queue_tbl,
	station_queue as station_queue_tbl, 
	sg_trackNum,
	playlists as playlists_tbl, pl_pk, pl_name, pl_ownerFk, 
	pl_lastmodifiedtimestamp,
	playlists_songs as playlists_songs_tbl, plsg_playlistFk, plsg_songFk,
	plsg_lexorder,
	stations_albums as stations_albums_tbl, stab_albumFk, stab_stationFk,
	stab_lastplayednum,
	stations_playlists as stations_playlists_tbl, stpl_playlistFk, stpl_stationFk,
	stpl_lastplayednum,
	users as users_tbl, u_pk, u_username, u_displayName,
	song_artist as song_artists_tbl, sgar_isPrimaryArtist, sgar_artistFk, 
	sgar_songFk
)
from .current_user_provider import CurrentUserProvider
from .queue_service import QueueService
from numpy.random import (
	choice as numpy_choice #pyright: ignore [reportUnknownVariableType]
)
from sqlalchemy import (
	desc,
	select,
	literal as dbLiteral,
	insert,
	func,
	Label,
	update,
	union_all,
	RowMapping
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Connection
from typing import (
	Any,
	Callable,
	Optional,
	cast,
	Collection,
	Sequence,
	Set,
	Tuple,
)

def choice(
	items: Sequence[Any],
	sampleSize: int,
	weights: Sequence[float]
) -> Collection[Any]:
	# the sum of weights needs to equal 1
	return numpy_choice(
		items,
		sampleSize,
		p = cast(Any,weights),
		replace=False
	).tolist()


class CollectionQueueService(SongPopper, RadioPusher):

	def __init__(
		self,
		conn: Connection,
		queueService: QueueService,
		currentUserProvider: CurrentUserProvider,
		choiceSelector: Optional[
			Callable[[Sequence[Any], int, Sequence[float]], Collection[Any]]
		]=None,
		queueSize: int = 3
	) -> None:
			if not conn:
				raise RuntimeError("No connection provided")
			if not choiceSelector:
				choiceSelector = choice
			self.conn = conn
			self.queue_service = queueService
			self.choice = choiceSelector
			self.get_datetime = get_datetime
			self.current_user_provider = currentUserProvider
			self.queue_size = queueSize



	def get_all_station_possibilities(
		self,
		stationid: int
	) -> Sequence[QueuePossibility]:
		
		albumQuery = select(
			stab_albumFk.label("key"),
			stab_lastplayednum.label("lastplayednum"),
			st_playnum.label("playnum"),
			dbLiteral(StationRequestTypes.ALBUM.lower()).label("itemtype")
		) \
			.select_from(stations_tbl) \
			.join(stations_albums_tbl, st_pk == stab_stationFk) \
			.where(st_pk == stationid)
		
		playlistQuery = select(
			stpl_playlistFk.label("key"),
			stpl_lastplayednum.label("lastplayednum"),
			st_playnum.label("playnum"),
			dbLiteral(StationRequestTypes.PLAYLIST.lower()).label("itemtype")
		) \
			.select_from(stations_tbl) \
			.join(stations_playlists_tbl, st_pk == stpl_stationFk) \
			.where(st_pk == stationid)

		sub = union_all(
			albumQuery,
			playlistQuery
		).cte()

		query = select(
			sub.c.key,
			sub.c.lastplayednum, 
			sub.c.playnum,
			sub.c.itemtype
		)\
			.order_by(
				desc(sub.c.lastplayednum),
				func.random()
			)
		rows = self.conn.execute(query).fetchall()

		return [QueuePossibility(
			itemId=row[0],
			lastplayednum=row[1],
			playnum=row[2],
			itemtype=row[3]
		) for row in rows]


	def get_random_collectionIds(
		self,
		stationId: int,
		metrics: QueueMetrics
	) -> Collection[Tuple[int, str]]:
		def weigh(n: float) -> float:
			return n * n * n
		rows = self.get_all_station_possibilities(stationId)
		room = min(len(rows), metrics.maxSize)
		if not room:
			raise RuntimeError("No radio possibilities were found")
		deficitSize = room - metrics.queued - metrics.loaded
		if deficitSize < 1:
			return []
		mostRecentDraw = rows[0].playnum or 1 \
			if len(rows) > 1 else 1
		ages = [(mostRecentDraw - r.lastplayednum) for r in rows]
		total = sum(
			(weigh(a) for a in ages)
		)
		weights = [weigh(a)/total for a in ages]
		zeroCount = sum(1 for w in weights if w == 0)
		sampleSize = deficitSize if deficitSize < len(rows) - zeroCount \
			else len(rows) - zeroCount
		ids = [(r.itemId, r.itemtype) for r in rows]
		if not ids:
			raise RuntimeError("No playlist possibilities were found")
		tupleMap = {f"{t[1]}{t[0]}":t for t in ids}
		try:
			selection = self.choice(
				[f"{t[1]}{t[0]}" for t in ids],
				sampleSize,
				weights
			)
			return [tupleMap[k] for k in selection]
		except:
			logging.radioLogger.error(rows)
			logging.radioLogger.error(ages)
			logging.radioLogger.error(weights)
			logging.radioLogger.error(sum(weights))
			raise


	def queue_count(
		self,
		alreadyQueued: list[StreamQueuedItem]
	) -> int:

		albumItems = (
			a for a in alreadyQueued\
			if a.itemtype == StationRequestTypes.ALBUM.lower()
		)

		playListItems = (
			a for a in alreadyQueued\
			if a.itemtype == StationRequestTypes.PLAYLIST.lower()
		)

		albumCount = sum(1 for _ in groupby(albumItems, lambda q: q.parentkey))
		playlistCount = sum(
			1 for _ in groupby(playListItems, lambda q: q.parentkey)
		)

		return albumCount + playlistCount


	def load_current_queue(self, station: StationInfo):
		return self.queue_service.load_current_queue(station)


	def get_album_songs_map(
		self,
		albumIds: list[int]
	):
		groupColumns: list[Label[Any]] = [
			sg_pk.label("id"),
			sg_name.label("name"),
			sg_albumFk.label("album.id"),
			ab_name.label("album.name"),
			sg_disc.label("discnum"),
			sg_trackNum.label("tracknum"),
			sg_path.label("treepath"),
			sg_internalpath.label("internalpath"),
			ar_name.label("artist.name"),
		]

		songAlbumQuery = songs_tbl\
			.select()\
			.outerjoin(albums_tbl, sg_albumFk == ab_pk)\
			.outerjoin(song_artists_tbl, sg_pk == sgar_songFk)\
			.outerjoin(artists_tbl, sgar_artistFk == ar_pk)\
			.where(sg_albumFk.in_(albumIds))\
			.where(sg_deletedTimstamp.is_(None))\
			.with_only_columns(
				*groupColumns,
				func.row_number().over(
					partition_by=sg_pk,
					order_by=(desc(sgar_isPrimaryArtist), desc(ar_pk))
				).label("artistrank")
			)\
			.cte()

		albumSongTuples = self.conn.execute(
			songAlbumQuery.select().where(songAlbumQuery.c.artistrank == 1)
		).mappings().fetchall()
		albumsMap: defaultdict[int, list[RowMapping]] = defaultdict(list)
		for row in albumSongTuples:
			albumsMap[row["album.id"]].append(row)

		return albumsMap


	def get_playlist_songs_map(
		self,
		playlistIds: list[int]
	):
		groupColumns: list[Label[Any]] = [
			sg_pk.label("id"),
			sg_name.label("name"),
			plsg_playlistFk.label("playlist.id"),
			plsg_lexorder.label("playlist.lexorder"),
			ab_name.label("album.name"),
			sg_path.label("treepath"),
			sg_internalpath.label("internalpath"),
			ar_name.label("artist.name"),
		]

		songPlaylistQuery = songs_tbl\
			.select()\
			.join(playlists_songs_tbl,sg_pk == plsg_songFk)\
			.outerjoin(albums_tbl, sg_albumFk == ab_pk)\
			.outerjoin(song_artists_tbl, sg_pk == sgar_songFk)\
			.outerjoin(artists_tbl, sgar_artistFk == ar_pk)\
			.where(plsg_playlistFk.in_(playlistIds))\
			.where(sg_deletedTimstamp.is_(None))\
			.with_only_columns(
				*groupColumns,
				func.row_number().over(
					partition_by=sg_pk,
					order_by=(desc(sgar_isPrimaryArtist), desc(ar_pk))
				).label("artistrank")
			)\
			.cte()
		playlistSongTuples = self.conn.execute(
			songPlaylistQuery.select().where(songPlaylistQuery.c.artistrank == 1)
		).mappings()
		playlistsMap: defaultdict[int, list[RowMapping]] = defaultdict(list)
		for row in playlistSongTuples:
			playlistsMap[row["playlist.id"]].append(row)

		return playlistsMap


	def fil_up_queue(
		self,
		station: StationInfo,
		metrics: QueueMetrics,
		alreadyQueued: list[StreamQueuedItem] | None = None
	):
		
		if alreadyQueued is None:
			alreadyQueued = []

		metrics.queued = self.queue_count(alreadyQueued)

		collectionIds = self.get_random_collectionIds(station.id, metrics)

		if not collectionIds:
			self.queue_service.replace_queue_file(station, alreadyQueued)
			return

		albumIds = [
			a[0] for a in collectionIds 
			if a[1] == StationRequestTypes.ALBUM.lower()
		]

		albumsMap = self.get_album_songs_map(albumIds)

		playlistIds = [
			a[0] for a in collectionIds 
			if a[1] == StationRequestTypes.PLAYLIST.lower()
		]

		playlistsMap = self.get_playlist_songs_map(playlistIds)

		requests: list[StreamQueuedItem] = []
		
		def albumSortKey(r: RowMapping):
			return (r["discnum"] or 0,r["tracknum"])

		def playlistSortKey(r: RowMapping):
			return r["playlist.lexorder"] or b""

		for i, collectionId in enumerate(collectionIds):
			
			if collectionId[1] == StationRequestTypes.ALBUM.lower():
				sortKey = albumSortKey
				collectionMap = albumsMap
				stationCollectionTbl = stations_albums_tbl
				stationFkCol = stab_stationFk
				collectionFkCol = stab_albumFk
			else: 
				sortKey = playlistSortKey
				collectionMap = playlistsMap
				stationCollectionTbl = stations_playlists_tbl
				stationFkCol = stpl_stationFk
				collectionFkCol = stpl_playlistFk

			lastPlayedUpdate = update(stationCollectionTbl)\
				.values(lastplayednum = station.playnum + i + 1) \
				.where(stationFkCol == station.id)\
				.where(collectionFkCol == collectionId[0])
			self.conn.execute(lastPlayedUpdate)

			sortedSongs = sorted(
				collectionMap[collectionId[0]],
				key=sortKey
			)
			requests.extend(
				StreamQueuedItem(
					id=r["id"],
					name=r["name"],
					itemtype=collectionId[1].lower(),
					parentkey=collectionId[0],
					album=r["album.name"],
					artist=r["artist.name"],
					queuedtimestamp=self.get_datetime().timestamp(),
					treepath=r["treepath"],
					internalpath=r["internalpath"],
				) for r in sortedSongs
			)

		self.queue_service.queue_insert_songs(
			alreadyQueued,
			requests,
			station
		)

		self.queue_service.replace_queue_file(station, alreadyQueued)

		#need to save again separately because
		#queue_service.queue_insert_songs is going to save
		#based on song count which will cause playnum to go wonky
		self.queue_service.__add_to_station_playnum__(
			station,
			len(collectionIds)
		)


	def __add_album_to_queue__(
		self,
		itemId: int,
		station: StationInfo,
		stationItemType: StationRequestTypes=StationRequestTypes.PLAYLIST
	):
		if station and\
			self.__can_album_be_queued_to_station__(
				itemId,
				station.id,
			):
			query = select(
				sg_pk.label("id"),
				sg_name.label("name"),
				ab_name.label("album.name"),
				sg_path.label("treepath"),
				sg_internalpath.label("internalpath"),
				ar_name.label("artist.name"),
				func.row_number().over(
					partition_by=sg_pk,
					order_by=(desc(sgar_isPrimaryArtist), desc(ar_pk))
				).label("artistrank")
				)\
				.outerjoin(albums_tbl, sg_albumFk == ab_pk)\
				.outerjoin(song_artists_tbl, sgar_songFk == sgar_artistFk)\
				.outerjoin(artists_tbl, sgar_artistFk == ar_pk)\
				.where(sg_deletedTimstamp.is_(None))\
				.where(sg_albumFk == itemId)\
				.cte()
			
			rows = self.conn.execute(
				query.select().where(query.c.artistrank == 1)
			).mappings()

			alreadyQueued = [*self.queue_service.load_current_queue(station)]

			self.queue_service.queue_insert_songs(
				alreadyQueued,
				[StreamQueuedItem(
					id=r["id"],
					name=r["name"],
					itemtype=StationRequestTypes.ALBUM.lower(),
					parentkey=itemId,
					album=r["album.name"],
					artist=r["artistname"],
					queuedtimestamp=self.get_datetime().timestamp(),
					treepath=r["treepath"],
					internalpath=r["internalpath"],
				) for r in rows],
				station,
			)
			return
		raise LookupError(f"album cannot be added to {station.name}")
	

	def __add_playlist_to_queue__(
		self,
		itemId: int,
		station: StationInfo,
		stationItemType: StationRequestTypes=StationRequestTypes.PLAYLIST
	):
		if station and\
			self.__can_playlist_be_queued_to_station__(
				itemId,
				station.id
			):
			query = select(
				sg_pk.label("id"),
				sg_name.label("name"),
				ab_name.label("album.name"),
				sg_path.label("treepath"),
				sg_internalpath.label("internalpath"),
				ar_name.label("artist.name"),
				func.row_number(ar_name).over(
					partition_by=sg_pk,
					order_by=(desc(sgar_isPrimaryArtist), desc(ar_pk))
				).label("artistrank")
			)\
			.join(playlists_songs_tbl, sg_pk == plsg_songFk)\
			.outerjoin(albums_tbl, sg_albumFk == ab_pk)\
			.outerjoin(song_artists_tbl, sgar_songFk == sgar_artistFk)\
			.outerjoin(artists_tbl, sgar_artistFk == ar_pk)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(plsg_playlistFk == itemId)\
			.cte()

			rows = self.conn.execute(
				query.select().where(query.c.artistrank == 1)
			).mappings()
			alreadyQueued = [*self.queue_service.load_current_queue(station)]
			self.queue_service.queue_insert_songs(
				alreadyQueued,
				[StreamQueuedItem(
					id=r["id"],
					name=r["name"],
					itemtype=StationRequestTypes.PLAYLIST.lower(),
					parentkey=itemId,
					album=r["album.name"],
					artist=r["artistname"],
					queuedtimestamp=self.get_datetime().timestamp(),
					treepath=r["treepath"],
					internalpath=r["internalpath"],
				) for r in rows],
				station,
			)
			return
		raise LookupError(f"album cannot be added to {station.name}")


	def add_to_queue(
		self,
		itemId: int,
		station: StationInfo,
		stationItemType: StationRequestTypes=StationRequestTypes.PLAYLIST,
	):
		
		if stationItemType == StationRequestTypes.ALBUM:
			self.__add_album_to_queue__(
				itemId,
				station,
				stationItemType
			)
		elif stationItemType == StationRequestTypes.PLAYLIST:
			self.__add_playlist_to_queue__(
				itemId,
				station,
				stationItemType
			)
		return
	

	def __can_playlist_be_queued_to_station__(
		self,
		playlistId: int,
		stationId: int
	) -> bool:
		query = select(func.count(1)).select_from(stations_playlists_tbl)\
			.join(stations_tbl, stab_stationFk == st_pk)\
			.where(stab_stationFk == stationId)\
			.where(
				st_typeid == StationTypes.ALBUMS_AND_PLAYLISTS.value
			)\
			.where(stpl_playlistFk == playlistId)
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False
	

	def __can_album_be_queued_to_station__(
		self,
		albumId: int,
		stationId: int
	) -> bool:
		query = select(func.count(1)).select_from(stations_albums_tbl)\
			.join(stations_tbl, stab_stationFk == st_pk)\
			.where(stab_stationFk == stationId)\
			.where(
				st_typeid == StationTypes.ALBUMS_AND_PLAYLISTS.value
			)\
			.where(stab_albumFk == albumId)
		
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False

	
	def can_collection_be_queued_to_station(
		self,
		collectionId: int,
		stationId: int,
		stationItemType: StationRequestTypes
	) -> bool:
		if stationItemType == StationRequestTypes.ALBUM:
			return self.__can_album_be_queued_to_station__(
				collectionId, 
				stationId
			)
		if stationItemType == StationRequestTypes.PLAYLIST:
			return self.__can_playlist_be_queued_to_station__(
				collectionId,
				stationId
			)
		return False


	def pop_next_queued(
		self,
		stationId: int,
		loaded: Set[StreamQueuedItem] | None=None
	) -> StreamQueuedItem | None:
		if not stationId:
			raise ValueError("Station Id must be provided")
		
		if self.conn.closed:
			#this method will sometimes get called before the calling code realizes
			#the connection is closed
			return

		# songOffset = len(loaded) if loaded else 0
		collectionOffset = len({(l.parentkey, l.itemtype) for l in loaded})\
			if loaded else 0
		station = self.queue_service.__get_station__(stationId)
		alreadyQueued = [*self.load_current_queue(station)]

		if (len(alreadyQueued) - collectionOffset) < 1:
			metrics = QueueMetrics(
				maxSize=self.queue_size + 1,
				loaded=collectionOffset
			)
			self.fil_up_queue(station, metrics, alreadyQueued)
			self.conn.commit()


		for item in alreadyQueued:
			if loaded and item in loaded:
				continue
			return item

		raise RuntimeError("No unskipped songs available.")
	


	def move_from_queue_to_history(
		self,
		stationId: int,
		songId: int,
		queueTimestamp: float,
	) -> bool:
		station = self.queue_service.__get_station__(stationId)
		alreadyQueued = [*self.load_current_queue(station)]
		completedIdx = next(
			(i for i,e in enumerate(alreadyQueued)\
				if e.id == songId and e.queuedtimestamp == queueTimestamp
			),
			None
		)
		if completedIdx is None:
			return False
		completed = alreadyQueued[completedIdx]
		stmt = insert(station_queue_tbl).values(
			stationfk = stationId,
			songfk = songId,
			action = completed.action or StationsSongsActions.PLAYED.value,
			queuedtimestamp = completed.queuedtimestamp,
			playedtimestamp = self.get_datetime().timestamp(),
			userfk = completed.userId
		)
		try:
			self.conn.execute(stmt)
		except IntegrityError as e:
			logging.radioLogger.error(e, exc_info=True)
			return False
		alreadyQueued.pop(completedIdx)
		queueMetrics = QueueMetrics(maxSize=self.queue_size)
		self.fil_up_queue(station, queueMetrics, alreadyQueued)
		self.conn.commit()
		return completed.action != StationsSongsActions.SKIP.value


	def get_catalogue(
		self,
		stationId: int,
		queryParams: SimpleQueryParameters,
		name: str = "",
		parentname: str = "",
		creator: str = "",
	) -> Tuple[list[CatalogueItem], int]:
		offset = queryParams.page * queryParams.limit if queryParams.limit else 0
		lname = clean_search_term_for_like(name)
		lcreator = clean_search_term_for_like(creator)

		albumQuery = select(
			ab_pk.label("id"),
			ab_name.label("name"),
			ar_name.label("creator"),
			ab_year.label("year"),
			ab_ownerFk.label("ownerid"),
			u_username.label("ownerusername"),
			u_displayName.label("ownerdisplayname"),
			dbLiteral(StationRequestTypes.ALBUM.lower()).label("itemtype")
		)\
			.select_from(stations_tbl) \
			.join(stations_albums_tbl, st_pk == stab_stationFk) \
			.join(albums_tbl, stab_albumFk == ab_pk) \
			.join(artists_tbl, ab_albumArtistFk == ar_pk, isouter=True) \
			.join(users_tbl, u_pk == ab_ownerFk, isouter=True)\
			.where(st_pk == stationId)
		
		playlistQuery = select(
			pl_pk.label("id"),
			pl_name.label("name"),
			u_displayName.label("creator"),
			func.FROM_UNIXTIME(pl_lastmodifiedtimestamp, "%Y").label("year"),
			pl_ownerFk.label("ownerid"),
			u_username.label("ownerusername"),
			u_displayName.label("ownerdisplayname"),
			dbLiteral(StationRequestTypes.PLAYLIST.lower()).label("itemtype")
		)\
			.select_from(stations_tbl) \
			.join(stations_playlists_tbl, st_pk == stpl_stationFk) \
			.join(playlists_tbl, stpl_playlistFk == pl_pk) \
			.join(users_tbl, pl_ownerFk == u_pk)\
			.where(st_pk == stationId)
		
		unioned_query = union_all(albumQuery, playlistQuery)
		sub = unioned_query.cte()
		
		query = select(
			sub.c.id.label("id"),
			sub.c.name.label("name"),
			sub.c.creator.label("creator"),
			sub.c.year.label("year"),
			sub.c.ownerid.label("ownerid"),
			sub.c.ownerusername.label("ownerusername"),
			sub.c.ownerdisplayname.label("ownerdisplayname"),
			sub.c.itemtype.label("itemtype")
		)
		
		if lname:
			query = query.where(sub.c.name.like(f"%{lname}%", escape="\\"))

		if lcreator:
			query = query.where(sub.c.creator.like(f"%{lcreator}%", escape="\\"))

		limitedQuery = query\
			.offset(offset)\
			.limit(queryParams.limit)

		records = self.conn.execute(limitedQuery).mappings()

		userId = self.current_user_provider.optional_user_id()
		result = [CatalogueItem(
			id=r["id"],
			name=r["name"] or "",
			parentname="",
			creator=r["creator"] or "",
			itemtype=r["itemtype"],
			requesttypeid=StationRequestTypes.ALBUM.value \
				if r["itemtype"] == StationRequestTypes.ALBUM.lower() \
				else StationRequestTypes.PLAYLIST.value ,
			queuedtimestamp=0,
			rules=[] if not userId or r["ownerid"] != userId else [
				ActionRule(
					sphere=UserRoleSphere.Album.value,
					name=UserRoleDef.ALBUM_EDIT.value,
					priority=RulePriorityLevel.OWNER.value
				)
			] if r["itemtype"] == StationRequestTypes.ALBUM.lower()
			else [
				ActionRule(
					sphere=UserRoleSphere.Playlist.value,
					name=UserRoleDef.PLAYLIST_EDIT.value,
					priority=RulePriorityLevel.OWNER.value
				)
			],
			owner=OwnerInfo(
				id=r["ownerid"],
				username=r["ownerusername"],
				displayname=r["ownerdisplayname"]
			)
			) for r in records]
		countQuery = select(func.count(1)).select_from(sub)
		count = self.conn.execute(countQuery).scalar() or 0
		return result, count


	def remove_song_from_queue(self,
		songId: int,
		queuedTimestamp: float,
		station: StationInfo,
	) -> Optional[CurrentPlayingInfo]:
		alreadyQueued = [*self.queue_service.load_current_queue(station)]
		skipIdx = next(
			(i for i,e in enumerate(alreadyQueued)\
				if e.id == songId and e.queuedtimestamp == queuedTimestamp
			),
			None
		)
		if skipIdx is None:
			raise RuntimeError(
				f"{songId} at {queuedTimestamp} could not be found to be skipped"
			)
		alreadyQueued[skipIdx].action = StationsSongsActions.SKIP.value

		self.fil_up_queue(
			station,
			QueueMetrics(maxSize=self.queue_size),
			alreadyQueued
		)
		self.conn.commit()
		return self.queue_service.get_now_playing_and_queue(station)


	def accepted_request_types(self) -> set[StationRequestTypes]:
		return { StationRequestTypes.ALBUM, StationRequestTypes.PLAYLIST }


	def get_queue_for_station(
		self,
		stationId: int
	) -> Tuple[list[StreamQueuedItem], int]:
		return self.queue_service.get_queue_for_station(stationId)
		
	