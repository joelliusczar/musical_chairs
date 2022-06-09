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
	get_datetime
from musical_chairs_libs.tables import songs,\
	albums,\
	song_artist,\
	artists

class _Sentinel: pass

_missing = _Sentinel()

sg: ColumnCollection = songs.columns
ab: ColumnCollection = albums.columns
ar: ColumnCollection = artists.columns
sgar: ColumnCollection = song_artist.columns

class SongInfoService:

	def __init__(
		self,
		conn: Optional[Connection]=None,
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

	def get_or_save_artist(self, name: Optional[SavedNameString]) -> Optional[int]:
		if not name:
			return None
		#we're deliberately querying by the displayable string
		#since it's conceivable to have distinct artist names that
		#use different versions of same base character symbol
		query = select(ar.pk).select_from(artists).where(ar.name == str(name))
		row = self.conn.execute(query).fetchone()
		if row:
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		print(name)
		stmt = insert(artists).values(
			name = str(name),
			searchableName = SearchNameString.format_name_for_search(str(name)),
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		res = self.conn.execute(stmt)
		insertedPk: int = res.lastrowid
		return insertedPk

	def get_or_save_album(
		self,
		name: Optional[SavedNameString],
		artistFk: Optional[int]=None,
		year: Optional[int]=None
	) -> Optional[int]:
		if not name:
			return None
		#we're deliberately querying by the displayable string
		#since it's conceivable to have distinct album names that
		#use different versions of same base character symbol
		query = select(ab.pk).select_from(albums).where(ab.name == str(name))
		row = self.conn.execute(query).fetchone()
		if row:
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		print(name)
		stmt = insert(albums).values(
			name = str(name),
			searchableName = SearchNameString.format_name_for_search(str(name)),
			albumArtistFk = artistFk,
			year = year,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		res = self.conn.execute(stmt)
		insertedPk: int = res.lastrowid
		return insertedPk

	def get_song_refs(
		self,
		songName: Union[Optional[SavedNameString], _Sentinel]=_missing,
		page: int=0,
		pageSize: Optional[int]=None,
	) -> Iterator[SongItemPlumbing]:
		query = select(
			sg.pk,
			sg.path,
			sg.name
		).select_from(songs)
		if type(songName) is SavedNameString or songName is None:
			#allow null through
			cleanedName = str(songName) if songName else None
			query = query.where(sg.name == cleanedName)
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
		timestamp = self.get_datetime().timestamp()
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
					sampleRate = songInfo.sampleRate,
					lastModifiedTimestamp = timestamp,
					lastModifiedByUserFk = None
				)
		count: int = self.conn.execute(songUpdate).rowcount
		try:
			songComposerInsert = insert(song_artist)\
				.values(songFk = songInfo.id, artistFk = songInfo.artistPk)
			self.conn.execute(songComposerInsert)
		except IntegrityError: pass
		try:
			songComposerInsert = insert(song_artist)\
				.values(
					songFk = songInfo.id,
					artistFk = songInfo.composerPk,
					comment = "composer"
				)
			self.conn.execute(songComposerInsert)
		except IntegrityError: pass
		return count