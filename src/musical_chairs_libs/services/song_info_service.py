import itertools
import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.tables as tbl
import sqlalchemy as sa
import typing
from .path_rule_service import PathRuleService
from .playlists_songs_service import PlaylistsSongsService
from sqlalchemy.sql.expression import (
	Select,
)
from sqlalchemy.engine import Connection
from musical_chairs_libs.protocols import (UserProvider)
from .song_artist_service import SongArtistService
from .stations_songs_service import StationsSongsService

album_artist = tbl.artists.alias("albumartist")
album_artist_id = album_artist.c.pk
album_artist_owner_id = album_artist.c.ownerfk
album_owner = tbl.users.alias("albumowner")
album_owner_id = album_owner.c.pk
album_artist_owner = tbl.users.alias("albumartistowner")
album_artist_owner_user_id = album_artist_owner.c.pk
artist_owner = tbl.users.alias("artistowner")
artist_owner_id = artist_owner.c.pk
station_owner = tbl.users.alias("stationowner")
station_owner_id = station_owner.c.pk
playlist_owner = tbl.users.alias("playlistowner")
playlist_owner_id = playlist_owner.c.pk


 
class SongInfoService:

	def __init__(
		self,
		conn: Connection,
		currentUserProvider: UserProvider,
		pathRuleService: PathRuleService,
		songArtistService: SongArtistService | None=None,
		stationsSongsService: StationsSongsService | None=None,
		playlistsSongsService: PlaylistsSongsService | None=None
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
		self.get_datetime = dtos.get_datetime


	def song_info(self, songPk: int) -> dtos.SongListDisplayItem | None:
		query = sa.select(
			tbl.sg_pk,
			tbl.sg_name,
			tbl.sg_path,
			tbl.sg_internalpath,
			tbl.ab_name.label("album"),
			tbl.ar_name.label("artist")
		)\
			.select_from(tbl.songs)\
			.join(tbl.albums, tbl.sg_albumFk == tbl.ab_pk, isouter=True)\
			.join(tbl.song_artist, tbl.sg_pk == tbl.sgar_songFk, isouter=True)\
			.join(tbl.artists, tbl.sgar_artistFk == tbl.ar_pk, isouter=True)\
			.where(tbl.sg_pk == songPk)\
			.where(tbl.sg_deletedTimstamp.is_(None))\
			.limit(1)
		row = self.conn.execute(query).mappings().fetchone()
		if not row:
			return None
		return dtos.SongListDisplayItem(
			id=row[tbl.sg_pk],
			treepath=row[tbl.sg_path],
			internalpath=row[tbl.sg_internalpath],
			name=row[tbl.sg_name],
			album=row["album"],
			artist=row["artist"],
			queuedtimestamp=0
		)


	def get_song_refs(
		self,
		songName: str | None | dtos.Lost=dtos.Lost(),
		page: int=0,
		pageSize: int | None=None,
	) -> typing.Iterator[dtos.ScanningSongItem]:
		query = sa.select(
			tbl.sg_pk,
			tbl.sg_path,
			tbl.sg_name
		).select_from(tbl.songs)\
			.where(tbl.sg_deletedTimstamp.is_(None))
		if type(songName) is str or songName is None:
			#allow null through
			savedName = dtos.SavedNameString.format_name_for_save(songName)\
				if songName\
				else None
			query = query.where(tbl.sg_name == savedName)
		if pageSize:
			offset = page * pageSize
			query = query.limit(pageSize).offset(offset)
		records = self.conn.execute(query).mappings().fetchall()
		for row in records:
			yield dtos.ScanningSongItem(
					id=row[tbl.sg_pk],
					treepath=row[tbl.sg_path],
					name=dtos.SavedNameString.format_name_for_save(row[tbl.sg_name])
				)


	def get_songIds(
		self,
		page: int = 0,
		pageSize: int | None=None,
		stationKey: int | str | None=None,
		songIds: typing.Iterable[int] | None=None
	) -> typing.Iterator[int]:
		offset = page * pageSize if pageSize else 0
		query = sa.select(tbl.sg_pk).select_from(tbl.songs)\
			.where(tbl.sg_deletedTimstamp.is_(None))
		#add joins
		if stationKey:
			query = query.join(tbl.stations_songs, tbl.stsg_songFk == tbl.sg_pk)
			if type(stationKey) == int:
				query = query.where(tbl.stsg_stationFk == stationKey)
			elif type(stationKey) is str:
				lStationKey = stationKey.replace("_","\\_").replace("%","\\%")
				query = query.join(tbl.stations, tbl.stsg_stationFk == tbl.st_pk)
				query = query.join(tbl.stations, tbl.st_pk == tbl.stsg_stationFk).where(
					tbl.st_name.like(f"%{lStationKey}%", escape="\\")
				)
		if songIds:
			query = query.where(tbl.sg_pk.in_(songIds))
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query).mappings().fetchall()
		yield from (typing.cast(int, row["pk"]) for row in records)


	def get_songs_for_edit(
		self,
		songIds: typing.Iterable[int],
	) -> typing.Iterator[dtos.SongEditInfo]:
		yield from self.get_all_songs(
			songIds=songIds,
			queryParams=dtos.SimpleQueryParameters()
		)


	def update_track_nums(self, tracklistings: dict[str, dtos.TrackListing]):
		for id, listing in tracklistings.items():
			stmt = sa.update(tbl.songs)\
				.values(tracknum = listing.tracknum)\
				.where(tbl.sg_pk == dtos.decode_id(id))
			self.conn.execute(stmt)


	def save_songs(
		self,
		ids: typing.Iterable[int],
		songInfo: dtos.ChangeTrackedSongInfo,
	) -> typing.Iterator[dtos.SongEditInfo]:
		if not ids:
			return iter([])
		if not songInfo:
			return self.get_songs_for_edit(ids, user)
		ids = list(ids)
		user = self.current_user_provider.current_user()
		if not songInfo.touched:
			songInfo.touched = {f for f in dtos.SongAboutInfo.model_fields}
		songInfo.name = str(dtos.SavedNameString(songInfo.name))
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
		songInfoDict["albumfk"] = songInfo.album.decoded_id() \
			if songInfo.album else None
		songInfoDict["lastmodifiedbyuserfk"] = user.id
		songInfoDict["lastmodifiedtimestamp"] = self.get_datetime().timestamp()
		with self.conn.begin():
			if "album" in songInfo.touched:
				songInfo.touched.add("albumfk")
			if any(k for k in songInfoDict.keys() if k in songInfo.touched):
				stmt = sa.update(tbl.songs).values(
					**{k:v for k,v in songInfoDict.items() if k in songInfo.touched}
				)\
					.where(tbl.sg_deletedTimstamp.is_(None))\
					.where(tbl.sg_pk.in_(ids))
				self.conn.execute(stmt)

			if "artists" in songInfo.touched or "primaryartist" in songInfo.touched:
				self.song_artist_service.link_songs_with_artists_in_trx(
					itertools.chain(
						(dtos.SongArtistTuple(sid, a.decoded_id() if a else None) for a 
							in songInfo.artists or [None] * len(ids)
							for sid in ids
						) if "artists" in songInfo.touched else (),
						#we can't use allArtists here bc we need the primaryartist selection
						(dtos.SongArtistTuple(
							sid,
							songInfo.primaryartist.decoded_id(),
							True
						) for sid 
			 				in ids)
							if "primaryartist" in
							songInfo.touched and songInfo.primaryartist else ()
					),
				)
			if "stations" in songInfo.touched:
				self.stations_songs_service.link_songs_with_stations_in_trx(
					(dtos.StationSongTuple(sid, t.decoded_id() if t else None) 
						for t in (songInfo.stations or [None] * len(ids)) for sid in ids),
				)
			if "playlists" in songInfo.touched:
				self.playlists_songs_service.link_songs_with_playlists_in_trx(
					(dtos.SongPlaylistTuple(sid, p.decoded_id() if p else None) 
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
		songIds: typing.Iterable[int],
	) -> dtos.SongEditInfo | None:
		if not songIds:
			return None
		commonSongInfo = None
		touched = {f for f in dtos.SongAboutInfo.model_fields }
		removedFields: set[str] = set()
		rules = None
		trackInfo: dict[str, dtos.TrackListing] = {}
		for songInfo in self.get_songs_for_edit(songIds):
			if rules is None: #empty set means no permissions. Don't overwrite
				rules = set(songInfo.rules)
			else:
				# only keep the set of rules that are common to
				# each song
				rules = rules & set(songInfo.rules)
			trackInfo[songInfo.id] = dtos.TrackListing(
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
			commonSongInfo["id"] = ""
			commonSongInfo["name"] = ""
			commonSongInfo["treepath"] = ""
			commonSongInfo["internalpath"] = ""
			commonSongInfo["rules"] = list(rules or [])
			commonSongInfo["touched"] = touched
			commonSongInfo["trackinfo"] = trackInfo
			return dtos.SongEditInfo(
				**commonSongInfo
			)
		else:
			return dtos.SongEditInfo(
				id="",
				name="Missing",
				treepath="", 
				internalpath="",
				touched=touched
			)


	def full_song_base_query(
		self,
		stationId: int | None=None,
		song: str = "",
		songIds: typing.Iterable[int] | None=None,
		album: str = "",
		albumId: int | None=None,
		artist: str = "",
		artistId: int | None=None
	) -> Select[typing.Any]:

		query = tbl.songs\
				.select()\
				.outerjoin(tbl.song_artist, tbl.sg_pk == tbl.sgar_songFk)\
				.outerjoin(tbl.artists, tbl.ar_pk == tbl.sgar_artistFk)\
				.outerjoin(tbl.albums, tbl.sg_albumFk == tbl.ab_pk)\
				.outerjoin(tbl.stations_songs, tbl.sg_pk == tbl.stsg_songFk)\
				.outerjoin(tbl.stations, tbl.stsg_stationFk ==  tbl.st_pk)\
				.outerjoin(album_owner, album_owner_id == tbl.ab_ownerFk) \
				.outerjoin(artist_owner, artist_owner_id ==  tbl.ar_ownerFk)\
				.outerjoin(station_owner, station_owner_id == tbl.st_ownerFk)\
				.outerjoin(
					album_artist,
					tbl.ab_albumArtistFk == album_artist_id,
				)\
				.outerjoin(album_artist_owner,
					album_artist_owner_user_id == album_artist_owner_id,
				)\
				.outerjoin(tbl.playlists_songs, tbl.sg_pk == tbl.plsg_songFk)\
				.outerjoin(tbl.playlists, tbl.plsg_playlistFk == tbl.pl_pk)\
				.outerjoin(playlist_owner, playlist_owner_id == tbl.pl_ownerFk)\
				.where(tbl.sg_deletedTimstamp.is_(None))

		lsong = dtos.clean_search_term_for_like(song)
		lalbum = dtos.clean_search_term_for_like(album)
		lartist = dtos.clean_search_term_for_like(artist)
			

		if stationId:
			query = query.where(tbl.st_pk == stationId)

		if lsong:
			query = query.where(tbl.sg_name.like(f"%{lsong}%", escape="\\"))

		if lalbum:
			query = query.where(tbl.ab_name.like(f"%{lalbum}%", escape="\\"))

		if albumId:
			query = query.where(tbl.ab_pk == albumId)

		if lartist:
			query = query.where(tbl.ar_name.like(f"%{lartist}%", escape="\\"))

		if artistId:
			query = query.where(tbl.ar_pk == artistId)

		if songIds is not None:
			query = query.where(tbl.sg_pk.in_(songIds))

		return query
		
		
	def __query_to_full_object__(
		self,
		query: Select[typing.Any],
		queryParams: dtos.SimpleQueryParameters,
	) -> typing.Iterator[dtos.SongEditInfo]:

		user = self.current_user_provider.current_user()
		
		pathRuleTree = None
		if user:
			pathRuleTree = self.path_rule_service.get_rule_path_tree()

		records = self.conn.execute(query).mappings().fetchall()

		for e in (
			d[1] for d in enumerate(dtos.PathDict.prefix_merge_collect(
				(
					dtos.PathDict(dict(row), omitNulls=True, spliter=">") 
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
					dtos.normalize_opening_slash(typing.cast(str, e["treepath"])))
				)
			songResult = dtos.SongEditInfo(
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
		queryParams: dtos.SimpleQueryParameters,
		stationId: int | None=None,
		song: str = "",
		songIds: typing.Iterable[int] | None=None,
		album: str = "",
		albumId: int | None=None,
		artist: str = "",
		artistId: int | None=None,
	) -> typing.Iterator[dtos.SongEditInfo]:
		
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
			tbl.sg_pk.label("id"),
			tbl.sg_name.label("name"),
			tbl.sg_path.label("treepath"),
			tbl.sg_internalpath.label("internalpath"),
			tbl.sg_track.label("track"),
			tbl.sg_trackNum.label("tracknum"),
			tbl.sg_disc.label("discnum"),
			tbl.sg_genre.label("genre"),
			tbl.sg_explicit.label("explicit"),
			tbl.sg_bitrate.label("bitrate"),
			tbl.sg_notes.label("notes"),
			tbl.sg_lyrics.label("lyrics"),
			tbl.sg_duration.label("duration"),
			tbl.sg_sampleRate.label("samplerate"),
			tbl.ab_pk.label("album>id"),
			tbl.ab_name.label("album>name"),
			tbl.ab_ownerFk.label("album>owner>id"),
			tbl.ab_versionnote.label("album>versionnote"),
			album_owner.c.username.label("album>owner>username"),
			album_owner.c.displayname.label("album>owner>displayname"),
			album_owner.c.publictoken.label("album>owner>publictoken"),
			tbl.ab_year.label("album>year"),
			tbl.ab_albumArtistFk.label("album>albumartist>id"),
			album_artist.c.name.label("album>albumartist>name"),
			album_artist.c.ownerfk.label("album>albumartist>owner>id"),
			album_artist_owner.c.username.label("album>albumartist>owner>username"),
			album_artist_owner.c.displayname\
				.label("album>albumartist>owner>displayname"),
			album_artist_owner.c.publictoken\
				.label("album>albumartist>owner>publictoken"),
			tbl.sgar_isPrimaryArtist.label("artists>isprimaryartist"),
			tbl.ar_pk.label("artists>id"),
			tbl.ar_name.label("artists>name"),
			tbl.ar_ownerFk.label("artists>owner>id"),
			artist_owner.c.username.label("artists>owner>username"),
			artist_owner.c.displayname.label("artists>owner>displayname"),
			artist_owner.c.publictoken.label("artists>owner>publictoken"),
			tbl.st_pk.label("stations>id"),
			tbl.st_name.label("stations>name"),
			tbl.st_playnum.label("stations>playnum"),
			tbl.st_ownerFk.label("stations>owner>id"),
			station_owner.c.username.label("stations>owner>username"),
			station_owner.c.displayname.label("stations>owner>displayname"),
			station_owner.c.publictoken.label("stations>owner>publictoken"),
			tbl.st_displayName.label("stations>displayname"),
			tbl.st_requestSecurityLevel.label("stations>requestsecuritylevel"),
			tbl.st_viewSecurityLevel.label("stations>viewsecuritylevel"),
			tbl.pl_pk.label("playlists>id"),
			tbl.pl_name.label("playlists>name"),
			tbl.pl_displayname.label("playlists>description"),
			tbl.pl_viewSecurityLevel.label("playlists>viewsecuritylevel"),
			tbl.pl_ownerFk.label("playlists>owner>id"),
			playlist_owner.c.username.label("playlists>owner>username"),
			playlist_owner.c.displayname.label("playlists>owner>displayname"),
			playlist_owner.c.publictoken.label("playlists>owner>publictoken")
		)

		if queryParams.orderByElement is not None:
			query = query.order_by(None).order_by(queryParams.orderByElement)

		offset = queryParams.page * queryParams.limit if queryParams.limit else 0
		query = query\
			.offset(offset)

		with dtos.open_transaction(self.conn):
			yield from self.__query_to_full_object__(query, queryParams)