#pyright: reportMissingTypeStubs=false
import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.tables as tbl
from typing import (
	Iterator,
	Optional,
	cast,
	Iterable,
	Tuple
)
from musical_chairs_libs.dtos_and_utilities import (
	SavedNameString,
	SearchNameString,
	AlbumInfo,
	ArtistInfo,
	AlbumCreationInfo,
	AlreadyUsedError,
	get_album_owner_roles,
	get_datetime,
	SongsAlbumInfo,
	SongListDisplayItem,
	normalize_opening_slash,
	PathDict,
	Lost,
	SimpleQueryParameters,
	StationAlbumTuple,
	UserRoleDef,
)
from .artist_service import ArtistService
from .path_rule_service import PathRuleService
from .stations_albums_service import StationsAlbumsService
from .current_user_provider import CurrentUserProvider
from sqlalchemy import (
	select,
	insert,
	update,
	literal as dbLiteral,
	Integer,
	func,
	delete,
	and_,
	or_,
	literal,
	String
)
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.schema import Column
from musical_chairs_libs.tables import (
	artists as artists_tbl, ar_name, ar_pk, ar_ownerFk,
	albums as albums_tbl, ab_name, ab_pk, ab_albumArtistFk, ab_year, ab_ownerFk, 
	ab_versionnote,
	users as user_tbl, u_pk, u_username, u_displayName,
	songs as songs_tbl, sg_pk, sg_name, sg_albumFk, sg_path, sg_internalpath,
	sg_deletedTimstamp, sg_disc, sg_trackNum,
	song_artist as song_artist_tbl, sgar_songFk, sgar_artistFk, 
	sgar_isPrimaryArtist
)

album_owner = user_tbl.alias("albumowner")
albumOwnerId = cast(Column[Integer], album_owner.c.pk)
albumOwnerPublicToken = cast(Column[String], album_owner.c.publictoken)
artist_owner = user_tbl.alias("artistowner")
artistOwnerId = cast(Column[Integer], artist_owner.c.pk)
artistOwnerPublicToken = cast(Column[String], artist_owner.c.publictoken)


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


	def get_albums_query(
		self,
		albumKeys: int | str | Iterable[int] | None | Lost=Lost(),
		artistKeys: int | str | Iterable[int] | None=None,
		exactStrMatch: bool=False
	):
		query = albums_tbl\
			.join(artists_tbl, ar_pk == ab_albumArtistFk, isouter=True) \
			.join(album_owner, albumOwnerId == ab_ownerFk, isouter=True) \
			.join(artist_owner, artistOwnerId == ar_ownerFk, isouter=True)\
			.select()
		if type(albumKeys) == int or albumKeys is None:
			query = query.where(ab_pk == albumKeys)
		elif type(albumKeys) is str:
			if albumKeys:
				if exactStrMatch:
					searchStr = SearchNameString.format_name_for_search(albumKeys)
					query = query\
						.where(ab_name == searchStr)
				else:
					searchStr = SearchNameString.format_name_for_like(albumKeys)
					query = query\
						.where(ab_name.like(f"%{searchStr}%", escape="\\"))
		elif isinstance(albumKeys, Iterable):
			query = query.where(ab_pk.in_(albumKeys))
		if type(artistKeys) == int:
			query = query.where(ab_albumArtistFk == artistKeys)
		elif type(artistKeys) is str:
			if artistKeys:		
				if exactStrMatch:
					searchStr = SearchNameString.format_name_for_search(artistKeys)
					query = query\
						.where(ar_name == searchStr)
				else:
					searchStr = SearchNameString.format_name_for_like(artistKeys)
					query = query\
						.where(ar_name.like(f"%{searchStr}%", escape="\\"))
		elif isinstance(artistKeys, Iterable):
			query = query.where(ab_albumArtistFk.in_(artistKeys))
		user = self.current_user_provider.current_user(
			optional=True
		)
		if user:
			query = query.where(or_(
				ab_ownerFk == user.id,
				dbLiteral(user.isadmin),
				dbLiteral(user.has_site_roles(UserRoleDef.ALBUM_EDIT))
			))

		return query
		

	def get_albums(
		self,
		page: int = 0,
		pageSize: Optional[int]=None,
		albumKeys: int | str | Iterable[int] | None | Lost=Lost(),
		artistKeys: int | str | Iterable[int] | None=None,
		exactStrMatch: bool=False
	) -> Iterator[AlbumInfo]:
		
		query = self.get_albums_query(albumKeys, artistKeys, exactStrMatch)\
		.with_only_columns(
			ab_pk.label("id"),
			ab_name.label("name"),
			ab_year.label("year"),
			ab_versionnote.label("versionnote"),
			ab_albumArtistFk.label("albumartistid"),
			ab_ownerFk.label("album>owner>id"),
			album_owner.c.username.label("album>owner>username"),
			album_owner.c.displayname.label("album>owner>displayname"),
			album_owner.c.publictoken.label("album>owner>publictoken"),
			ar_name.label("artist>name"),
			ar_ownerFk.label("artist>owner>id"),
			artist_owner.c.username.label("artist>owner>username"),
			artist_owner.c.displayname.label("artist>owner>displayname"),
			artist_owner.c.publictoken.label("artist>owner>publictoken"),
		)
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		with dtos.open_transaction(self.conn):
			records = self.conn.execute(query).mappings().fetchall()
			ownerRules = [*get_album_owner_roles()]
			userId = self.current_user_provider.optional_user_id()
			yield from (AlbumInfo(
				id=row["id"],
				name=row["name"],
				versionnote=row["versionnote"],
				owner=dtos.User(
					id=row["album>owner>id"],
					username=row["album>owner>username"],
					displayname=row["album>owner>displayname"],
					publictoken=row["album>owner>publictoken"]
				),
				year=row["year"],
				albumartist=ArtistInfo(
					id=row["albumartistid"],
					name=row["artist>name"],
					owner=dtos.User(
						id=row["artist>owner>id"],
						username=row["artist>owner>username"],
						displayname=row["artist>owner>displayname"],
						publictoken=row["artist>owner>publictoken"]
					)
				) if row["albumartistid"] else None,
				rules=ownerRules if row["album>owner>id"] == userId else []
				) for row in records)


	def get_album_owner(self, albumId: int) -> dtos.User:
		query = select(ab_ownerFk, u_username, u_displayName, tbl.u_publictoken)\
			.select_from(albums_tbl)\
			.join(user_tbl, u_pk == ab_ownerFk)\
			.where(ab_pk == albumId)
		with dtos.open_transaction(self.conn):
			data = self.conn.execute(query).mappings().fetchone()
			if not data:
				return dtos.User(id=0,username="", displayname="", publictoken="")
			return dtos.User(
				id=data[ab_ownerFk],
				username=data[u_username],
				displayname=data[u_displayName],
				publictoken=data[tbl.u_publictoken]
		)


	def get_albums_page(
		self,
		queryParams: SimpleQueryParameters,
		album: str = "",
		artist: str = "",
	) -> Tuple[list[AlbumInfo], int]:
		with dtos.open_transaction(self.conn):
			result = list(self.get_albums(
				queryParams.page,
				queryParams.limit,
				album,
				artist
			))
			countQuery = self.get_albums_query(album, artist)\
				.with_only_columns(func.count(1))
			count = self.conn.execute(countQuery).scalar() or 0
			return result, count


	def get_song_counts(self) -> dict[str, int]:
		query = select(ab_pk, func.count(sg_pk))\
			.join(songs_tbl, sg_albumFk == ab_pk)\
			.where(sg_deletedTimstamp.is_(None))\
			.group_by(ab_pk)
		with dtos.open_transaction(self.conn):
			records = self.conn.execute(query).fetchall()

			return {dtos.encode_id(r[0]):r[1] for r in records}


	def get_album_songs(
		self,
		albumId: Optional[int],
		albumInfo: AlbumInfo,
	) -> list[SongListDisplayItem]:
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
		with dtos.open_transaction(self.conn):
			songsResult = self.conn.execute(songsQuery).mappings().fetchall()
			pathRuleTree = None
			if self.current_user_provider.is_loggedIn():
				pathRuleTree = self.path_rule_service.get_rule_path_tree()

			songs = [
				SongListDisplayItem(
					**PathDict(
						dict(row),
						omitNulls=True,
						defaultValues={"name": "(blank)"}
					)
				) for row in songsResult
			]
			if pathRuleTree:
				for song in songs:
					song.rules = list(pathRuleTree.values_flat(
							normalize_opening_slash(song.treepath))
						)
				return songs
			else:
				return songs


	def get_album(
			self,
			albumId: int | None,
		) -> Optional[SongsAlbumInfo]:
		with dtos.open_transaction(self.conn):
			albumInfo = next(self.get_albums(albumKeys=albumId), None)
			if not albumInfo:
				albumInfo = AlbumInfo(
					id="0",
					name="(Missing)",
					owner=dtos.User(
						id=0,
						username="",
						publictoken=""
					)
				)
			
			songs = self.get_album_songs(albumId, albumInfo)
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


	def add_album(
		self,
		album: AlbumCreationInfo
	) -> AlbumInfo:
		user = self.current_user_provider.current_user()
		savedName = SavedNameString(album.name)
		with self.conn.begin() as transaction:
			stmt = insert(tbl.albums).values(
				name = str(savedName),
				year = album.year,
				versionnote = str(SavedNameString(album.versionnote)),
				albumartistfk = album.albumartist.decoded_id() \
					if album.albumartist else None,
				lastmodifiedbyuserfk = user.id,
				lastmodifiedtimestamp = self.get_datetime().timestamp(),
				ownerfk = user.id,
			)
			try:
				res = self.conn.execute(stmt)
				affectedPk = res.lastrowid
				self.stations_albums_service.link_albums_with_stations_in_trx(
					(StationAlbumTuple(affectedPk, t.decoded_id() if t else None) 
						for t in (album.stations or [None]))
				)
				artist = next(self.artist_service.get_artists(
					userId=user.id,
					artistKeys=album.albumartist.id
				), None) if album.albumartist else None
				transaction.commit()
				owner = user.to_user()
				return AlbumInfo(
					id=dtos.encode_id(affectedPk), 
					name=str(savedName),
					owner=owner,
					year=album.year,
					albumartist=artist,
					versionnote=album.versionnote
				)
			except IntegrityError:
				raise AlreadyUsedError.build_error(
				f"{album.name} is already used for artist.",
				"body->name"
			)


	def update_album(
		self,
		album: AlbumCreationInfo,
		albumId: int
	) -> AlbumInfo | None:
		
		user = self.current_user_provider.current_user()
		savedName = SavedNameString(album.name)
		stmt = update(albums_tbl).values(
			name = str(savedName),
			year = album.year,
			versionnote = str(SavedNameString(album.versionnote)),
			albumartistfk = album.albumartist.decoded_id() \
				if album.albumartist else None,
			lastmodifiedbyuserfk = user.id,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		).where(ab_pk == albumId)
		with self.conn.begin() as transaction:
			owner = self.get_album_owner(albumId)
			try:
				self.conn.execute(stmt)
			except IntegrityError:
				raise AlreadyUsedError.build_error(
					f"{album.name} is already used for artist.",
					"body->name"
				)
			artist = next(self.artist_service.get_artists(
				userId=user.id,
				artistKeys=album.albumartist.id
			), None) if album.albumartist else None
			self.stations_albums_service.link_albums_with_stations_in_trx(
				(StationAlbumTuple(albumId, t.decoded_id() if t else None) 
					for t in (album.stations or [None]))
			)
			transaction.commit()
			return AlbumInfo(
				id=dtos.encode_id(albumId), #pyright: ignore reportUnknownMemberType,
				name=str(savedName),
				owner=owner,
				year=album.year,
				albumartist=artist,
				versionnote=album.versionnote
			)


	def save_album(
		self,
		album: AlbumCreationInfo,
		albumId: int | None=None
	) -> AlbumInfo | None:
		if not album and not albumId:
			raise ValueError("No album info to save")
		if albumId:
			return self.update_album(album, albumId)
		else:
			return self.add_album(album)


	def delete_album(self, albumkey: int) -> int:
		if not albumkey:
			return 0
		delStmt = delete(albums_tbl).where(ab_pk == albumkey)
		with self.conn.begin() as transaction:
			delCount = self.conn.execute(delStmt).rowcount
			transaction.commit()
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
		with self.conn.begin() as transaction:
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
			transaction.commit()
			insertedPk = res.lastrowid
			return insertedPk