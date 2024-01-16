
from typing import (
	Iterator,
	Optional,
	Union,
	cast,
	Iterable,
)
from musical_chairs_libs.dtos_and_utilities import (
	SavedNameString,
	SearchNameString,
	get_datetime,
	AlbumInfo,
	ArtistInfo,
	build_error_obj,
	AlbumCreationInfo,
	AlreadyUsedError,
	AccountInfo,
	OwnerInfo,
)
from .artist_service import ArtistService
from sqlalchemy import (
	select,
	insert,
	update,
	Integer
)
from sqlalchemy.sql.expression import (
	Update,
)
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.schema import Column
from musical_chairs_libs.tables import (
	albums as albums_tbl,
	artists as artists_tbl,
	ab_name, ab_pk, ab_albumArtistFk, ab_year, ab_ownerFk,
	ar_name, ar_pk, ar_ownerFk,
	users as user_tbl, u_pk, u_username, u_displayName
)



class AlbumService:

	def __init__(
		self,
		conn: Connection,
		artistService: Optional[ArtistService]=None
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		if not artistService:
			artistService = ArtistService(conn)
		self.conn = conn
		self.get_datetime = get_datetime
		self.artist_service = artistService

	def get_albums(self,
		page: int = 0,
		pageSize: Optional[int]=None,
		albumKeys: Union[int, str, Iterable[int], None]=None,
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
		elif type(albumKeys) is str:
			searchStr = SearchNameString.format_name_for_search(albumKeys)
			if exactStrMatch:
				query = query\
					.where(ab_name == searchStr)
			else:
				query = query\
					.where(ab_name.like(f"%{searchStr}%"))
		elif isinstance(albumKeys, Iterable):
			query = query.where(ab_pk.in_(albumKeys))
		if userId:
			query = query.where(ab_ownerFk == userId)
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query).mappings()
		yield from (AlbumInfo(
			id=row["id"],
			name=row["name"],
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

	def __get_album_owner__(self, albumId: int) -> OwnerInfo:
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
			artist = next(self.artist_service.get_artists(
				userId=user.id,
				artistKeys=album.albumartist.id
			), None) if album.albumartist else None
			self.conn.commit()
			return AlbumInfo(
				id=affectedPk,
				name=str(savedName),
				owner=owner,
				year=album.year,
				albumartist=artist
			)
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