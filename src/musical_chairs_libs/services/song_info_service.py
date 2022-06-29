#pyright: reportUnknownMemberType=false
from typing import\
	Iterator,\
	Optional,\
	Union,\
	Any,\
	cast,\
	Iterable,\
	Tuple
from musical_chairs_libs.dtos_and_utilities import\
	SavedNameString,\
	SongItem,\
	SongItemPlumbing,\
	SongTreeNode,\
	Tag,\
	SearchNameString,\
	SongBase,\
	get_datetime,\
	Sentinel,\
	missing
from sqlalchemy import select, insert, update, func, delete
from sqlalchemy.sql import ColumnCollection
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
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
	songs_tags as songs_tags_tbl


sg: ColumnCollection = songs_tbl.columns
ab: ColumnCollection = albums_tbl.columns
tg: ColumnCollection = tags_tbl.columns #pyright: ignore [reportUnknownMemberType]
st: ColumnCollection = stations_tbl.columns #pyright: ignore [reportUnknownMemberType]
ar: ColumnCollection = artists_tbl.columns
sgar: ColumnCollection = song_artist_tbl.columns
sgtg: ColumnCollection = songs_tags_tbl.columns
sttg: ColumnCollection = stations_tags_tbl.columns #pyright: ignore [reportUnknownMemberType]

sg_pk: Any = sg.pk
sg_name: Any = sg.name
sg_path: Any = sg.path
tg_pk: Any = tg.pk #pyright: ignore [reportUnknownMemberType]
tg_name: Any = tg.name #pyright: ignore [reportUnknownMemberType]
st_pk: Any = st.pk #pyright: ignore [reportUnknownMemberType]
st_name: Any = st.name #pyright: ignore [reportUnknownMemberType]
sttg_tagFk: Any = sttg.tagFk #pyright: ignore [reportUnknownMemberType]
sttg_stationFk: Any = sttg.stationFk #pyright: ignore [reportUnknownMemberType]
sgtg_tagFk: Any = sgtg.tagFk
sgtg_songFk: Any = sgtg.songFk

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

	def song_info(self, songPk: int) -> Optional[SongItem]:
		query = select(
			sg.pk,
			sg.name,
			ab.name.label("album"),
			ar.name.label("artist")
		)\
			.select_from(songs_tbl)\
			.join(albums_tbl, sg.albumFk == ab.pk, isouter=True)\
			.join(song_artist_tbl, sg.pk == sgar.songFk, isouter=True)\
			.join(artists_tbl, sgar.artistFk == ar.pk, isouter=True)\
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
		query = select(ar.pk).select_from(artists_tbl).where(ar.name == savedName)
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

	def get_or_save_album(
		self,
		name: Optional[str],
		artistFk: Optional[int]=None,
		year: Optional[int]=None
	) -> Optional[int]:
		if not name:
			return None
		savedName = SavedNameString.format_name_for_save(name)
		query = select(ab.pk).select_from(albums_tbl).where(ab.name == savedName)
		if artistFk:
			query = query.where(ab.albumArtistFk == artistFk)
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
	) -> Iterator[SongItemPlumbing]:
		query = select(
			sg.pk,
			sg.path,
			sg.name
		).select_from(songs_tbl)
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
					id=row.pk, #pyright: ignore [reportUnknownArgumentType]
					path=row.path, #pyright: ignore [reportUnknownArgumentType]
					name=SavedNameString.format_name_for_save(row.name) #pyright: ignore [reportUnknownArgumentType]
				)

	def update_song_info(self, songInfo: SongItemPlumbing) -> int:
		savedName =  SavedNameString.format_name_for_save(songInfo.name)
		timestamp = self.get_datetime().timestamp()
		songUpdate = update(songs_tbl) \
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
			songComposerInsert = insert(song_artist_tbl)\
				.values(songFk = songInfo.id, artistFk = songInfo.artistPk)
			self.conn.execute(songComposerInsert)
		except IntegrityError: pass
		try:
			songComposerInsert = insert(song_artist_tbl)\
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