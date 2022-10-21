#pyright: reportUnknownMemberType=false
from typing import\
	Iterator,\
	Optional,\
	Union,\
	cast,\
	Iterable,\
	Any,\
	Tuple,\
	Set
from musical_chairs_libs.dtos_and_utilities import\
	SavedNameString,\
	SongListDisplayItem,\
	ScanningSongItem,\
	SongTreeNode,\
	Tag,\
	SearchNameString,\
	get_datetime,\
	Sentinel,\
	missing,\
	AlbumInfo,\
	ArtistInfo,\
	SongEditInfo,\
	build_error_obj,\
	AlbumCreationInfo,\
	SongTagTuple,\
	SongArtistTuple
from sqlalchemy import select, insert, update, func, delete
from sqlalchemy.sql.expression import Tuple as dbTuple
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from musical_chairs_libs.errors import AlreadyUsedError
from .env_manager import EnvManager
from .tag_service import TagService
from sqlalchemy.engine.row import Row
from dataclasses import asdict, fields
from itertools import chain
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

	def get_songIds(
		self,
		page: int = 0,
		pageSize: Optional[int]=None,
		stationId: Union[Optional[int], Sentinel]=missing,
		stationName: Union[Optional[str], Sentinel]=missing,
		tagId: Union[Optional[int], Sentinel]=missing,
		tagIds: Optional[Iterable[int]]=None,
		songIds: Optional[Iterable[int]]=None
	) -> Iterator[int]:
		offset = page * pageSize if pageSize else 0
		query = select(sg_pk).select_from(songs_tbl)
		#add joins
		if stationId or tagId or stationName or tagIds:
			query = query.join(songs_tags_tbl, sgtg_songFk == sg_pk)
			if stationId:
				query = query.join(stations_tags_tbl, sgtg_tagFk == sttg_tagFk)
			elif stationName and type(stationName) is str:
				query = query.join(stations_tags_tbl, sgtg_tagFk == sttg_tagFk)\
					.join(stations_tbl, sttg_stationFk == st_pk)
		#add wheres
		if tagId:
			query = query.where(sgtg_tagFk == tagId)
		elif tagIds:
			query = query.where(sgtg_tagFk.in_(tagIds))
		if stationId:
			query = query.where(sttg_stationFk == stationId)
		elif stationName and type(stationName) is str:
			searchStr = SearchNameString.format_name_for_search(stationName)
			query = query.where(
				func.format_name_for_search(st_name).like(f"%{searchStr}%")
			)
		if songIds:
			query = query.where(sg_pk.in_(songIds))
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (cast(int, row["pk"]) for row in cast(Iterable[Row],records))

	def get_song_tags(
		self,
		songId: Union[int, Sentinel]=missing,
		songIds: Optional[Iterable[int]]=None,
		tagId: Union[Optional[int], Sentinel]=missing,
		tagIds: Optional[Iterable[int]]=None
	) -> Iterable[SongTagTuple]:
		query = select(
			sgtg_tagFk,
			sgtg_songFk
		)

		if type(songId) == int:
			query = query.where(sgtg_songFk == songId)
		elif isinstance(songIds, Iterable):
			query = query.where(sgtg_songFk.in_(songIds))
		if type(tagId) == int:
			query = query.where(sgtg_tagFk == tagId)
		elif isinstance(tagIds, Iterable):
			query = query.where(sgtg_tagFk.in_(tagIds))
		query = query.order_by(sgtg_songFk)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (SongTagTuple(
				cast(int, row[sgtg_songFk]),
				cast(int, row[sgtg_tagFk]),
				True
			)
			for row in cast(Iterable[Row],records))

	def remove_songs_for_tags(
		self,
		songTags: Iterable[Union[SongTagTuple, Tuple[int, int]]],
	) -> int:
		songTags = songTags or []
		delStmt = delete(songs_tags_tbl)\
			.where(dbTuple(sgtg_songFk, sgtg_tagFk).in_(songTags))
		return cast(int, self.conn.execute(delStmt).rowcount) #pyright: ignore [reportUnknownMemberType]

	def validate_song_tags(
		self,
		songTags: Iterable[SongTagTuple]
	) -> Iterable[SongTagTuple]:
		if not songTags:
			return iter([])
		query = select(
			sg_pk,
			tg_pk
		).where(dbTuple(sg_pk, tg_pk).in_(songTags))

		records = self.conn.execute(query)
		yield from (SongTagTuple(
			cast(int, row[sg_pk]),
			cast(int, row[tg_pk])
		) for row in cast(Iterable[Row],records))

	def link_songs_with_tags(
		self,
		songTags: Iterable[SongTagTuple],
		userId: Optional[int]=None
	) -> Iterable[SongTagTuple]:
		if not songTags:
			return []
		uniquePairs = set(self.validate_song_tags(songTags))
		if not uniquePairs:
			return []
		existingPairs = set(self.get_song_tags(
			songIds={st.songId for st in uniquePairs}
		))
		outPairs = existingPairs - uniquePairs
		inPairs = uniquePairs - existingPairs
		self.remove_songs_for_tags(outPairs)
		if not inPairs: #if no songs - artist have been linked
			return existingPairs - outPairs
			#return (a for a in existingArtists if a.id not in outArtistIds)
		params = [{
			"songFk": p.songId,
			"tagFk": p.tagId,
			"lastModifiedByUserFk": userId,
			"lastModifiedTimestamp": self.get_datetime().timestamp()
		} for p in inPairs]
		stmt = insert(songs_tags_tbl)
		self.conn.execute(stmt, params) #pyright: ignore [reportUnknownMemberType]
		return self.get_song_tags(
			songIds={st.songId for st in uniquePairs}
		)

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
			.join(artists_tbl, ar_pk == ab_albumArtistFk, isouter=True)
		if type(albumId) == int:
			query = query.where(ab_pk == albumId)
		elif isinstance(albumIds, Iterable):
			query = query.where(ab_pk.in_(albumIds))
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
		#check speficially if instance because [] is falsy
		elif isinstance(artistIds, Iterable) :
			query = query.where(ar_pk.in_(artistIds))
		elif type(artistName) is str:
			searchStr = SearchNameString.format_name_for_search(artistName)
			query = query\
				.where(func.format_name_for_search(ar_name).like(f"%{searchStr}%"))
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (ArtistInfo(**row) for row in records) #pyright: ignore [reportUnknownVariableType, reportUnknownArgumentType]

	def get_song_artists(
		self,
		songId: Union[int, Sentinel]=missing,
		songIds: Optional[Iterable[int]]=None,
		artistId: Union[Optional[int], Sentinel]=missing,
		artistIds: Optional[Iterable[int]]=None
	) -> Iterable[SongArtistTuple]:
		query = select(
			sgar_artistFk,
			sgar_songFk,
			sgar_isPrimaryArtist
		)

		if type(songId) == int:
			query = query.where(sgar_songFk == songId)
		elif isinstance(songIds, Iterable):
			query = query.where(sgar_songFk.in_(songIds))
		if type(artistId) == int:
			query = query.where(sgar_artistFk == artistId)
		elif isinstance(artistIds, Iterable):
			query = query.where(sgar_artistFk.in_(artistIds))
		query = query.order_by(sgar_songFk)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (SongArtistTuple(
				cast(int, row[sgar_songFk]),
				cast(int, row[sgar_artistFk]),
				cast(bool, row[sgar_isPrimaryArtist])
			)
			for row in cast(Iterable[Row],records))


	def remove_songs_for_artists(
		self,
		songArtists: Iterable[Union[SongArtistTuple, Tuple[int, int]]],
	) -> int:
		songArtists = songArtists or []
		delStmt = delete(song_artist_tbl)\
			.where(dbTuple(sgar_songFk, sgar_artistFk).in_(songArtists))
		count = cast(int, self.conn.execute(delStmt).rowcount) #pyright: ignore [reportUnknownMemberType]
		return count

	def validate_song_artists(
		self,
		songArtists: Iterable[SongArtistTuple]
	) -> Iterable[SongArtistTuple]:
		if not songArtists:
			return iter([])
		songArtistsSet = set(songArtists)
		primaryArtistId = next(
			(sa.artistId for sa in songArtistsSet if sa.isPrimaryArtist),
			-1
		)
		query = select(
			sg_pk,
			ar_pk
		).where(dbTuple(sg_pk, ar_pk).in_(songArtistsSet))

		records = self.conn.execute(query)
		yield from (SongArtistTuple(
			cast(int, row[sg_pk]),
			cast(int, row[ar_pk]),
			isPrimaryArtist=cast(int, row[ar_pk]) == primaryArtistId
		) for row in cast(Iterable[Row],records))

	def link_songs_with_artists(
		self,
		songArtists: Iterable[SongArtistTuple],
		userId: Optional[int]=None
	) -> Iterable[SongArtistTuple]:
		if not songArtists:
			return []
		uniquePairs = set(self.validate_song_artists(songArtists))
		if len([sa for sa in uniquePairs if sa.isPrimaryArtist]) > 1:
			raise ValueError("Only one artist can be the primary artist")
		existingPairs = set(self.get_song_artists(
			songIds={sa.songId for sa in uniquePairs}
		))
		outPairs = existingPairs - uniquePairs
		inPairs = uniquePairs - existingPairs
		self.remove_songs_for_artists(outPairs)
		if not inPairs: #if no songs - artist have been linked
			return existingPairs - outPairs
		params = [{
			"songFk": p.songId,
			"artistFk": p.artistId,
			"isPrimaryArtist": p.isPrimaryArtist,
			"lastModifiedByUserFk": userId,
			"lastModifiedTimestamp": self.get_datetime().timestamp()
		} for p in inPairs]
		stmt = insert(song_artist_tbl)
		self.conn.execute(stmt, params) #pyright: ignore [reportUnknownMemberType]
		return self.get_song_artists(
			songIds={sa.songId for sa in uniquePairs}
		)

	def prepare_song_row_for_model(self, row: Row) -> dict[str, Any]:
		songDict: dict[Any, Any] = {**row}
		albumArtistId = songDict.pop("album.albumArtistId", None)
		albumArtistName = songDict.pop("album.albumArtist.name", "")
		album = AlbumInfo(
			songDict.pop("album.id", None),
			songDict.pop("album.name", None),
			songDict.pop("album.year", None),
			ArtistInfo(
				albumArtistId,
				albumArtistName
			) if albumArtistId else None
		)
		songDict["album"] = album
		songDict.pop("artist.id", None)
		songDict.pop("artist.name", None)
		songDict.pop("tag.id", None)
		songDict.pop("tag.name", None)
		songDict.pop(sgar_isPrimaryArtist.description, None)
		return songDict


	def get_songs_for_edit(
		self,
		songIds: Iterable[int]
	) -> Iterator[SongEditInfo]:
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
			func.max(ab_pk).label("album.id"),
			func.max(ab_name).label("album.name"),
			func.max(ab_year).label("album.year"),
			func.max(ab_albumArtistFk).label("album.albumArtistId"),
			func.max(album_artist.c.name).label("album.albumArtist.name"),
			sgar_isPrimaryArtist,
			ar_pk.label("artist.id"),
			ar_name.label("artist.name"),
			tg_pk.label("tag.id"),
			tg_name.label("tag.name"),
		).select_from(songs_tbl)\
				.join(song_artist_tbl, sg_pk == sgar_songFk, isouter=True)\
				.join(artists_tbl, ar_pk == sgar_artistFk, isouter=True)\
				.join(albums_tbl, sg_albumFk == ab_pk, isouter=True)\
				.join(songs_tags_tbl, sg_pk == sgtg_songFk, isouter=True)\
				.join(tags_tbl, sgtg_tagFk ==  tg_pk, isouter=True)\
				.join(album_artist, ab_albumArtistFk == album_artist.c.pk, isouter=True)\
				.group_by(
					"artist.id",
					"artist.name",
					sgar_isPrimaryArtist,
					"tag.id",
					"tag.name",
					)\
				.where(sg_pk.in_(songIds))\
				.order_by(sg_pk)
		records = self.conn.execute(query).fetchall()
		currentSongRow = None
		artists: set[ArtistInfo] = set()
		tags: set[Tag] = set()
		primaryArtist: Optional[ArtistInfo] = None
		for row in records:
			if not currentSongRow:
				currentSongRow = row
			elif row["id"] != currentSongRow["id"]:
				songDict = self.prepare_song_row_for_model(currentSongRow)
				yield SongEditInfo(**songDict,
					primaryArtist=primaryArtist,
					artists=list(artists),
					tags=list(tags)
				)
				currentSongRow = row
				artists =  set()
				tags = set()
				primaryArtist = None
			if row[sgar_isPrimaryArtist]:
				primaryArtist = ArtistInfo(
					row["artist.id"],
					row["artist.name"]
				)
			elif row["artist.id"]:
				artists.add(ArtistInfo(
						row["artist.id"],
						row["artist.name"]
					)
				)
			if row["tag.id"]:
				tags.add(Tag(row["tag.id"], row["tag.name"]))
		if currentSongRow:
			songDict = self.prepare_song_row_for_model(currentSongRow)
			yield SongEditInfo(**songDict,
					primaryArtist=primaryArtist,
					artists=list(artists),
					tags=list(tags)
				)

	def save_songs(
		self,
		ids: Iterable[int],
		songInfo: SongEditInfo,
		userId: Optional[int]=None,
		touched: Optional[Set[str]]=None
	) -> Iterator[SongEditInfo]:
		if not ids:
			return iter([])
		if not songInfo:
			return self.get_songs_for_edit(ids)
		if touched == None:
			touched = {f.name for f in fields(SongEditInfo)}
		songInfo.name = str(SavedNameString(songInfo.name))
		songInfoDict = asdict(songInfo)
		songInfoDict.pop("artists", None)
		songInfoDict.pop("primaryArtist", None)
		songInfoDict.pop("tags", None)
		songInfoDict.pop("id", None)
		songInfoDict.pop("album", None)
		songInfoDict.pop("covers", None)
		songInfoDict["albumFk"] = songInfo.album.id if songInfo.album else None
		songInfoDict["lastModifiedByUserFk"] = userId
		songInfoDict["lastModifiedTimestamp"] = self.get_datetime().timestamp()
		if "album" in touched:
			touched.add("albumFk")
		stmt = update(songs_tbl).values(
			**{k:v for k,v in songInfoDict.items() if k in touched}
		).where(sg_pk.in_(ids))
		self.conn.execute(stmt)
		if "artists" in touched or "primaryArtist" in touched:
			self.link_songs_with_artists(
				chain(
					(SongArtistTuple(sid, a.id) for a in songInfo.artists or []
						for sid in ids
					) if "artists" in touched else (),
					#we can't use allArtists here bc we need the primaryArtist selection
					(SongArtistTuple(sid, songInfo.primaryArtist.id, True) for sid in ids)
						if "primaryArtist" in touched and songInfo.primaryArtist else ()
				),
				userId
			)
		if "tags" in touched:
			self.link_songs_with_tags(
				(SongTagTuple(songInfo.id, t.id) for t in (songInfo.tags or [])),
				userId
			)

		return self.get_songs_for_edit(ids)
