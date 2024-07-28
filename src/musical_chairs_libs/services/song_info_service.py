
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
	StationInfo,
	get_datetime,
	Sentinel,
	missing,
	AlbumInfo,
	ArtistInfo,
	SongAboutInfo,
	SongEditInfo,
	StationSongTuple,
	SongArtistTuple,
	AccountInfo,
	OwnerInfo,
	normalize_opening_slash
)
from .path_rule_service import PathRuleService
from sqlalchemy import (
	select,
	insert,
	update,
	delete,
)
from sqlalchemy.sql.expression import (
	Tuple as dbTuple,
	Select,
)
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import RowMapping
from itertools import chain
from musical_chairs_libs.tables import (
	albums as albums_tbl,
	song_artist as song_artist_tbl,
	artists as artists_tbl,
	songs as songs_tbl,
	stations_songs as stations_songs_tbl, stsg_songFk, stsg_stationFk,
	stations as stations_tbl, st_name, st_pk, st_displayName, st_ownerFk,
	st_requestSecurityLevel, st_viewSecurityLevel,
	sg_pk, sg_name, sg_path,
	ab_name, ab_pk, ab_albumArtistFk, ab_year, ab_ownerFk,
	ar_name, ar_pk, ar_ownerFk,
	sg_albumFk, sg_bitrate,sg_comment, sg_disc, sg_duration, sg_explicit,
	sg_genre, sg_lyrics, sg_sampleRate, sg_track, sg_internalpath,
	sgar_isPrimaryArtist, sgar_songFk, sgar_artistFk,
	users as user_tbl
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
		songName: Union[Optional[str], Sentinel]=missing,
		page: int=0,
		pageSize: Optional[int]=None,
	) -> Iterator[ScanningSongItem]:
		query = select(
			sg_pk,
			sg_path,
			sg_name
		).select_from(songs_tbl)
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

	def update_song_info(self, songInfo: ScanningSongItem) -> int:
		savedName =  SavedNameString.format_name_for_save(songInfo.name)
		timestamp = self.get_datetime().timestamp()
		songUpdate = update(songs_tbl) \
				.where(sg_pk == songInfo.id) \
				.values(
					name = savedName,
					albumfk = songInfo.albumId,
					track = songInfo.track,
					disc = songInfo.disc,
					bitrate = songInfo.bitrate,
					comment = songInfo.comment,
					genre = songInfo.genre,
					duration = songInfo.duration,
					samplerate = songInfo.samplerate,
					lastmodifiedtimestamp = timestamp,
					lastmodifiedbyuserfk = None
				)
		count = self.conn.execute(songUpdate).rowcount
		try:
			songComposerInsert = insert(song_artist_tbl)\
				.values(songfk = songInfo.id, artistFk = songInfo.artistId)
			self.conn.execute(songComposerInsert)
		except IntegrityError: pass
		try:
			songComposerInsert = insert(song_artist_tbl)\
				.values(
					songfk = songInfo.id,
					artistfk = songInfo.composerId,
					comment = "composer"
				)
			self.conn.execute(songComposerInsert)
			self.conn.commit()
		except IntegrityError: pass
		return count


	def get_songIds(
		self,
		page: int = 0,
		pageSize: Optional[int]=None,
		stationKey: Union[int, str, None]=None,
		songIds: Optional[Iterable[int]]=None
	) -> Iterator[int]:
		offset = page * pageSize if pageSize else 0
		query = select(sg_pk).select_from(songs_tbl)
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


	def get_station_songs(
		self,
		songIds: Union[int, Iterable[int], None]=None,
		stationIds: Union[int, Iterable[int], None]=None,
	) -> Iterable[StationSongTuple]:
		query = select(
			stsg_songFk,
			stsg_stationFk
		)

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

	def validate_stations_songs(
		self,
		stationSongs: Iterable[StationSongTuple]
	) -> Iterable[StationSongTuple]:
		if not stationSongs:
			return iter([])
		stationSongSet = set(stationSongs)
		songQuery = select(sg_pk).where(
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
		params = [{
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


	def _prepare_song_row_for_model(self, row: RowMapping) -> dict[str, Any]:
		songDict: dict[Any, Any] = {**row}
		albumArtistId = songDict.pop("album.albumartistid", 0) or 0
		albumArtistName = songDict.pop("album.albumartist.name", "")
		albumArtistOwner = OwnerInfo(
			id=songDict.pop("album.albumartist.ownerid", 0) or 0,
			username=songDict.pop("album.albumartist.ownername", ""),
			displayname=songDict.pop("album.albumartist.ownerdisplayname", ""),
		)
		album = AlbumInfo(
			id=songDict.pop("album.id", 0) or 0,
			name=songDict.pop("album.name", None) or "",
			owner=OwnerInfo(
				id=songDict.pop("album.ownerid", 0) or 0,
				username=songDict.pop("album.ownername", ""),
				displayname=songDict.pop("album.ownerdisplayname", ""),
			),
			year=songDict.pop("album.year", None),
			albumartist=ArtistInfo(
				id=albumArtistId,
				name=albumArtistName,
				owner=albumArtistOwner,
			) if albumArtistId else None
		)
		if album.id:
			songDict["album"] = album
		songDict.pop("artist.id", None)
		songDict.pop("artist.name", None)
		songDict.pop("artist.ownerid", None)
		songDict.pop("artist.ownername", None)
		songDict.pop("artist.ownerdisplayname", None)
		songDict.pop("station.id", None)
		songDict.pop("station.name", None)
		songDict.pop("station.displayname", None)
		songDict.pop("station.ownerid", None)
		songDict.pop("station.ownername", None)
		songDict.pop("station.ownerdisplayname", None)
		songDict.pop(sgar_isPrimaryArtist.description, None) #pyright: ignore reportUnknownMemberType
		return songDict

	def __get_query_for_songs_for_edit__(
		self,
		songIds: Iterable[int]
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
			sg_track.label("track"),
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
			ab_ownerFk.label("album.ownerid"),
			albumOwner.c.username.label("album.ownername"),
			albumOwner.c.displayname.label("album.ownerdisplayname"),
			ab_year.label("album.year"),
			ab_albumArtistFk.label("album.albumartistid"),
			album_artist.c.name.label("album.albumartist.name"),
			album_artist.c.ownerfk.label("album.albumartist.ownerid"),
			albumArtistOwner.c.username.label("album.albumartist.ownername"),
			albumArtistOwner.c.displayname.label("album.albumartist.ownerdisplayname"),
			sgar_isPrimaryArtist,
			ar_pk.label("artist.id"),
			ar_name.label("artist.name"),
			ar_ownerFk.label("artist.ownerid"),
			artistOwner.c.username.label("artist.ownername"),
			artistOwner.c.displayname.label("artist.ownerdisplayname"),
			st_pk.label("station.id"),
			st_name.label("station.name"),
			st_ownerFk.label("station.ownerid"),
			stationOwner.c.username.label("station.ownername"),
			stationOwner.c.displayname.label("station.ownerdisplayname"),
			st_displayName.label("station.displayname"),
			st_requestSecurityLevel.label("station.requestsecuritylevel"),
			st_viewSecurityLevel.label("station.viewsecuritylevel")
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
				.where(sg_pk.in_(songIds))\
				.order_by(sg_pk)
		return query

	def get_songs_for_edit(
		self,
		songIds: Iterable[int],
		user: AccountInfo,
	) -> Iterator[SongEditInfo]:
		rulePathTree = self.path_rule_service.get_rule_path_tree(user)
		query = self.__get_query_for_songs_for_edit__(songIds)
		records = self.conn.execute(query).mappings()
		currentSongRow = None
		artists: set[ArtistInfo] = set()
		stations: set[StationInfo] = set()
		primaryArtist: Optional[ArtistInfo] = None
		for row in records:
			if not currentSongRow:
				currentSongRow = row
			elif row["id"] != currentSongRow["id"]:
				songDict = self._prepare_song_row_for_model(currentSongRow)
				rules = [*rulePathTree.valuesFlat(songDict["path"])]
				yield SongEditInfo(**songDict,
					primaryartist=primaryArtist,
					artists=list(artists),
					stations=list(stations),
					rules=rules
				)
				currentSongRow = row
				artists =  set()
				stations = set()
				primaryArtist = None
			if row[sgar_isPrimaryArtist]:
				primaryArtist = ArtistInfo(
					id=row["artist.id"],
					name=row["artist.name"],
					owner=OwnerInfo(
						id=row["artist.ownerid"],
						username=row["artist.ownername"],
						displayname=row["artist.ownerdisplayname"]
					)
				)
			elif row["artist.id"]:
				artists.add(ArtistInfo(
						id=row["artist.id"],
						name=row["artist.name"],
						owner=OwnerInfo(
							id=row["artist.ownerid"],
							username=row["artist.ownername"],
							displayname=row["artist.ownerdisplayname"]
						)
					)
				)
			if row["station.id"]:
				stations.add(StationInfo(
					id=row["station.id"],
					name=row["station.name"],
					displayname=row["station.displayname"],
					owner=OwnerInfo(
						id=row["station.ownerid"],
						username=row["station.ownername"],
						displayname=row["station.ownerdisplayname"]
					),
					requestsecuritylevel=row["station.requestsecuritylevel"],
					viewsecuritylevel=row["station.viewsecuritylevel"]
				))
		if currentSongRow:
			songDict = self._prepare_song_row_for_model(currentSongRow)
			rules = [*rulePathTree.valuesFlat(
				normalize_opening_slash(cast(str, songDict["path"]))
			)]
			yield SongEditInfo(**songDict,
					primaryartist=primaryArtist,
					artists=sorted(artists, key=lambda a: a.id if a else 0),
					stations=sorted(stations, key=lambda t: t.id if t else 0),
					rules=rules
				)

	def save_songs(
		self,
		ids: Iterable[int],
		songInfo: SongAboutInfo,
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
		).where(sg_pk.in_(ids))
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
			return SongEditInfo(
				**commonSongInfo,
				touched=touched,
				rules=list(rules or [])
			)
		else:
			return SongEditInfo(id=0, path="", touched=touched)




