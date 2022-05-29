#pyright: reportUnknownMemberType=false
from typing import Optional
from musical_chairs_libs.dtos import SongItem
from sqlalchemy import select
from sqlalchemy.sql import ColumnCollection
from sqlalchemy.engine import Connection
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.tables import songs,\
	albums,\
	song_artist,\
	artists

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

	def song_info(self, songPk: int) -> Optional[SongItem]:
		sg: ColumnCollection = songs.columns
		ab: ColumnCollection = albums.columns
		ar: ColumnCollection = artists.columns
		sgar: ColumnCollection = song_artist.columns
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
