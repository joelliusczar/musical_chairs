
from typing import (
	Iterator,
	Optional,
	Union,
	cast,
	Iterable,
	Any,
)
from musical_chairs_libs.dtos_and_utilities import (
	SavedNameString,
	SongListDisplayItem,
	ScanningSongItem,
	get_datetime,
	Lost,
	SongAboutInfo,
	SongEditInfo,
	ChangeTrackedSongInfo,
	StationSongTuple,
	SongArtistTuple,
	normalize_opening_slash,
	clean_search_term_for_like,
	PathDict,
	SimpleQueryParameters,
	SongPlaylistTuple,
	TrackListing,
)
from .path_rule_service import PathRuleService
from .playlists_songs_service import PlaylistsSongsService
from sqlalchemy import (
	select,
	update,
)
from sqlalchemy.sql.expression import (
	Select,
)
from sqlalchemy.engine import Connection
from itertools import chain
from musical_chairs_libs.tables import (
	albums as albums_tbl,
	song_artist as song_artist_tbl,
	artists as artists_tbl,
	songs as songs_tbl,
	stations_songs as stations_songs_tbl, stsg_songFk, stsg_stationFk,
	stations as stations_tbl, st_name, st_pk, st_displayName, st_ownerFk,
	st_requestSecurityLevel, st_viewSecurityLevel,
	sg_pk, sg_name, sg_path, sg_trackNum,
	ab_name, ab_pk, ab_albumArtistFk, ab_year, ab_ownerFk,
	ar_name, ar_pk, ar_ownerFk,
	sg_albumFk, sg_bitrate,sg_comment, sg_disc, sg_duration, sg_explicit,
	sg_genre, sg_lyrics, sg_sampleRate, sg_track, sg_internalpath,
	sg_deletedTimstamp,
	sgar_isPrimaryArtist, sgar_songFk, sgar_artistFk,
	users as user_tbl,
	playlists as playlists_tbl, pl_pk, pl_name, pl_viewSecurityLevel,
	pl_description, pl_ownerFk,
	playlists_songs as playlists_songs_tbl, plsg_songFk, plsg_playlistFk

)
from .current_user_provider import CurrentUserProvider
from .song_artist_service import SongArtistService
from .stations_songs_service import StationsSongsService

album_artist = artists_tbl.alias("albumartist")
album_artist_id = album_artist.c.pk
album_artist_owner_id = album_artist.c.ownerfk
album_owner = user_tbl.alias("albumowner")
album_owner_id = album_owner.c.pk
album_artist_owner = user_tbl.alias("albumartistowner")
album_artist_owner_user_id = album_artist_owner.c.pk
artist_owner = user_tbl.alias("artistowner")
artist_owner_id = artist_owner.c.pk
station_owner = user_tbl.alias("stationowner")
station_owner_id = station_owner.c.pk
playlist_owner = user_tbl.alias("playlistowner")
playlist_owner_id = playlist_owner.c.pk


 
class SongInfoService:

	def __init__(
		self,
		conn: Connection,
		currentUserProvider: CurrentUserProvider,
		pathRuleService: PathRuleService,
		songArtistService: Optional[SongArtistService]=None,
		stationsSongsService: Optional[StationsSongsService]=None,
		playlistsSongsService: Optional[PlaylistsSongsService]=None
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		if not songArtistService:
			songArtistService = SongArtistService(conn, currentUserProvider)
		if not stationsSongsService:
			stationsSongsService = StationsSongsService(conn, currentUserProvider)
		if not playlistsSongsService:
			playlistsSongsService = PlaylistsSongsService(
				conn,
				currentUserProvider,
				pathRuleService
			)
		self.path_rule_service = pathRuleService
		self.song_artist_service = songArtistService
		self.stations_songs_service = stationsSongsService
		self.playlists_songs_service = playlistsSongsService
		self.current_user_provider = currentUserProvider
		self.get_datetime = get_datetime


	def song_info(self, songPk: int) -> Optional[SongListDisplayItem]:
		query = select(
			sg_pk,
			sg_name,
			sg_path,
			sg_internalpath,
			ab_name.label("album"),
			ar_name.label("artist")
		)\
			.select_from(songs_tbl)\
			.join(albums_tbl, sg_albumFk == ab_pk, isouter=True)\
			.join(song_artist_tbl, sg_pk == sgar_songFk, isouter=True)\
			.join(artists_tbl, sgar_artistFk == ar_pk, isouter=True)\
			.where(sg_pk == songPk)\
			.where(sg_deletedTimstamp.is_(None))\
			.limit(1)
		row = self.conn.execute(query).mappings().fetchone()
		if not row:
			return None
		return SongListDisplayItem(
			id=row[sg_pk],
			path=row[sg_path],
			internalpath=row[sg_internalpath],
			name=row[sg_name],
			album=row["album"],
			artist=row["artist"],
			queuedtimestamp=0
		)


	def get_song_refs(
		self,
		songName: Union[Optional[str], Lost]=Lost(),
		page: int=0,
		pageSize: Optional[int]=None,
	) -> Iterator[ScanningSongItem]:
		query = select(
			sg_pk,
			sg_path,
			sg_name
		).select_from(songs_tbl)\
			.where(sg_deletedTimstamp.is_(None))
		if type(songName) is str or songName is None:
			#allow null through
			savedName = SavedNameString.format_name_for_save(songName) if songName\
				else None
			query = query.where(sg_name == savedName)
		if pageSize:
			offset = page * pageSize
			query = query.limit(pageSize).offset(offset)
		records = self.conn.execute(query).mappings()
		for row in records:
			yield ScanningSongItem(
					id=row[sg_pk],
					path=row[sg_path],
					name=SavedNameString.format_name_for_save(row[sg_name])
				)


	def get_songIds(
		self,
		page: int = 0,
		pageSize: Optional[int]=None,
		stationKey: Union[int, str, None]=None,
		songIds: Optional[Iterable[int]]=None
	) -> Iterator[int]:
		offset = page * pageSize if pageSize else 0
		query = select(sg_pk).select_from(songs_tbl)\
			.where(sg_deletedTimstamp.is_(None))
		#add joins
		if stationKey:
			query = query.join(stations_songs_tbl, stsg_songFk == sg_pk)
			if type(stationKey) == int:
				query = query.where(stsg_stationFk == stationKey)
			elif type(stationKey) is str:
				lStationKey = stationKey.replace("_","\\_").replace("%","\\%")
				query = query.join(stations_tbl, stsg_stationFk == st_pk)
				query = query.join(stations_tbl, st_pk == stsg_stationFk).where(
					st_name.like(f"%{lStationKey}%")
				)
		if songIds:
			query = query.where(sg_pk.in_(songIds))
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query).mappings()
		yield from (cast(int, row["pk"]) for row in records)


	def get_songs_for_edit(
		self,
		songIds: Iterable[int],
	) -> Iterator[SongEditInfo]:
		yield from self.get_all_songs(
			songIds=songIds,
			queryParams=SimpleQueryParameters()
		)


	def update_track_nums(self, tracklistings: dict[int, TrackListing]):
		for id, listing in tracklistings.items():
			stmt = update(songs_tbl)\
				.values(tracknum = listing.tracknum)\
				.where(sg_pk == id)
			self.conn.execute(stmt)


	def save_songs(
		self,
		ids: Iterable[int],
		songInfo: ChangeTrackedSongInfo,
	) -> Iterator[SongEditInfo]:
		if not ids:
			return iter([])
		if not songInfo:
			return self.get_songs_for_edit(ids, user)
		ids = list(ids)
		user = self.current_user_provider.current_user()
		if not songInfo.touched:
			songInfo.touched = {f for f in SongAboutInfo.model_fields}
		songInfo.name = str(SavedNameString(songInfo.name))
		songInfoDict = songInfo.model_dump()
		songInfoDict.pop("artists", None)
		songInfoDict.pop("primaryartist", None)
		songInfoDict.pop("tags", None)
		songInfoDict.pop("id", None)
		songInfoDict.pop("album", None)
		songInfoDict.pop("stations", None)
		songInfoDict.pop("playlists", None)
		songInfoDict.pop("covers", None)
		songInfoDict.pop("touched", None)
		songInfoDict.pop("trackinfo", None)
		songInfoDict["albumfk"] = songInfo.album.id if songInfo.album else None
		songInfoDict["lastmodifiedbyuserfk"] = user.id
		songInfoDict["lastmodifiedtimestamp"] = self.get_datetime().timestamp()
		if "album" in songInfo.touched:
			songInfo.touched.add("albumfk")
		if any(k for k in songInfoDict.keys() if k in songInfo.touched):
			stmt = update(songs_tbl).values(
				**{k:v for k,v in songInfoDict.items() if k in songInfo.touched}
			)\
				.where(sg_deletedTimstamp.is_(None))\
				.where(sg_pk.in_(ids))
			self.conn.execute(stmt)

		if "artists" in songInfo.touched or "primaryartist" in songInfo.touched:
			self.song_artist_service.link_songs_with_artists(
				chain(
					(SongArtistTuple(sid, a.id if a else None) for a 
						in songInfo.artists or [None] * len(ids)
						for sid in ids
					) if "artists" in songInfo.touched else (),
					#we can't use allArtists here bc we need the primaryartist selection
					(SongArtistTuple(sid, songInfo.primaryartist.id, True) for sid in ids)
						if "primaryartist" in
						songInfo.touched and songInfo.primaryartist else ()
				),
			)
		if "stations" in songInfo.touched:
			self.stations_songs_service.link_songs_with_stations(
				(StationSongTuple(sid, t.id if t else None) 
					for t in (songInfo.stations or [None] * len(ids)) for sid in ids),
			)
		if "playlists" in songInfo.touched:
			self.playlists_songs_service.link_songs_with_playlists(
				(SongPlaylistTuple(sid, p.id if p else None) 
					for p in (songInfo.playlists or [None] * len(ids)) for sid in ids),
			)
		if "trackinfo" in songInfo.touched:
			self.update_track_nums(songInfo.trackinfo)
		self.conn.commit()
		if len(ids) < 2:
			yield from self.get_songs_for_edit(ids)
		else:
			fetched = self.get_songs_for_multi_edit(ids)
			if fetched:
				yield fetched


	def get_songs_for_multi_edit(
		self,
		songIds: Iterable[int],
	) -> Optional[SongEditInfo]:
		if not songIds:
			return None
		commonSongInfo = None
		touched = {f for f in SongAboutInfo.model_fields }
		removedFields: set[str] = set()
		rules = None
		trackInfo: dict[int, TrackListing] = {}
		for songInfo in self.get_songs_for_edit(songIds):
			if rules is None: #empty set means no permissions. Don't overwrite
				rules = set(songInfo.rules)
			else:
				# only keep the set of rules that are common to
				# each song
				rules = rules & set(songInfo.rules)
			trackInfo[songInfo.id] = TrackListing(
				name=songInfo.name,
				tracknum=songInfo.tracknum,
				track=songInfo.track
			) 
			songInfoDict = songInfo.model_dump()
			if not commonSongInfo:
				commonSongInfo = songInfoDict
				continue
			for field in touched:
				isUniqueField = field in { "touched" }
				if isUniqueField or songInfoDict[field] != commonSongInfo[field]:
					removedFields.add(field)
					commonSongInfo.pop(field, None)
			touched -= removedFields
			removedFields.clear()
		if commonSongInfo:
			commonSongInfo["id"] = 0
			commonSongInfo["name"] = ""
			commonSongInfo["path"] = ""
			commonSongInfo["internalpath"] = ""
			commonSongInfo["rules"] = list(rules or [])
			commonSongInfo["touched"] = touched
			commonSongInfo["trackinfo"] = trackInfo
			return SongEditInfo(
				**commonSongInfo
			)
		else:
			return SongEditInfo(
				id=0,
				name="Missing",
				path="", 
				internalpath="",
				touched=touched
			)


	def full_song_base_query(
		self,
		stationId: Optional[int]=None,
		song: str = "",
		songIds: Optional[Iterable[int]]=None,
		album: str = "",
		albumId: Optional[int]=None,
		artist: str = "",
		artistId: Optional[int]=None
	) -> Select[Any]:

		query = songs_tbl\
				.select()\
				.outerjoin(song_artist_tbl, sg_pk == sgar_songFk)\
				.outerjoin(artists_tbl, ar_pk == sgar_artistFk)\
				.outerjoin(albums_tbl, sg_albumFk == ab_pk)\
				.outerjoin(stations_songs_tbl, sg_pk == stsg_songFk)\
				.outerjoin(stations_tbl, stsg_stationFk ==  st_pk)\
				.outerjoin(album_owner, album_owner_id == ab_ownerFk) \
				.outerjoin(artist_owner, artist_owner_id ==  ar_ownerFk)\
				.outerjoin(station_owner, station_owner_id == st_ownerFk)\
				.outerjoin(
					album_artist,
					ab_albumArtistFk == album_artist_id,
				)\
				.outerjoin(album_artist_owner,
					album_artist_owner_user_id == album_artist_owner_id,
				)\
				.outerjoin(playlists_songs_tbl, sg_pk == plsg_songFk)\
				.outerjoin(playlists_tbl, plsg_playlistFk == pl_pk)\
				.outerjoin(playlist_owner, playlist_owner_id == pl_ownerFk)\
				.where(sg_deletedTimstamp.is_(None))

		lsong = clean_search_term_for_like(song)
		lalbum = clean_search_term_for_like(album)
		lartist = clean_search_term_for_like(artist)
			

		if stationId:
			query = query.where(st_pk == stationId)

		if lsong:
			query = query.where(sg_name.like(f"%{lsong}%"))

		if lalbum:
			query = query.where(ab_name.like(f"%{lalbum}%"))

		if albumId:
			query = query.where(ab_pk == albumId)

		if lartist:
			query = query.where(ar_name.like(f"%{lartist}%"))

		if artistId:
			query = query.where(ar_pk == artistId)

		if songIds is not None:
			query = query.where(sg_pk.in_(songIds))

		return query
		
		
	def __query_to_full_object__(
		self,
		query: Select[Any],
		queryParams: SimpleQueryParameters,
	) -> Iterator[SongEditInfo]:

		user = self.current_user_provider.current_user()
		
		pathRuleTree = None
		if user:
			pathRuleTree = self.path_rule_service.get_rule_path_tree()

		records = self.conn.execute(query).mappings()

		for e in (
			d[1] for d in enumerate(PathDict.prefix_merge_collect(
				(
					PathDict(dict(row), omitNulls=True) 
					for row in records
				),
				"id",
				"artists",
				"stations",
				"playlists"
			)) if queryParams.limit is None or d[0] < queryParams.limit
		):
			rules = []
			if pathRuleTree:
				rules = list(pathRuleTree.values_flat(
					normalize_opening_slash(cast(str, e["path"])))
				)
			songResult = SongEditInfo(
				**e,
				rules=rules
			)
			if songResult.artists:
				primaryArtistMatch = next(
					(i for i in 
						enumerate(songResult.artists) if i[1].isprimaryartist
					), 
					None
				)

				if primaryArtistMatch:
					songResult.primaryartist = primaryArtistMatch[1]

				songResult.artists = sorted(
					(a for a in songResult.artists if not a.isprimaryartist),
					key=lambda a: a.name
				)
			songResult.stations = sorted(
				songResult.stations or [],
				key=lambda s: s.name
			)
			
			yield songResult
		

	def get_all_songs(
		self,
		queryParams: SimpleQueryParameters,
		stationId: Optional[int]=None,
		song: str = "",
		songIds: Optional[Iterable[int]]=None,
		album: str = "",
		albumId: Optional[int]=None,
		artist: str = "",
		artistId: Optional[int]=None,
	) -> Iterator[SongEditInfo]:
		
		query = self.full_song_base_query(
			stationId,
			song,
			songIds,
			album,
			albumId,
			artist,
			artistId
		)
		query = query.with_only_columns(
			sg_pk.label("id"),
			sg_name.label("name"),
			sg_path.label("path"),
			sg_internalpath.label("internalpath"),
			sg_track.label("track"),
			sg_trackNum.label("tracknum"),
			sg_disc.label("disc"),
			sg_genre.label("genre"),
			sg_explicit.label("explicit"),
			sg_bitrate.label("bitrate"),
			sg_comment.label("comment"),
			sg_lyrics.label("lyrics"),
			sg_duration.label("duration"),
			sg_sampleRate.label("samplerate"),
			ab_pk.label("album.id"),
			ab_name.label("album.name"),
			ab_ownerFk.label("album.owner.id"),
			album_owner.c.username.label("album.owner.username"),
			album_owner.c.displayname.label("album.owner.displayname"),
			ab_year.label("album.year"),
			ab_albumArtistFk.label("album.albumartist.id"),
			album_artist.c.name.label("album.albumartist.name"),
			album_artist.c.ownerfk.label("album.albumartist.owner.id"),
			album_artist_owner.c.username.label("album.albumartist.owner.username"),
			album_artist_owner.c.displayname\
				.label("album.albumartist.owner.displayname"),
			sgar_isPrimaryArtist.label("artists.isprimaryartist"),
			ar_pk.label("artists.id"),
			ar_name.label("artists.name"),
			ar_ownerFk.label("artists.owner.id"),
			artist_owner.c.username.label("artists.owner.username"),
			artist_owner.c.displayname.label("artists.owner.displayname"),
			st_pk.label("stations.id"),
			st_name.label("stations.name"),
			st_ownerFk.label("stations.owner.id"),
			station_owner.c.username.label("stations.owner.username"),
			station_owner.c.displayname.label("stations.owner.displayname"),
			st_displayName.label("stations.displayname"),
			st_requestSecurityLevel.label("stations.requestsecuritylevel"),
			st_viewSecurityLevel.label("stations.viewsecuritylevel"),
			pl_pk.label("playlists.id"),
			pl_name.label("playlists.name"),
			pl_description.label("playlists.description"),
			pl_viewSecurityLevel.label("playlists.viewsecuritylevel"),
			pl_ownerFk.label("playlists.owner.id"),
			playlist_owner.c.username.label("playlists..owner.username"),
			playlist_owner.c.displayname.label("playlists.owner.displayname")
		)

		if queryParams.orderByElement is not None:
			query = query.order_by(None).order_by(queryParams.orderByElement)

		offset = queryParams.page * queryParams.limit if queryParams.limit else 0
		query = query\
			.offset(offset)
		
		return self.__query_to_full_object__(query, queryParams)



