
from typing import (
	Iterator,
	Optional,
	Union,
	cast,
	Iterable,
	Tuple
)
from musical_chairs_libs.dtos_and_utilities import (
	SavedNameString,
	SearchNameString,
	get_datetime,
	AlbumInfo,
	ArtistInfo,
	AlbumCreationInfo,
	AlreadyUsedError,
	AccountInfo,
	OwnerInfo,
	SongsAlbumInfo,
	SongListDisplayItem,
	normalize_opening_slash,
	PathDict,
	Lost,
	StationAlbumTuple,
	WrongPermissionsError
)
from .artist_service import ArtistService
from .path_rule_service import PathRuleService
from .stations_albums_service import StationsAlbumsService
from .current_user_provider import CurrentUserProvider
from sqlalchemy import (
	select,
	insert,
	update,
	Integer,
	func,
	delete,
	and_,
	literal,
	String
)
from sqlalchemy.sql.expression import (
	Update
)
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.schema import Column
from musical_chairs_libs.tables import (
	albums as albums_tbl,
	artists as artists_tbl,
	ab_name, ab_pk, ab_albumArtistFk, ab_year, ab_ownerFk, ab_versionnote,
	ar_name, ar_pk, ar_ownerFk,
	users as user_tbl, u_pk, u_username, u_displayName,
	songs as songs_tbl, sg_pk, sg_name, sg_albumFk, sg_path, sg_internalpath,
	sg_deletedTimstamp, sg_disc, sg_trackNum,
	song_artist as song_artist_tbl, sgar_songFk, sgar_artistFk, 
	sgar_isPrimaryArtist
)



class AlbumService:

	def __init__(
		self,
		conn: Connection,
		currentUserProvider: CurrentUserProvider,
		stationsAlbumsService: StationsAlbumsService,
		pathRuleService: PathRuleService,
		artistService: Optional[ArtistService]=None,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		if not artistService:
			artistService = ArtistService(
				conn,
				currentUserProvider,
				pathRuleService
			)
		self.conn = conn
		self.get_datetime = get_datetime
		self.artist_service = artistService
		self.path_rule_service = pathRuleService
		self.stations_albums_service = stationsAlbumsService
		self.current_user_provider = currentUserProvider

	def album_editor_user(
		self,
		albumkey: int,
	) -> AccountInfo:
		user = self.current_user_provider.get_scoped_user()
		if user.isadmin:
			return user
		owner = self.get_album_owner(albumkey)
		if owner.id == user.id:
			return user
		raise WrongPermissionsError()

	def get_albums(
		self,
		page: int = 0,
		pageSize: Optional[int]=None,
		albumKeys: Union[int, str, Iterable[int], None, Lost]=Lost(),
		artistKeys: Union[int, str, Iterable[int], None]=None,
		userId: Optional[int]=None,
		exactStrMatch: bool=False
	) -> Iterator[AlbumInfo]:
		album_owner = user_tbl.alias("albumowner")
		albumOwnerId = cast(Column[Integer], album_owner.c.pk)
		artist_owner = user_tbl.alias("artistowner")
		artistOwnerId = cast(Column[Integer], artist_owner.c.pk)
		
		query = select(
			ab_pk.label("id"),
			ab_name.label("name"),
			ab_year.label("year"),
			ab_versionnote.label("versionnote"),
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
		if type(albumKeys) == int or albumKeys is None:
			query = query.where(ab_pk == albumKeys)
		elif type(albumKeys) is str:
			if albumKeys:
				searchStr = SearchNameString.format_name_for_search(albumKeys)
				if exactStrMatch:
					query = query\
						.where(ab_name == searchStr)
				else:
					query = query\
						.where(ab_name.like(f"%{searchStr}%"))
		elif isinstance(albumKeys, Iterable):
			query = query.where(ab_pk.in_(albumKeys))
		if type(artistKeys) == int:
			query = query.where(ab_albumArtistFk == artistKeys)
		elif type(artistKeys) is str:
			if artistKeys:
				searchStr = SearchNameString.format_name_for_search(artistKeys)
				if exactStrMatch:
					query = query\
						.where(ar_name == searchStr)
				else:
					query = query\
						.where(ar_name.like(f"%{searchStr}%"))
		elif isinstance(artistKeys, Iterable):
			query = query.where(ab_albumArtistFk.in_(artistKeys))
		if userId:
			query = query.where(ab_ownerFk == userId)
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query).mappings()
		yield from (AlbumInfo(
			id=row["id"],
			name=row["name"],
			versionnote=row["versionnote"],
			owner=OwnerInfo(
				id=row["album.ownerid"],
				username=row["album.ownername"],
				displayname=row["album.ownerdisplayname"]
			),
			year=row["year"],
			albumartist=ArtistInfo(
				id=row["albumartistid"],
				name=row["artist.name"],
				owner=OwnerInfo(
					id=row["artist.ownerid"],
					username=row["artist.ownername"],
					displayname=row["artist.ownerdisplayname"]
				)
			) if row["albumartistid"] else None
			) for row in records)

	def get_album_owner(self, albumId: int) -> OwnerInfo:
		query = select(ab_ownerFk, u_username, u_displayName)\
			.select_from(albums_tbl)\
			.join(user_tbl, u_pk == ab_ownerFk)\
			.where(ab_pk == albumId)
		data = self.conn.execute(query).mappings().fetchone()
		if not data:
			return OwnerInfo(id=0,username="", displayname="")
		return OwnerInfo(
			id=data[ab_ownerFk],
			username=data[u_username],
			displayname=data[u_displayName]
		)
	
	def get_albums_page(
		self,
		page: int = 0,
		album: str = "",
		artist: str = "",
		limit: Optional[int]=None,
		user: Optional[AccountInfo]=None
	) -> Tuple[list[AlbumInfo], int]:
		result = list(self.get_albums(page, limit, album, artist))
		countQuery = select(func.count(1))\
			.select_from(albums_tbl)
		count = self.conn.execute(countQuery).scalar() or 0
		return result, count
	
	def get_song_counts(self) -> dict[int, int]:
		query = select(ab_pk, func.count(sg_pk))\
			.join(songs_tbl, sg_albumFk == ab_pk)\
			.where(sg_deletedTimstamp.is_(None))\
			.group_by(ab_pk)
		
		records = self.conn.execute(query)

		return {r[0]:r[1] for r in records}
	
	def get_album_songs(
		self,
		albumId: Optional[int],
		albumInfo: AlbumInfo,
	) -> Iterator[SongListDisplayItem]:
		songsQuery = select(
			sg_pk.label("id"),
			sg_name,
			sg_path,
			sg_internalpath,
			sg_trackNum.label("track"),
			sg_disc,
			coalesce[String](ar_name, "").label("artist"),
			literal(0).label("queuedtimestamp"),
			literal(albumInfo.name).label("album")
		)\
			.join(
				song_artist_tbl,
				and_(sgar_songFk == sg_pk, sgar_isPrimaryArtist == 1),
				isouter=True
			)\
			.join(
				artists_tbl,
				ar_pk == sgar_artistFk,
				isouter=True
			)\
			.where(sg_albumFk == albumId)\
			.where(sg_deletedTimstamp.is_(None))\
			.order_by(sg_disc, sg_trackNum)
		songsResult = self.conn.execute(songsQuery).mappings()
		pathRuleTree = None
		if self.current_user_provider.is_loggedIn():
			pathRuleTree = self.path_rule_service.get_rule_path_tree()

		songs = (
			SongListDisplayItem(
				**PathDict(dict(row), omitNulls=True, defaultValues={"name": "(blank)"})
			) for row in songsResult
		)
		if pathRuleTree:
			for song in songs:
				song.rules = list(pathRuleTree.valuesFlat(
						normalize_opening_slash(song.path))
					)
				yield song
		else:
			yield from songs


	def get_album(
			self,
			albumId: Optional[int],
		) -> Optional[SongsAlbumInfo]:
		albumInfo = next(self.get_albums(albumKeys=albumId), None)
		if not albumInfo:
			albumInfo = AlbumInfo(
				id=0,
				name="(Missing)",
				owner=OwnerInfo(
					id=0,
				)
			)
		
		songs = [*self.get_album_songs(albumId, albumInfo)]
		if albumId:
			stations = [
				*self.stations_albums_service.get_stations_by_album(albumId)
			]
		else:
			stations = []

		return SongsAlbumInfo(
			**albumInfo.model_dump(),
			songs=songs,
			stations=stations
		)


	def save_album(
		self,
		album: AlbumCreationInfo,
		albumId: Optional[int]=None
	) -> Optional[AlbumInfo]:
		if not album and not albumId:
			raise ValueError("No album info to save")
		user = self.current_user_provider.get_scoped_user()
		upsert = update if albumId else insert
		savedName = SavedNameString(album.name)
		stmt = upsert(albums_tbl).values(
			name = str(savedName),
			year = album.year,
			versionnote = album.versionnote,
			albumartistfk = album.albumartist.id if album.albumartist else None,
			lastmodifiedbyuserfk = user.id,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		owner = user
		if albumId and isinstance(stmt, Update):
			stmt = stmt.where(ab_pk == albumId)
			owner = self.get_album_owner(albumId)
		else:
			stmt = stmt.values(ownerfk = user.id)
		try:
			res = self.conn.execute(stmt)
		except IntegrityError:
			raise AlreadyUsedError.build_error(
				f"{album.name} is already used for artist.",
				"body->name"
			)
		affectedPk = albumId if albumId else res.lastrowid
		artist = next(self.artist_service.get_artists(
			userId=user.id,
			artistKeys=album.albumartist.id
		), None) if album.albumartist else None
		self.stations_albums_service.link_albums_with_stations(
			(StationAlbumTuple(affectedPk, t.id if t else None) 
				for t in (album.stations or [None]))
		)
		self.conn.commit()
		if res.rowcount == 0:
			return None
		return AlbumInfo(
			id=affectedPk,
			name=str(savedName),
			owner=owner,
			year=album.year,
			albumartist=artist,
			versionnote=album.versionnote
		)
		
		
	def delete_album(self, albumkey: int) -> int:
		if not albumkey:
			return 0
		delStmt = delete(albums_tbl).where(ab_pk == albumkey)
		delCount = self.conn.execute(delStmt).rowcount
		self.conn.commit()
		return delCount

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