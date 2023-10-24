
from typing import (
	Iterator,
	Optional,
	Union,
	cast,
	Iterable,
	Any,
	Tuple,
	Callable
)
from musical_chairs_libs.dtos_and_utilities import (
	SavedNameString,
	SongListDisplayItem,
	ScanningSongItem,
	StationInfo,
	SearchNameString,
	get_datetime,
	Sentinel,
	missing,
	AlbumInfo,
	ArtistInfo,
	SongAboutInfo,
	SongEditInfo,
	build_error_obj,
	AlbumCreationInfo,
	StationSongTuple,
	SongArtistTuple,
	AlreadyUsedError,
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
	Integer
)
from sqlalchemy.sql.expression import (
	Tuple as dbTuple,
	Select,
	Update,
)
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.schema import Column
from sqlalchemy.engine.row import RowMapping
from dataclasses import asdict, fields
from itertools import chain, groupby
from musical_chairs_libs.tables import (
	albums as albums_tbl,
	song_artist as song_artist_tbl,
	artists as artists_tbl,
	songs as songs_tbl,
	stations_songs as stations_songs_tbl, stsg_songFk, stsg_stationFk,
	stations as stations_tbl, st_name, st_pk, st_displayName, st_ownerFk,
	sg_pk, sg_name, sg_path,
	ab_name, ab_pk, ab_albumArtistFk, ab_year, ab_ownerFk,
	ar_name, ar_pk, ar_ownerFk,
	sg_albumFk, sg_bitrate,sg_comment, sg_disc, sg_duration, sg_explicit,
	sg_genre, sg_lyrics, sg_sampleRate, sg_track,
	sgar_isPrimaryArtist, sgar_songFk, sgar_artistFk,
	users as user_tbl, u_pk, u_username, u_displayName
)



class SongInfoService:

	def __init__(
		self,
		conn: Connection,
		pathRuleService: Optional[PathRuleService]=None
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		if not pathRuleService:
			pathRuleService = PathRuleService(conn)
		self.path_rule_service = pathRuleService
		self.get_datetime = get_datetime

	def song_info(self, songPk: int) -> Optional[SongListDisplayItem]:
		query = select(
			sg_pk,
			sg_name,
			sg_path,
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
			id=cast(int,row[sg_pk]),
			path=cast(str,row[sg_path]),
			name=cast(str,row[sg_name]),
			album=cast(str,row["album"]),
			artist=cast(str,row["artist"]),
			queuedtimestamp=0
		)

	def get_or_save_artist(self, name: Optional[str]) -> Optional[int]:
		if not name:
			return None
		savedName = SavedNameString.format_name_for_save(name)
		query = select(ar_pk).select_from(artists_tbl).where(ar_name == savedName)
		row = self.conn.execute(query).fetchone()
		if row:
			pk = cast(int, row[0])
			return pk
		print(name)
		stmt = insert(artists_tbl).values(
			name = savedName,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		res = self.conn.execute(stmt)
		insertedPk = res.lastrowid
		self.conn.commit()
		return insertedPk

	def __get_artist_owner__(self, artistId: int) -> OwnerInfo:
		query = select(ar_ownerFk, u_username, u_displayName)\
			.select_from(artists_tbl)\
			.join(user_tbl, u_pk == ar_ownerFk)\
			.where(ab_pk == artistId)
		data = self.conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
		if not data:
			return OwnerInfo(0,"", "")
		return OwnerInfo(
			data[ar_ownerFk],
			data[u_username],
			data[u_displayName]
		)

	def save_artist(
		self,
		user: AccountInfo,
		artistName: str,
		artistId: Optional[int]=None
	) -> ArtistInfo:
		if not artistName and not artistId:
			raise ValueError("No artist info to save")
		upsert = update if artistId else insert
		savedName = SavedNameString(artistName)
		stmt = upsert(artists_tbl).values(
			name = str(savedName),
			lastModifiedByUserFk = user.id,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		owner = user
		if artistId and isinstance(stmt, Update):
			stmt = stmt.where(ar_pk == artistId)
			owner = self.__get_artist_owner__(artistId)
		else:
			stmt = stmt.values(ownerfk = user.id)
		try:
			res = self.conn.execute(stmt)

			affectedPk: int = artistId if artistId else res.lastrowid
			self.conn.commit()
			return ArtistInfo(id=affectedPk, name=str(savedName), owner=owner)
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{artistName} is already used.",
					"path->name"
				)]
			)

	def __get_album_owner__(self, albumId: int) -> OwnerInfo:
		query = select(ab_ownerFk, u_username, u_displayName)\
			.select_from(albums_tbl)\
			.join(user_tbl, u_pk == ab_ownerFk)\
			.where(ab_pk == albumId)
		data = self.conn.execute(query).fetchone()
		if not data:
			return OwnerInfo(0,"", "")
		return OwnerInfo(
			data[ab_ownerFk],
			data[u_username],
			data[u_displayName]
		)

	def save_album(
		self,
		album: AlbumCreationInfo,
		user: AccountInfo,
		albumId: Optional[int]=None
	) -> AlbumInfo:
		if not album and not albumId:
			raise ValueError("No album info to save")
		upsert = update if albumId else insert
		savedName = SavedNameString(album.name)
		stmt = upsert(albums_tbl).values(
			name = str(savedName),
			year = album.year,
			albumartistfk = album.albumartist.id if album.albumartist else None,
			lastmodifiedbyuserfk = user.id,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		owner = user
		if albumId and isinstance(stmt, Update):
			stmt = stmt.where(ab_pk == albumId)
			owner = self.__get_album_owner__(albumId)
		else:
			stmt = stmt.values(ownerfk = user.id)
		try:
			res = self.conn.execute(stmt)

			affectedPk = albumId if albumId else res.lastrowid
			artist = next(self.get_artists(
				userId=user.id,
				artistKeys=album.albumartist.id
			), None) if album.albumartist else None
			self.conn.commit()
			return AlbumInfo(affectedPk, str(savedName), owner, album.year, artist)
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{album.name} is already used for artist.",
					"body->name"
				)]
			)

	def get_or_save_album(
		self,
		name: Optional[str],
		artistFk: Optional[int]=None,
		year: Optional[int]=None
	) -> Optional[int]:
		if not name:
			return None
		savedName = SavedNameString.format_name_for_save(name)
		query = select(ab_pk).select_from(albums_tbl).where(ab_name == savedName)
		if artistFk:
			query = query.where(ab_albumArtistFk == artistFk)
		row = self.conn.execute(query).fetchone()
		if row:
			pk = cast(int, row[0])
			return pk
		print(name)
		stmt = insert(albums_tbl).values(
			name = savedName,
			albumartistfk = artistFk,
			year = year,
			lastmodifiedtimestamp = self.get_datetime().timestamp(),
			ownerfk = 1,
			lastmodifiedbyuserfk = 1
		)
		res = self.conn.execute(stmt)
		insertedPk = res.lastrowid
		return insertedPk

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
				query = query.join(stations_tbl, stsg_stationFk == st_pk)
				query = query.join(stations_tbl, st_pk == stsg_stationFk).where(
					st_name.like(f"%{stationKey}%")
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
		stationSongs: Iterable[Union[StationSongTuple, Tuple[int, int]]],
	) -> int:
		stationSongs = stationSongs or []
		delStmt = delete(stations_songs_tbl)\
			.where(dbTuple(stsg_songFk, stsg_stationFk).in_(stationSongs))
		return self.conn.execute(delStmt).rowcount

	def validate_stations_songs(
		self,
		stationSongs: Iterable[StationSongTuple]
	) -> Iterable[StationSongTuple]:
		if not stationSongs:
			return iter([])
		query = select(
			sg_pk,
			st_pk
		).where(dbTuple(sg_pk, st_pk).in_(stationSongs))

		records = self.conn.execute(query)
		yield from (StationSongTuple(
			cast(int, row[0]),
			cast(int, row[1])
		) for row in records)

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

	def get_albums(self,
		page: int = 0,
		pageSize: Optional[int]=None,
		albumKeys: Union[int, str, Iterable[int], None]=None,
		userId: Optional[int]=None
	) -> Iterator[AlbumInfo]:
		album_owner = user_tbl.alias("albumowner")
		albumOwnerId = cast(Column[Integer], album_owner.c.pk)
		artist_owner = user_tbl.alias("artistowner")
		artistOwnerId = cast(Column[Integer], artist_owner.c.pk)
		query = select(
			ab_pk.label("id"),
			ab_name.label("name"),
			ab_year.label("year"),
			ab_albumArtistFk.label("albumartistid"),
			ab_ownerFk.label("album.ownerid"),
			album_owner.c.username.label("album.ownername"),
			album_owner.c.displayname.label("album.ownerdisplayname"),
			ar_name.label("artist.name"),
			ar_ownerFk.label("artist.ownerid"),
			artist_owner.c.username.label("artist.ownername"),
			artist_owner.c.displayname.label("artist.ownerdisplayname")
		).select_from(albums_tbl)\
			.join(artists_tbl, ar_pk == ab_albumArtistFk, isouter=True) \
			.join(album_owner, albumOwnerId == ab_ownerFk, isouter=True) \
			.join(artist_owner, artistOwnerId == ar_ownerFk, isouter=True)
		if type(albumKeys) == int:
			query = query.where(ab_pk == albumKeys)
		elif isinstance(albumKeys, Iterable):
			query = query.where(ab_pk.in_(albumKeys))
		elif type(albumKeys) is str:
			searchStr = SearchNameString.format_name_for_search(albumKeys)
			query = query\
				.where(ab_name.like(f"%{searchStr}%"))
		if userId:
			query = query.where(ab_ownerFk == userId)
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query).mappings()
		yield from (AlbumInfo(
			row["id"],
			row["name"],
			OwnerInfo(
				row["album.ownerid"],
				row["album.ownername"],
				row["album.ownerdisplayname"]
			),
			row["year"],
			ArtistInfo(
				row["albumartistid"],
				row["artist.name"],
				OwnerInfo(
					row["artist.ownerid"],
					row["artist.ownername"],
					row["artist.ownerdisplayname"]
				)
			) if row["albumartistid"] else None
			) for row in records)

	def get_artists(self,
		page: int = 0,
		pageSize: Optional[int]=None,
		artistKeys: Union[int, Iterable[int], str, None]=None,
		userId: Optional[int]=None
	) -> Iterator[ArtistInfo]:
		query = select(
			ar_pk,
			ar_name,
			ar_ownerFk,
			u_username,
			u_displayName
		)\
		.join(user_tbl, u_pk == ar_ownerFk, isouter=True)
		if type(artistKeys) == int:
			query = query.where(ar_pk == artistKeys)
		#check speficially if instance because [] is falsy
		elif isinstance(artistKeys, Iterable) :
			query = query.where(ar_pk.in_(artistKeys))
		elif type(artistKeys) is str:
			query = query\
				.where(ar_name.like(f"%{artistKeys}%"))
		if userId:
			query = query.where(ar_ownerFk == userId)
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query).mappings()

		yield from (ArtistInfo(
			row[ar_pk],
			row[ar_name],
			OwnerInfo(
				row[ar_ownerFk],
				row[u_username],
				row[u_displayName]
			)
		)
			for row in records)

	def get_song_artists(
		self,
		songIds: Union[int, Iterable[int],None]=None,
		artistIds: Union[int, Iterable[int],None]=None,
	) -> Iterable[SongArtistTuple]:
		query = select(
			sgar_artistFk,
			sgar_songFk,
			sgar_isPrimaryArtist
		)

		if type(songIds) == int:
			query = query.where(sgar_songFk == songIds)
		elif isinstance(songIds, Iterable):
			query = query.where(sgar_songFk.in_(songIds))
		if type(artistIds) == int:
			query = query.where(sgar_artistFk == artistIds)
		elif isinstance(artistIds, Iterable):
			query = query.where(sgar_artistFk.in_(artistIds))
		query = query.order_by(sgar_songFk)
		records = self.conn.execute(query).mappings()
		yield from (SongArtistTuple(
				row[sgar_songFk],
				row[sgar_artistFk],
				row[sgar_isPrimaryArtist]
			)
			for row in records)

	def remove_songs_for_artists(
		self,
		songArtists: Iterable[Union[SongArtistTuple, Tuple[int, int]]],
	) -> int:
		songArtists = songArtists or []
		delStmt = delete(song_artist_tbl)\
			.where(dbTuple(sgar_songFk, sgar_artistFk).in_(songArtists))
		count = self.conn.execute(delStmt).rowcount
		return count

	def validate_song_artists(
		self,
		songArtists: Iterable[SongArtistTuple]
	) -> Iterable[SongArtistTuple]:
		if not songArtists:
			return iter([])
		songArtistsSet = set(songArtists)
		primaryArtistId = next(
			(sa.artistid for sa in songArtistsSet if sa.isprimaryartist),
			-1
		)
		query = select(
			sg_pk,
			ar_pk
		).where(dbTuple(sg_pk, ar_pk).in_(songArtistsSet))

		records = self.conn.execute(query)
		yield from (SongArtistTuple(
			row[0],
			row[1],
			isprimaryartist=cast(int, row[1]) == primaryArtistId
		) for row in records)

	def __are_all_primary_artist_single(
		self,
		songArtists: Iterable[SongArtistTuple]
	) -> bool:
		songKey: Callable[[SongArtistTuple],int] = lambda a: a.songid
		artistsGroups = groupby(sorted(songArtists, key=songKey), key=songKey)
		for _, g in artistsGroups:
			if len([sa for sa in g if sa.isprimaryartist]) > 1:
				return False
		return True

	def link_songs_with_artists(
		self,
		songArtists: Iterable[SongArtistTuple],
		userId: Optional[int]=None
	) -> Iterable[SongArtistTuple]:
		if not songArtists:
			return []
		uniquePairs = set(self.validate_song_artists(songArtists))

		if not self.__are_all_primary_artist_single(uniquePairs):
			raise ValueError("Only one artist can be the primary artist")
		existingPairs = set(self.get_song_artists(
			songIds={sa.songid for sa in uniquePairs}
		))
		outPairs = existingPairs - uniquePairs
		inPairs = uniquePairs - existingPairs
		self.remove_songs_for_artists(outPairs)
		if not inPairs: #if no songs - artist have been linked
			return existingPairs - outPairs
		params = [{
			"songfk": p.songid,
			"artistfk": p.artistid,
			"isprimaryartist": p.isprimaryartist,
			"lastmodifiedbyuserfk": userId,
			"lastmodifiedtimestamp": self.get_datetime().timestamp()
		} for p in inPairs]
		stmt = insert(song_artist_tbl)
		self.conn.execute(stmt, params)
		return self.get_song_artists(
			songIds={sa.songid for sa in uniquePairs}
		)

	def _prepare_song_row_for_model(self, row: RowMapping) -> dict[str, Any]:
		songDict: dict[Any, Any] = {**row}
		albumArtistId = songDict.pop("album.albumartistid", None)
		albumArtistName = songDict.pop("album.albumartist.name", "")
		albumArtistOwner = OwnerInfo(
			songDict.pop("album.albumartist.ownerid", 0),
			songDict.pop("album.albumartist.ownername", ""),
			songDict.pop("album.albumartist.ownerdisplayname", ""),
		)
		album = AlbumInfo(
			songDict.pop("album.id", None),
			songDict.pop("album.name", None),
			OwnerInfo(
				songDict.pop("album.ownerid", 0),
				songDict.pop("album.ownername", ""),
				songDict.pop("album.ownerdisplayname", ""),
			),
			songDict.pop("album.year", None),
			ArtistInfo(
				albumArtistId,
				albumArtistName,
				albumArtistOwner,
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
			st_displayName.label("station.displayname")
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
					row["artist.id"],
					row["artist.name"],
					OwnerInfo(
						row["artist.ownerid"],
						row["artist.ownername"],
						row["artist.ownerdisplayname"]
					)
				)
			elif row["artist.id"]:
				artists.add(ArtistInfo(
						row["artist.id"],
						row["artist.name"],
						OwnerInfo(
							row["artist.ownerid"],
							row["artist.ownername"],
							row["artist.ownerdisplayname"]
						)
					)
				)
			if row["station.id"]:
				stations.add(StationInfo(
					row["station.id"],
					row["station.name"],
					row["station.displayname"],
					owner=OwnerInfo(
						row["station.ownerid"],
						row["station.ownername"],
						row["station.ownerdisplayname"]
					)
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
			songInfo.touched = {f.name for f in fields(SongAboutInfo)}
		ids = list(ids)
		songInfo.name = str(SavedNameString(songInfo.name))
		songInfoDict = asdict(songInfo)
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
			self.link_songs_with_artists(
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
		if "stations" in songInfo.touched:
			self.link_songs_with_stations(
				(StationSongTuple(sid, t.id)
					for t in (songInfo.stations or []) for sid in ids),
				user.id
			)
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
		touched = {f.name for f in fields(SongAboutInfo) }
		removedFields: set[str] = set()
		rules = None
		for songInfo in self.get_songs_for_edit(songIds, user):
			if rules is None: #empty set means no permissions. Don't overwrite
				rules = set(songInfo.rules)
			else:
				# only keep the set of rules that are common to
				# each song
				rules = rules & set(songInfo.rules)
			songInfoDict = asdict(songInfo)
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




