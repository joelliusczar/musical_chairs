#pyright: reportUnknownMemberType=false
from typing import\
	Iterator,\
	Optional,\
	Union,\
	cast,\
	Iterable,\
	Tuple,\
	Any
from musical_chairs_libs.dtos_and_utilities import\
	SavedNameString,\
	SongListDisplayItem,\
	ScanningSongItem,\
	SongTreeNode,\
	Tag,\
	SearchNameString,\
	SongBase,\
	get_datetime,\
	Sentinel,\
	missing,\
	AlbumInfo,\
	ArtistInfo,\
	SongEditInfo,\
	build_error_obj,\
	AlbumCreationInfo
from sqlalchemy import select, insert, update, func, delete
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from musical_chairs_libs.errors import AlreadyUsedError

from .env_manager import EnvManager
from .tag_service import TagService
from musical_chairs_libs.tables import\
	albums as albums_tbl,\
	song_artist as song_artist_tbl,\
	artists as artists_tbl,\
	songs as songs_tbl,\
	stations_tags as stations_tags_tbl,\
	stations as stations_tbl,\
	tags as tags_tbl,\
	songs_tags as songs_tags_tbl,\
	sg_pk, sg_name, sg_path,\
	tg_pk, tg_name,\
	st_name, st_pk,\
	ab_name, ab_pk, ab_albumArtistFk, ab_year,\
	ar_name, ar_pk,\
	sttg_stationFk, sttg_tagFk,\
	sg_albumFk, sg_bitrate,sg_comment, sg_disc, sg_duration, sg_explicit,\
	sg_genre, sg_lyrics, sg_sampleRate, sg_track,\
	sgtg_songFk, sgtg_tagFk,\
	sgar_isPrimaryArtist, sgar_songFk, sgar_artistFk


class SongInfoService:

	def __init__(
		self,
		conn: Optional[Connection]=None,
		envManager: Optional[EnvManager]=None,
		tagService: Optional[TagService]=None,
	) -> None:
		if not conn:
			if not envManager:
				envManager = EnvManager()
			conn = envManager.get_configured_db_connection()
		if not tagService:
			tagService = TagService(conn)
		self.conn = conn
		self.get_datetime = get_datetime
		self.tag_service = tagService

	def song_info(self, songPk: int) -> Optional[SongListDisplayItem]:
		query = select(
			sg_pk,
			sg_name,
			ab_name.label("album"),
			ar_name.label("artist")
		)\
			.select_from(songs_tbl)\
			.join(albums_tbl, sg_albumFk == ab_pk, isouter=True)\
			.join(song_artist_tbl, sg_pk == sgar_songFk, isouter=True)\
			.join(artists_tbl, sgar_artistFk == ar_pk, isouter=True)\
			.where(sg_pk == songPk)\
			.limit(1)
		row = self.conn.execute(query).fetchone()
		if not row:
			return None
		return SongListDisplayItem(
			row.pk, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			row.name, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			row.album, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			row.artist #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
		)

	def get_or_save_artist(self, name: Optional[str]) -> Optional[int]:
		if not name:
			return None
		savedName = SavedNameString.format_name_for_save(name)
		query = select(ar_pk).select_from(artists_tbl).where(ar_name == savedName)
		row = self.conn.execute(query).fetchone()
		if row:
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		print(name)
		stmt = insert(artists_tbl).values(
			name = savedName,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		res = self.conn.execute(stmt)
		insertedPk: int = res.lastrowid
		return insertedPk

	def save_artist(
		self,
		artistName: str,
		artistId: Optional[int]=None,
		userId: Optional[int]=None
	) -> ArtistInfo:
		if not artistName and not artistId:
			return ArtistInfo(id=-1, name="")
		upsert = update if artistId else insert
		savedName = SavedNameString(artistName)
		stmt = upsert(artists_tbl).values(
			name = str(savedName),
			lastModifiedByUserFk = userId,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		if artistId:
			stmt = stmt.where(ar_pk == artistId)
		try:
			res = self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]

			affectedPk: int = artistId if artistId else res.lastrowid #pyright: ignore [reportUnknownMemberType]
			return ArtistInfo(id=affectedPk, name=str(savedName))
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{artistName} is already used.", "name"
				)]
			)

	def save_album(
		self,
		album: AlbumCreationInfo,
		albumId: Optional[int]=None,
		userId: Optional[int]=None
	) -> AlbumInfo:
		if not album and not albumId:
			return AlbumInfo(id=-1, name="")
		upsert = update if albumId else insert
		savedName = SavedNameString(album.name)
		stmt = upsert(albums_tbl).values(
			name = str(savedName),
			year = album.year,
			albumArtistFk = album.albumArtist.id if album.albumArtist else None,
			lastModifiedByUserFk = userId,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		if albumId:
			stmt = stmt.where(ab_pk == albumId)
		try:
			res = self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]

			affectedPk: int = albumId if albumId else res.lastrowid #pyright: ignore [reportUnknownMemberType]
			artist = next(self.get_artists(artistId=album.albumArtist.id), None)\
				if album.albumArtist else None
			return AlbumInfo(affectedPk, str(savedName), album.year, artist)
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{album.name} is already used for artist.", "name"
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
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		print(name)
		stmt = insert(albums_tbl).values(
			name = savedName,
			albumArtistFk = artistFk,
			year = year,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		res = self.conn.execute(stmt)
		insertedPk: int = res.lastrowid
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
		records = self.conn.execute(query)
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield ScanningSongItem(
					id=row.pk, #pyright: ignore [reportUnknownArgumentType]
					path=row.path, #pyright: ignore [reportUnknownArgumentType]
					name=SavedNameString.format_name_for_save(row.name) #pyright: ignore [reportUnknownArgumentType]
				)

	def update_song_info(self, songInfo: ScanningSongItem) -> int:
		savedName =  SavedNameString.format_name_for_save(songInfo.name)
		timestamp = self.get_datetime().timestamp()
		songUpdate = update(songs_tbl) \
				.where(sg_pk == songInfo.id) \
				.values(
					name = savedName,
					albumFk = songInfo.albumId,
					track = songInfo.track,
					disc = songInfo.disc,
					bitrate = songInfo.bitrate,
					comment = songInfo.comment,
					genre = songInfo.genre,
					duration = songInfo.duration,
					sampleRate = songInfo.sampleRate,
					lastModifiedTimestamp = timestamp,
					lastModifiedByUserFk = None
				)
		count: int = self.conn.execute(songUpdate).rowcount
		try:
			songComposerInsert = insert(song_artist_tbl)\
				.values(songFk = songInfo.id, artistFk = songInfo.artistId)
			self.conn.execute(songComposerInsert)
		except IntegrityError: pass
		try:
			songComposerInsert = insert(song_artist_tbl)\
				.values(
					songFk = songInfo.id,
					artistFk = songInfo.composerId,
					comment = "composer"
				)
			self.conn.execute(songComposerInsert)
		except IntegrityError: pass
		return count

	def song_ls(self, prefix: Optional[str] = "") -> Iterator[SongTreeNode]:
		query = select(
				func.next_directory_level(sg_path, prefix).label("prefix"),
				func.min(sg_name).label("name"),
				func.count(sg_pk).label("totalChildCount"),
				func.max(sg_pk).label("pk"),
				func.max(sg_path).label("control_path")
		).where(sg_path.like(f"{prefix}%"))\
			.group_by(func.next_directory_level(sg_path, prefix))
		records = self.conn.execute(query)
		for row in records: #pyright: ignore [reportUnknownVariableType]
			if row["control_path"] == row["prefix"]:
				yield SongTreeNode(
					path=cast(str, row["prefix"]),
					totalChildCount=cast(int, row["totalChildCount"]),
					id=cast(int, row["pk"]),
					name=cast(str, row["name"])
				)
			else:
				yield SongTreeNode(
					path=cast(str, row["prefix"]),
					totalChildCount=cast(int, row["totalChildCount"])
				)

	def get_songs(
		self,
		page: int = 0,
		pageSize: Optional[int]=None,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None,
		tagId: Optional[int]=None,
		songIds: Optional[Iterable[int]]=None
	) -> Iterator[SongBase]:
		offset = page * pageSize if pageSize else 0
		query = select(sg_pk, sg_name).select_from(songs_tbl)
		if stationId or tagId or stationName:
			query = query.join(songs_tags_tbl, sgtg_songFk == sg_pk)
			if tagId:
				query = query.where(sgtg_tagFk == tagId)
			elif stationId:
				query = query.join(stations_tags_tbl, sgtg_tagFk == sttg_tagFk)\
					.where(sttg_stationFk == stationId)
			elif stationName:
				searchStr = SearchNameString.format_name_for_search(stationName)
				query = query.join(stations_tags_tbl, sgtg_tagFk == sttg_tagFk)\
					.join(stations_tbl, sttg_stationFk == st_pk)\
					.where(func.format_name_for_search(st_name).like(f"%{searchStr}%"))
		if songIds:
			query = query.where(sg_pk.in_(songIds))
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield SongBase(
				id=cast(int, row["pk"]),
				name=cast(str, row["name"]),
			)

	def remove_songs_for_tag(
		self,
		tagId: int,
		songIds: Iterable[int]
	) -> int:
		if not tagId:
			return 0
		songIds = songIds or []
		delStmt = delete(songs_tags_tbl).where(sgtg_tagFk == tagId)\
			.where(sgtg_songFk.in_(songIds))
		return cast(int, self.conn.execute(delStmt).rowcount) #pyright: ignore [reportUnknownMemberType]

	def link_songs_with_tag(
		self,
		tagId: int,
		songIds: Iterable[int],
		userId: Optional[int]=None
	) -> Tuple[Optional[Tag], Iterable[SongBase]]:
		if not songIds:
			return (None, [])
		tag = next(self.tag_service.get_tags(tagId=tagId), None)
		if not tag:
			return (None, [])
		songIdSet = set(songIds)
		existingSongs = list(self.get_songs(tagId=tagId))
		existingSongIds = {s.id for s in existingSongs}
		outSongIds = existingSongIds - songIdSet
		inSongIds = songIdSet - existingSongIds
		self.remove_songs_for_tag(tagId, outSongIds)
		if not inSongIds: #if no songs have been linked
			return (tag,(s for s in existingSongs if s.id not in outSongIds))
		songParams = [{
			"tagFk": tagId,
			"songFk": s,
			"lastModifiedByUserFk": userId,
			"lastModifiedTimestamp": self.get_datetime().timestamp()
		} for s in inSongIds]
		stmt = insert(songs_tags_tbl)
		self.conn.execute(stmt, songParams) #pyright: ignore [reportUnknownMemberType]
		return (tag, self.get_songs(tagId=tagId))

	def get_albums(self,
		page: int = 0,
		pageSize: Optional[int]=None,
		albumId: Union[int, Sentinel]=missing,
		albumIds: Union[Iterable[int], Sentinel]=missing,
		albumName: Union[str, Sentinel]=missing
	) -> Iterator[AlbumInfo]:
		query = select(
			ab_pk.label("id"),
			ab_name.label("name"),
			ab_year.label("year"),
			ab_albumArtistFk.label("albumArtistId"),
			ar_name.label("Artist.Name")
		).select_from(albums_tbl)\
			.join(artists_tbl, ar_pk == ab_albumArtistFk)
		if type(albumId) == int:
			query = query.where(ab_pk == albumId)
		elif albumIds:
			query = query.where(ab_pk.in_(cast(Iterable[int],albumIds)))
		elif type(albumName) is str:
			searchStr = SearchNameString.format_name_for_search(albumName)
			query = query\
				.where(func.format_name_for_search(ab_name).like(f"%{searchStr}%"))
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (AlbumInfo(
			row["id"], #pyright: ignore [reportUnknownArgumentType]
			row["name"], #pyright: ignore [reportUnknownArgumentType]
			row["year"], #pyright: ignore [reportUnknownArgumentType]
			ArtistInfo(
				row["albumArtistId"], #pyright: ignore [reportUnknownArgumentType]
				row["Artist.Name"] #pyright: ignore [reportUnknownArgumentType]
			)) for row in records) #pyright: ignore [reportUnknownVariableType, reportUnknownArgumentType]

	def get_artists(self,
		page: int = 0,
		pageSize: Optional[int]=None,
		artistId: Union[int, Sentinel]=missing,
		artistIds: Union[Iterable[int], Sentinel]=missing,
		artistName: Union[str, Sentinel]=missing
	) -> Iterator[ArtistInfo]:
		query = select(
			ar_pk.label("id"),
			ar_name.label("name"),
		)
		if type(artistId) == int:
			query = query.where(ar_pk == artistId)
		elif artistIds:
			query = query.where(ar_pk.in_(cast(Iterable[int], artistIds)))
		elif type(artistName) is str:
			searchStr = SearchNameString.format_name_for_search(artistName)
			query = query\
				.where(func.format_name_for_search(ar_name).like(f"%{searchStr}%"))
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (ArtistInfo(**row) for row in records) #pyright: ignore [reportUnknownVariableType, reportUnknownArgumentType]



	def get_song_for_edit(self, songId: int) -> Optional[SongEditInfo]:
		album_artist = artists_tbl.alias("AlbumArtist") #pyright: ignore [reportUnknownVariableType]
		query = select(
			func.max(sg_pk).label("id"),
			func.max(sg_name).label("name"),
			func.max(sg_path).label("path"),
			func.max(sg_track).label("track"),
			func.max(sg_disc).label("disc"),
			func.max(sg_genre).label("genre"),
			func.max(sg_explicit).label("explicit"),
			func.max(sg_bitrate).label("bitrate"),
			func.max(sg_comment).label("comment"),
			func.max(sg_lyrics).label("lyrics"),
			func.max(sg_duration).label("duration"),
			func.max(sg_sampleRate).label("sampleRate"),
			func.max(ab_pk).label("Album.Id"),
			func.max(ab_name).label("Album.Name"),
			sgar_isPrimaryArtist,
			ar_pk.label("Artist.Id"),
			ar_name.label("Artist.Name"),
			tg_pk.label("Tag.Id"),
			tg_name.label("Tag.Name"),
		).select_from(songs_tbl)\
				.join(song_artist_tbl, sg_pk == sgar_songFk, isouter=True)\
				.join(artists_tbl, ar_pk == sgar_artistFk)\
				.join(albums_tbl, sg_albumFk == ab_pk, isouter=True)\
				.join(songs_tags_tbl, sg_pk == sgtg_songFk, isouter=True)\
				.join(tags_tbl, sgtg_tagFk ==  tg_pk)\
				.join(album_artist, ab_albumArtistFk == ar_pk, isouter=True)\
				.group_by(
					"Artist.Id",
					"Artist.Name",
					sgar_isPrimaryArtist,
					"Tag.Id",
					"Tag.Name",
					)\
				.where(sg_pk == songId)\
				.order_by(sg_pk)
		records = self.conn.execute(query).fetchall()
		currentSongRow = None
		artists: set[ArtistInfo] = set()
		tags: set[Tag] = set()
		primaryArtist: Optional[ArtistInfo] = None
		for row in records:
			if not currentSongRow:
				currentSongRow = row
			if row[sgar_isPrimaryArtist]:
				primaryArtist = ArtistInfo(
					row["Artist.Id"],
					row["Artist.Name"]
				)
			else:
				artists.add(ArtistInfo(
						row["Artist.Id"],
						row["Artist.Name"]
					)
				)
			tags.add(Tag(row["Tag.Id"], row["Tag.Name"]))
		if not currentSongRow:
			return None
		songDict: dict[Any, Any] = {**currentSongRow}
		album = AlbumInfo(
			songDict.pop("Album.Id", None),
			songDict.pop("Album.Name", None)
		)
		songDict.pop("Artist.Id", None)
		songDict.pop("Artist.Name", None)
		songDict.pop("Tag.Id", None)
		songDict.pop("Tag.Name", None)
		songDict.pop(sgar_isPrimaryArtist.description, None)
		return SongEditInfo(**songDict,
			album=album,
			primaryArtist=primaryArtist,
			artists=list(artists),
			tags=list(tags)
		)



	# 	result = [{**r} for r in records]
	# 	print("hi")
		# for row in rows:
		# 	yield FullSongInfo(
		# 		id=row["id"],

		# 	)
