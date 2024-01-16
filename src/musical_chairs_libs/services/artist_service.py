
from typing import (
	Iterator,
	Optional,
	Union,
	cast,
	Iterable,
)
from musical_chairs_libs.dtos_and_utilities import (
	SavedNameString,
	get_datetime,
	ArtistInfo,
	build_error_obj,
	AlreadyUsedError,
	AccountInfo,
	OwnerInfo,
)
from sqlalchemy import (
	select,
	insert,
	update,
)
from sqlalchemy.sql.expression import (
	Update,
)
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from musical_chairs_libs.tables import (
	artists as artists_tbl,
	ab_pk,
	ar_name, ar_pk, ar_ownerFk,
	users as user_tbl, u_pk, u_username, u_displayName
)



class ArtistService:

	def __init__(
		self,
		conn: Connection
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime

	def get_artists(self,
		page: int = 0,
		pageSize: Optional[int]=None,
		artistKeys: Union[int, Iterable[int], str, None]=None,
		userId: Optional[int]=None,
		exactStrMatch: bool=False
	) -> Iterator[ArtistInfo]:
		query = select(
			ar_pk,
			ar_name,
			ar_ownerFk,
			u_username,
			u_displayName
		)\
		.join(user_tbl, u_pk == ar_ownerFk, isouter=True)
		if type(artistKeys) == int:
			query = query.where(ar_pk == artistKeys)
		elif type(artistKeys) is str:
			if exactStrMatch:
				query = query\
					.where(ar_name == artistKeys)
			else:
				query = query\
					.where(ar_name.like(f"%{artistKeys}%"))
		#check speficially if instance because [] is falsy
		elif isinstance(artistKeys, Iterable) :
			query = query.where(ar_pk.in_(artistKeys))
		if userId:
			query = query.where(ar_ownerFk == userId)
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query).mappings()

		yield from (ArtistInfo(
			id=row[ar_pk],
			name=row[ar_name],
			owner=OwnerInfo(
				id=row[ar_ownerFk],
				username=row[u_username],
				displayname=row[u_displayName]
			)
		)
			for row in records)

	def get_or_save_artist(self, name: Optional[str]) -> Optional[int]:
		if not name:
			return None
		savedName = SavedNameString.format_name_for_save(name)
		query = select(ar_pk).select_from(artists_tbl).where(ar_name == savedName)
		row = self.conn.execute(query).fetchone()
		if row:
			pk = cast(int, row[0])
			return pk
		print(name)
		stmt = insert(artists_tbl).values(
			name = savedName,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		res = self.conn.execute(stmt)
		insertedPk = res.lastrowid
		self.conn.commit()
		return insertedPk

	def __get_artist_owner__(self, artistId: int) -> OwnerInfo:
		query = select(ar_ownerFk, u_username, u_displayName)\
			.select_from(artists_tbl)\
			.join(user_tbl, u_pk == ar_ownerFk)\
			.where(ab_pk == artistId)
		data = self.conn.execute(query).mappings().fetchone()
		if not data:
			return OwnerInfo(id=0,username="", displayname="")
		return OwnerInfo(
			id=data[ar_ownerFk],
			username=data[u_username],
			displayname=data[u_displayName]
		)

	def save_artist(
		self,
		user: AccountInfo,
		artistName: str,
		artistId: Optional[int]=None
	) -> ArtistInfo:
		if not artistName and not artistId:
			raise ValueError("No artist info to save")
		upsert = update if artistId else insert
		savedName = SavedNameString(artistName)
		stmt = upsert(artists_tbl).values(
			name = str(savedName),
			lastmodifiedbyuserfk = user.id,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		owner = user
		if artistId and isinstance(stmt, Update):
			stmt = stmt.where(ar_pk == artistId)
			owner = self.__get_artist_owner__(artistId)
		else:
			stmt = stmt.values(ownerfk = user.id)
		try:
			res = self.conn.execute(stmt)

			affectedPk: int = artistId if artistId else res.lastrowid
			self.conn.commit()
			return ArtistInfo(id=affectedPk, name=str(savedName), owner=owner)
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{artistName} is already used.",
					"path->name"
				)]
			)