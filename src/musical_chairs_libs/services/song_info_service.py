
from typing import (
	Iterator,
	Optional,
	Union,
	cast,
	Iterable,
	Any,
	Tuple
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
	SongPlaylistTuple,
	SongArtistTuple,
	AccountInfo,
	normalize_opening_slash,
	clean_search_term_for_like,
	PathDict
)
from .path_rule_service import PathRuleService
from sqlalchemy import (
	select,
	insert,
	update,
	delete,
	func,
)
from sqlalchemy.sql.expression import (
	Tuple as dbTuple,
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
	stsg_lastmodifiedtimestamp,
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
	playlists_songs as song_playlist_tbl, plsg_playlistFk, plsg_songFk
)
from .song_artist_service import SongArtistService


class SongInfoService:

	def __init__(
		self,
		conn: Connection,
		pathRuleService: Optional[PathRuleService]=None,
		songArtistService: Optional[SongArtistService]=None,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		if not pathRuleService:
			pathRuleService = PathRuleService(conn)
		if not songArtistService:
			songArtistService = SongArtistService(conn)
		self.path_rule_service = pathRuleService
		self.song_artist_service = songArtistService
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

	def get_station_songs(
		self,
		songIds: Union[int, Iterable[int], None]=None,
		stationIds: Union[int, Iterable[int], None]=None,
	) -> Iterable[StationSongTuple]:
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
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (StationSongTuple(
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
		delStmt = delete(song_playlist_tbl)
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


	def remove_songs_for_stations(
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

	def validate_stations_songs(
		self,
		stationSongs: Iterable[StationSongTuple]
	) -> Iterable[StationSongTuple]:
		if not stationSongs:
			return iter([])
		stationSongSet = set(stationSongs)
		songQuery = select(sg_pk)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(
				sg_pk.in_((s.songid for s in stationSongSet))
			)
		stationQuery = select(st_pk).where(
			st_pk.in_((s.stationid for s in stationSongSet))
		)

		songRecords = self.conn.execute(songQuery).fetchall()
		stationRecords = self.conn.execute(stationQuery).fetchall()
		yield from (t for t in (StationSongTuple(
			cast(int, songRow[0]),
			cast(int, stationRow[0])
		) for songRow in songRecords 
			for stationRow in stationRecords
		) if t in stationSongSet)

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
		stmt = insert(stations_songs_tbl)
		self.conn.execute(stmt, params)
		return self.get_playlist_songs(
			songIds={st.songid for st in uniquePairs}
		)

	def link_songs_with_stations(
		self,
		stationSongs: Iterable[StationSongTuple],
		userId: Optional[int]=None
	) -> Iterable[StationSongTuple]:
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
		self.remove_songs_for_stations(outPairs)
		if not inPairs: #if no songs - stations have been linked
			return existingPairs - outPairs
		params: list[dict[str, Any]] = [{
			"songfk": p.songid,
			"stationfk": p.stationid,
			"lastmodifiedbyuserfk": userId,
			"lastmodifiedtimestamp": self.get_datetime().timestamp()
		} for p in inPairs]
		stmt = insert(stations_songs_tbl)
		self.conn.execute(stmt, params)
		return self.get_station_songs(
			songIds={st.songid for st in uniquePairs}
		)


	def __get_query_for_songs_for_edit__(
		self
	) -> Select[Any]:
		album_artist = artists_tbl.alias("albumartist")
		albumArtistId = album_artist.c.pk
		albumArtistOwnerId = album_artist.c.ownerfk
		albumOwner = user_tbl.alias("albumowner")
		albumOwnerId = albumOwner.c.pk
		albumArtistOwner = user_tbl.alias("albumartistowner")
		albumArtistOwnerUserId = albumArtistOwner.c.pk
		artistOwner = user_tbl.alias("artistowner")
		artistOwnerId = artistOwner.c.pk
		stationOwner = user_tbl.alias("stationowner")
		stationOwnerId = stationOwner.c.pk
		query = select(
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
			albumOwner.c.username.label("album.owner.username"),
			albumOwner.c.displayname.label("album.owner.displayname"),
			ab_year.label("album.year"),
			ab_albumArtistFk.label("album.albumartist.id"),
			album_artist.c.name.label("album.albumartist.name"),
			album_artist.c.ownerfk.label("album.albumartist.owner.id"),
			albumArtistOwner.c.username.label("album.albumartist.owner.username"),
			albumArtistOwner.c.displayname\
				.label("album.albumartist.owner.displayname"),
			sgar_isPrimaryArtist.label("artists.isprimaryartist"),
			ar_pk.label("artists.id"),
			ar_name.label("artists.name"),
			ar_ownerFk.label("artists.owner.id"),
			artistOwner.c.username.label("artists.owner.username"),
			artistOwner.c.displayname.label("artists.owner.displayname"),
			st_pk.label("stations.id"),
			st_name.label("stations.name"),
			st_ownerFk.label("stations.owner.id"),
			stationOwner.c.username.label("stations.owner.username"),
			stationOwner.c.displayname.label("stations.owner.displayname"),
			st_displayName.label("stations.displayname"),
			st_requestSecurityLevel.label("stations.requestsecuritylevel"),
			st_viewSecurityLevel.label("stations.viewsecuritylevel")
		).select_from(songs_tbl)\
				.join(song_artist_tbl, sg_pk == sgar_songFk, isouter=True)\
				.join(artists_tbl, ar_pk == sgar_artistFk, isouter=True)\
				.join(albums_tbl, sg_albumFk == ab_pk, isouter=True)\
				.join(stations_songs_tbl, sg_pk == stsg_songFk, isouter=True)\
				.join(stations_tbl, stsg_stationFk ==  st_pk, isouter=True)\
				.join(albumOwner, albumOwnerId == ab_ownerFk, isouter=True) \
				.join(artistOwner, artistOwnerId ==  ar_ownerFk, isouter=True)\
				.join(stationOwner, stationOwnerId == st_ownerFk, isouter=True)\
				.join(
					album_artist,
					ab_albumArtistFk == albumArtistId,
					isouter=True
				)\
				.join(albumArtistOwner,
					albumArtistOwnerUserId == albumArtistOwnerId,
					isouter=True
				) \
				.where(sg_deletedTimstamp.is_(None))
		return query


	def get_songs_for_edit(
		self,
		songIds: Iterable[int],
		user: AccountInfo,
	) -> Iterator[SongEditInfo]:
		yield from self.get_all_songs(songIds=songIds, user=user)


	def save_songs(
		self,
		ids: Iterable[int],
		songInfo: ChangeTrackedSongInfo,
		user: AccountInfo
	) -> Iterator[SongEditInfo]:
		if not ids:
			return iter([])
		if not songInfo:
			return self.get_songs_for_edit(ids, user)
		if not songInfo.touched:
			songInfo.touched = {f for f in SongAboutInfo.model_fields}
		ids = list(ids)
		songInfo.name = str(SavedNameString(songInfo.name))
		songInfoDict = songInfo.model_dump()
		songInfoDict.pop("artists", None)
		songInfoDict.pop("primaryartist", None)
		songInfoDict.pop("tags", None)
		songInfoDict.pop("id", None)
		songInfoDict.pop("album", None)
		songInfoDict.pop("stations", None)
		songInfoDict.pop("covers", None)
		songInfoDict.pop("touched", None)
		songInfoDict["albumfk"] = songInfo.album.id if songInfo.album else None
		songInfoDict["lastmodifiedbyuserfk"] = user.id
		songInfoDict["lastmodifiedtimestamp"] = self.get_datetime().timestamp()
		if "album" in songInfo.touched:
			songInfo.touched.add("albumfk")
		stmt = update(songs_tbl).values(
			**{k:v for k,v in songInfoDict.items() if k in songInfo.touched}
		)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(sg_pk.in_(ids))
		self.conn.execute(stmt)
		if "artists" in songInfo.touched or "primaryartist" in songInfo.touched:
			self.song_artist_service.link_songs_with_artists(
				chain(
					(SongArtistTuple(sid, a.id) for a in songInfo.artists or []
						for sid in ids
					) if "artists" in songInfo.touched else (),
					#we can't use allArtists here bc we need the primaryartist selection
					(SongArtistTuple(sid, songInfo.primaryartist.id, True) for sid in ids)
						if "primaryartist" in
						songInfo.touched and songInfo.primaryartist else ()
				),
				user.id
			)
			if not [*songInfo.allArtists]:
				self.song_artist_service.remove_songs_for_artists(songIds=ids)
		if "stations" in songInfo.touched:
			self.link_songs_with_stations(
				(StationSongTuple(sid, t.id)
					for t in (songInfo.stations or []) for sid in ids),
				user.id
			)
			if not songInfo.stations:
				self.remove_songs_for_stations(songIds=ids)
		self.conn.commit()
		if len(ids) < 2:
			yield from self.get_songs_for_edit(ids, user)
		else:
			fetched = self.get_songs_for_multi_edit(ids, user)
			if fetched:
				yield fetched


	def get_songs_for_multi_edit(
		self,
		songIds: Iterable[int],
		user: AccountInfo
	) -> Optional[SongEditInfo]:
		if not songIds:
			return None
		commonSongInfo = None
		touched = {f for f in SongAboutInfo.model_fields }
		removedFields: set[str] = set()
		rules = None
		for songInfo in self.get_songs_for_edit(songIds, user):
			if rules is None: #empty set means no permissions. Don't overwrite
				rules = set(songInfo.rules)
			else:
				# only keep the set of rules that are common to
				# each song
				rules = rules & set(songInfo.rules)
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
			commonSongInfo["path"] = ""
			del commonSongInfo["rules"]
			commonSongInfo["touched"] = touched
			return SongEditInfo(
				**commonSongInfo,
				rules=list(rules or [])
			)
		else:
			return SongEditInfo(id=0, path="", internalpath="", touched=touched)


	def __attach_catalogue_joins__(
		self,
		query: Select[Any],
		stationId: Optional[int]=None,
		song: str = "",
		songIds: Optional[Iterable[int]]=None,
		album: str = "",
		albumId: Optional[int]=None,
		artist: str = "",
		artistId: Optional[int]=None
	) -> Any:


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

		if songIds:
			query = query.where(sg_pk.in_(songIds))

		if stationId:
			return query.order_by(
				stsg_lastmodifiedtimestamp.desc(),
				ar_name
			)
		else:
			return query.order_by(
				sg_pk
			)


	def get_all_songs(
		self,
		stationId: Optional[int]=None,
		page: int = 0,
		song: str = "",
		songIds: Optional[Iterable[int]]=None,
		album: str = "",
		albumId: Optional[int]=None,
		artist: str = "",
		artistId: Optional[int]=None,
		limit: Optional[int]=None,
		user: Optional[AccountInfo]=None
	) -> Iterator[SongEditInfo]:
		offset = page * limit if limit else 0
		pathRuleTree = None
		if user:
			pathRuleTree = self.path_rule_service.get_rule_path_tree(user)

		query = self.__attach_catalogue_joins__(
			self.__get_query_for_songs_for_edit__(),
			stationId,
			song,
			songIds,
			album,
			albumId,
			artist,
			artistId
		)
		query = query\
			.offset(offset)
		records = self.conn.execute(query).mappings()


		for e in (
			d[1] for d in enumerate(PathDict.prefix_merge_collect(
				(
					PathDict(dict(row), omitNulls=True) 
					for row in records
				),
				"id",
				"artists",
				"stations"
			)) if limit is None or d[0] < limit
		):
			rules = []
			if pathRuleTree:
				rules = list(pathRuleTree.valuesFlat(
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


	def get_fullsongs_page(
		self,
		stationId: Optional[int]=None,
		page: int = 0,
		song: str = "",
		album: str = "",
		artist: str = "",
		limit: Optional[int]=None,
		user: Optional[AccountInfo]=None
	) -> Tuple[Iterator[SongEditInfo], int]:
		
		countQuery = select(func.count(sg_pk))

		if stationId:
			countQuery = countQuery\
				.join(stations_songs_tbl, stsg_songFk == sg_pk)\
				.where(stsg_stationFk == stationId)
		count = self.conn.execute(countQuery).scalar() or 0

		return self.get_all_songs(
			stationId=stationId,
			page=page,
			song=song,
			album=album,
			artist=artist,
			limit=limit,
			user=user
		), count


	def get_song_catalogue(
		self,
		stationId: Optional[int]=None,
		page: int = 0,
		song: str = "",
		album: str = "",
		artist: str = "",
		limit: Optional[int]=None,
		user: Optional[AccountInfo]=None
	) -> Tuple[list[SongListDisplayItem], int]:
		songs, count = self.get_fullsongs_page(
			stationId,
			page,
			song,
			album,
			artist,
			limit,
			user
		)

		return [SongListDisplayItem(
			id=s.id,
			name=s.name or "Missing Name",
			queuedtimestamp=0,
			album=s.album.name if s.album else "No Album",
			artist=s.primaryartist.name 
				if s.primaryartist 
				else next((a.name for a in s.artists or []), None),
			path=s.path,
			internalpath=s.internalpath,
			track=s.track,
			rules=s.rules
		) for s in songs], count

