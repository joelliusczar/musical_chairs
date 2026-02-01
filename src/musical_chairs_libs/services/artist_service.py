
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
	get_datetime,
	ArtistInfo,
	AlreadyUsedError,
	AccountInfo,
	OwnerInfo,
	SongsArtistInfo,
	SongListDisplayItem,
	DictDotMap,
	normalize_opening_slash,
	SearchNameString,
	SimpleQueryParameters
)
from .current_user_provider import CurrentUserProvider
from .path_rule_service import PathRuleService
from sqlalchemy import (
	select,
	insert,
	update,
	delete,
	literal,
	func
)
from sqlalchemy.sql.expression import (
	Update,
)
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from musical_chairs_libs.tables import (
	artists as artists_tbl,
	ab_pk,
	ar_name, ar_flatname, ar_pk, ar_ownerFk,
	users as user_tbl, u_pk, u_username, u_displayName,
	sg_pk, sg_name, sg_track, sg_albumFk, sg_path, sg_internalpath,
	sg_deletedTimstamp,
	song_artist as song_artist_tbl, sgar_songFk, sgar_artistFk, 
)



class ArtistService:

	def __init__(
		self,
		conn: Connection,
		currentUserProvider: CurrentUserProvider,
		pathRuleService: PathRuleService
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime
		self.path_rule_service = pathRuleService
		self.current_user_provider = currentUserProvider


	def get_artists_query(
		self,
		artistKeys: Union[int, Iterable[int], str, None]=None,
		userId: Optional[int]=None,
		exactStrMatch: bool=False
	):
		query = artists_tbl\
			.outerjoin(user_tbl, u_pk == ar_ownerFk)\
			.select()
		
		if type(artistKeys) == int:
			query = query.where(ar_pk == artistKeys)
		elif type(artistKeys) is str:
			if artistKeys:
				if exactStrMatch:
					searchStr = SearchNameString.format_name_for_search(artistKeys)
					query = query\
						.where(ar_flatname == searchStr)
				else:
					searchStr = SearchNameString.format_name_for_like(artistKeys)
					query = query\
						.where(ar_flatname.like(f"%{searchStr}%", escape="\\"))
		#check speficially if instance because [] is falsy
		elif isinstance(artistKeys, Iterable) :
			query = query.where(ar_pk.in_(artistKeys))

		if userId:
			query = query.where(ar_ownerFk == userId)
		
		return query


	def get_artists(self,
		page: int = 0,
		pageSize: Optional[int]=None,
		artistKeys: Union[int, Iterable[int], str, None]=None,
		userId: Optional[int]=None,
		exactStrMatch: bool=False
	) -> Iterator[ArtistInfo]:
		
		query = self.get_artists_query(artistKeys, userId, exactStrMatch)\
		.with_only_columns(
			ar_pk,
			ar_name,
			ar_ownerFk,
			u_username,
			u_displayName
		)

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
			flatname = str(SearchNameString(name)),
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		res = self.conn.execute(stmt)
		insertedPk = res.lastrowid
		self.conn.commit()
		return insertedPk

	def get_artist_owner(self, artistId: int) -> OwnerInfo:
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


	def get_artist_page(
		self,
		queryParams: SimpleQueryParameters,
		artist: str = "",
	) -> Tuple[list[ArtistInfo], int]:
		result = list(self.get_artists(
			queryParams.page, queryParams.limit, artist))
		countQuery = self.get_artists_query(artist)\
			.with_only_columns(func.count(1))
		count = self.conn.execute(countQuery).scalar() or 0
		return result, count


	def get_artist(
			self,
			artistId: int,
			user: Optional[AccountInfo]=None
		) -> Optional[SongsArtistInfo]:
		artistInfo = next(self.get_artists(artistKeys=artistId), None)
		if not artistInfo:
			return None
		songsQuery = select(
			sg_pk.label("id"),
			sg_name,
			sg_path,
			sg_internalpath,
			sg_track,
			literal("").label("album"),
			literal(0).label("queuedtimestamp"),
			literal(artistInfo.name).label("artist")
		)\
			.join(
				song_artist_tbl,
				sgar_songFk == sg_pk,
			)\
			.join(
				artists_tbl,
				ar_pk == sgar_artistFk,
			)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(sg_albumFk == artistId)
		songsResult = self.conn.execute(songsQuery).mappings()
		pathRuleTree = None
		if self.current_user_provider.is_loggedIn():
			pathRuleTree = self.path_rule_service.get_rule_path_tree()

		songs = [
			SongListDisplayItem(
				**DictDotMap.unflatten(dict(row), omitNulls=True)
			) for row in songsResult
		]
		if pathRuleTree:
			for song in songs:
				song.rules = list(pathRuleTree.values_flat(
						normalize_opening_slash(song.treepath))
					)

		return SongsArtistInfo(**artistInfo.model_dump(), songs=songs)


	def save_artist(
		self,
		artistName: str,
		artistId: Optional[int]=None
	) -> Optional[ArtistInfo]:
		if not artistName and not artistId:
			raise ValueError("No artist info to save")
		user = self.current_user_provider.current_user()
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
			owner = self.get_artist_owner(artistId)
		else:
			stmt = stmt.values(ownerfk = user.id)
		try:
			res = self.conn.execute(stmt)

			affectedPk: int = artistId if artistId else res.lastrowid
			self.conn.commit()
			if res.rowcount == 0:
				return None
			return ArtistInfo(id=affectedPk, name=str(savedName), owner=owner)
		except IntegrityError:
			raise AlreadyUsedError.build_error(
				f"{artistName} is already used.",
				"path->name"
			)


	def delete_artist(self, artistid: int) -> int:
		if not artistid:
			return 0
		delStmt = delete(artists_tbl).where(ar_pk == artistid)
		delCount = self.conn.execute(delStmt).rowcount
		self.conn.commit()
		return delCount