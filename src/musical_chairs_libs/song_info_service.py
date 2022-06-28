#pyright: reportUnknownMemberType=false
from typing import Iterator, Optional, Union, Any, cast
from musical_chairs_libs.dtos import\
	SavedNameString,\
	SongItem,\
	SongItemPlumbing,\
	SongTreeNode
from sqlalchemy import select, insert, update, func
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

sg_pk: Any = sg.pk
sg_name: Any = sg.name,
sg_path: Any = sg.path

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

	def get_or_save_artist(self, name: Optional[str]) -> Optional[int]:
		if not name:
			return None
		savedName = SavedNameString.format_name_for_save(name)
		query = select(ar.pk).select_from(artists).where(ar.name == savedName)
		row = self.conn.execute(query).fetchone()
		if row:
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		print(name)
		stmt = insert(artists).values(
			name = savedName,
			lastModifiedTimestamp = self.get_datetime().timestamp()
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
		savedName = SavedNameString.format_name_for_save(name)
		query = select(ab.pk).select_from(albums).where(ab.name == savedName)
		if artistFk:
			query = query.where(ab.albumArtistFk == artistFk)
		row = self.conn.execute(query).fetchone()
		if row:
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		print(name)
		stmt = insert(albums).values(
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
		songName: Union[Optional[str], _Sentinel]=_missing,
		page: int=0,
		pageSize: Optional[int]=None,
	) -> Iterator[SongItemPlumbing]:
		query = select(
			sg.pk,
			sg.path,
			sg.name
		).select_from(songs)
		if type(songName) is str or songName is None:
			#allow null through
			savedName = SavedNameString.format_name_for_save(songName) if songName\
				else None
			query = query.where(sg.name == savedName)
		if pageSize:
			offset = page * pageSize
			query = query.limit(pageSize).offset(offset)
		records = self.conn.execute(query)
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield SongItemPlumbing(
					row.pk, #pyright: ignore [reportUnknownArgumentType]
					row.path, #pyright: ignore [reportUnknownArgumentType]
					SavedNameString.format_name_for_save(row.name) #pyright: ignore [reportUnknownArgumentType]
				)

	def update_song_info(self, songInfo: SongItemPlumbing) -> int:
		savedName =  SavedNameString.format_name_for_save(songInfo.name)
		timestamp = self.get_datetime().timestamp()
		songUpdate = update(songs) \
				.where(sg.pk == songInfo.id) \
				.values(
					name = savedName,
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

	def song_ls(self, prefix: Optional[str] = "") -> Iterator[SongTreeNode]:
		query = select(
				func.next_directory_level(sg_path, prefix).label("prefix"),
				func.min(sg.name).label("name"),
				func.count(sg_pk).label("totalChildCount"),
				func.max(sg_pk).label("pk"),
				func.max(sg_path).label("control_path")
		).where(sg_path.like(f"{prefix}%"))\
			.group_by(func.next_directory_level(sg_path, prefix))
		records = self.conn.execute(query)
		for row in records: #pyright: ignore [reportUnknownVariableType]
			if row["control_path"] == row["prefix"]:
				yield SongTreeNode(
					cast(str, row["prefix"]),
					cast(int, row["totalChildCount"]),
					cast(int, row["pk"]),
					cast(str, row["name"])
				)
			else:
				yield SongTreeNode(
					cast(str, row["prefix"]),
					cast(int, row["totalChildCount"])
				)