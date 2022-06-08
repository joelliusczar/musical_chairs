#pyright: reportUnknownMemberType=false
from typing import Iterator, Optional, Union
from musical_chairs_libs.dtos import\
	SavedNameString,\
	SearchNameString,\
	SongItem,\
	SongItemPlumbing
from sqlalchemy import select, insert, update
from sqlalchemy.sql import ColumnCollection
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.simple_functions import\
	format_name_for_save,\
	format_name_for_search,\
	get_datetime
from musical_chairs_libs.tables import songs,\
	albums,\
	song_artist,\
	artists

class _Sentinel: pass

_missing = _Sentinel()

a: ColumnCollection = artists.columns
sg: ColumnCollection = songs.columns
ab: ColumnCollection = albums.columns
ar: ColumnCollection = artists.columns
sgar: ColumnCollection = song_artist.columns

class SongInfoService:

	def __init__(
		self,
		conn: Optional[Connection] = None,
		envManager: Optional[EnvManager]=None
	) -> None:
		if not conn:
			if not envManager:
				envManager = EnvManager()
			conn = envManager.get_configured_db_connection()
		self.conn = conn
		self.get_datetime = get_datetime

	def song_info(self, songPk: int) -> Optional[SongItem]:
		query = select(
			sg.pk,
			sg.name,
			ab.name.label("album"),
			ar.name.label("artist")
		)\
			.select_from(songs)\
			.join(albums, sg.albumFk == ab.pk, isouter=True)\
			.join(song_artist, sg.pk == sgar.songFk, isouter=True)\
			.join(artists, sgar.artistFk == ar.pk, isouter=True)\
			.where(sg.pk == songPk)\
			.limit(1)
		row = self.conn.execute(query).fetchone()
		if not row:
			return None
		return SongItem(
			row.pk, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			row.name, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			row.album, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			row.artist #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
		)

	def get_or_save_artist(self, name: Optional[str]) -> Optional[int]:
		if not name:
			return None
		cleanedName = format_name_for_save(name)
		query = select(a.pk).select_from(artists).where(a.name == cleanedName)
		row = self.conn.execute(query).fetchone()
		if row:
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		print(name)
		searchableName = format_name_for_search(name)
		timestamp = self.get_datetime().timestamp
		stmt = insert(artists).values(
			name = cleanedName,
			searchableName = searchableName,
			lastModifiedTimestamp = timestamp
		)
		res = self.conn.execute(stmt)
		insertedPk: int = res.lastrowid
		return insertedPk

	def get_or_save_album(
		self,
		name: Optional[str],
		artistFk: Optional[int]=None,
		year: Optional[int]=None
	) -> Optional[int]:
		if not name:
			return None
		cleanedName = format_name_for_save(name)
		query = select(a.pk).select_from(albums).where(a.name == cleanedName)
		row = self.conn.execute(query).fetchone()
		if row:
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		print(name)
		searchableName = format_name_for_search(name)
		timestamp = self.get_datetime().timestamp
		stmt = insert(albums).values(
			name = cleanedName,
			searchableName = searchableName,
			albumArtistFk = artistFk,
			year = year,
			lastModifiedTimestamp = timestamp
		)
		res = self.conn.execute(stmt)
		insertedPk: int = res.lastrowid
		return insertedPk

	def get_song_refs(
		self,
		title: Union[Optional[SavedNameString], _Sentinel]=_missing,
		page: int=0,
		pageSize: Optional[int]=None,
	) -> Iterator[SongItemPlumbing]:
		query = select(
			sg.pk,
			sg.path,
			sg.name
		).select_from(songs)
		if type(title) is SavedNameString:
			#allow null through
			cleanedName = str(title) if title else None
			query = query.where(sg.title == cleanedName)
		if pageSize:
			offset = page * pageSize
			limit = (page + 1) * pageSize
			query = query.limit(limit).offset(offset)
		records = self.conn.execute(query)
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield SongItemPlumbing(
					row.pk, #pyright: ignore [reportUnknownArgumentType]
					row.path, #pyright: ignore [reportUnknownArgumentType]
					SavedNameString(row.name) #pyright: ignore [reportUnknownArgumentType]
				)

	def update_song_info(self, songInfo: SongItemPlumbing) -> int:
		saveName = str(songInfo.name)
		searchableName = str(SearchNameString(saveName))
		timestamp = self.get_datetime().timestamp
		songUpdate = update(songs) \
				.where(sg.pk == songInfo.id) \
				.values(
					name = saveName,
					searchableName = searchableName,
					albumFk = songInfo.albumPk,
					track = songInfo.track,
					disc = songInfo.disc,
					bitrate = songInfo.bitrate,
					comment = songInfo.comment,
					genre = songInfo.genre,
					duration = songInfo.duration,
					lastModifiedTimestamp = timestamp,
					lastModifiedByUserFk = None
				)
		count: int = self.conn.execute(songUpdate).rowcount
		try:
			songArtistInsert = insert(song_artist)\
				.values(songFk = songInfo.id, artistFk = songInfo.artistPk)
			self.conn.execute(songArtistInsert)
		except IntegrityError: pass
		return count