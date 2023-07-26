
from typing import (
	Iterator,
	Optional,
	Union,
	cast,
	Iterable,
	Any,
	Tuple,
	Callable,
	overload
)
from musical_chairs_libs.dtos_and_utilities import (
	SavedNameString,
	SongListDisplayItem,
	ScanningSongItem,
	SongTreeNode,
	StationInfo,
	SearchNameString,
	get_datetime,
	Sentinel,
	missing,
	AlbumInfo,
	ArtistInfo,
	SongAboutInfo,
	SongEditInfo,
	build_error_obj,
	AlbumCreationInfo,
	StationSongTuple,
	SongArtistTuple,
	AlreadyUsedError,
	ActionRule,
	PathsActionRule,
	UserRoleDef,
	RulePriorityLevel,
	normalize_opening_slash,
	AccountInfo,
	ChainedAbsorbentTrie,
	get_path_owner_roles,
	OwnerInfo,
	UserRoleDomain,
	build_rules_query,
	MinItemSecurityLevel,
	generate_user_and_rules_from_rows
)
from sqlalchemy import (
	select,
	insert,
	update,
	func,
	delete,
	union_all,
	or_,
	and_
)
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.expression import (
	Tuple as dbTuple,
	Select,
)
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import ColumnCollection as TblCols
from sqlalchemy.sql.schema import Column
from .env_manager import EnvManager
from sqlalchemy.engine.row import Row
from dataclasses import asdict, fields
from itertools import chain, groupby
from musical_chairs_libs.tables import (
	albums as albums_tbl,
	song_artist as song_artist_tbl,
	artists as artists_tbl,
	songs as songs_tbl,
	stations_songs as stations_songs_tbl, stsg_songFk, stsg_stationFk,
	stations as stations_tbl, st_name, st_pk, st_displayName, st_ownerFk,
	sg_pk, sg_name, sg_path,
	ab_name, ab_pk, ab_albumArtistFk, ab_year, ab_ownerFk,
	ar_name, ar_pk, ar_ownerFk,
	sg_albumFk, sg_bitrate,sg_comment, sg_disc, sg_duration, sg_explicit,
	sg_genre, sg_lyrics, sg_sampleRate, sg_track,
	sgar_isPrimaryArtist, sgar_songFk, sgar_artistFk,
	path_user_permissions as path_user_permissions_tbl,
	pup_userFk, pup_path, pup_role, pup_priority, pup_span, pup_count,
	users as user_tbl, u_pk, u_username, u_displayName, u_email, u_dirRoot,
	u_disabled
)


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

	def song_info(self, songPk: int) -> Optional[SongListDisplayItem]:
		query = select(
			sg_pk,
			sg_name,
			sg_path,
			ab_name.label("album"), #pyright: ignore reportUnknownMemberType
			ar_name.label("artist") #pyright: ignore reportUnknownMemberType
		)\
			.select_from(songs_tbl)\
			.join(albums_tbl, sg_albumFk == ab_pk, isouter=True)\
			.join(song_artist_tbl, sg_pk == sgar_songFk, isouter=True)\
			.join(artists_tbl, sgar_artistFk == ar_pk, isouter=True)\
			.where(sg_pk == songPk)\
			.limit(1)
		row = self.conn.execute(query).fetchone() #pyright: ignore reportUnknownMemberType
		if not row:
			return None
		return SongListDisplayItem(
			id=cast(int,row[sg_pk]),
			path=cast(str,row[sg_path]),
			name=cast(str,row[sg_name]),
			album=cast(str,row["album"]),
			artist=cast(str,row["artist"]),
			queuedTimestamp=0
		)

	def get_or_save_artist(self, name: Optional[str]) -> Optional[int]:
		if not name:
			return None
		savedName = SavedNameString.format_name_for_save(name)
		query = select(ar_pk).select_from(artists_tbl).where(ar_name == savedName)
		row = self.conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
		if row:
			pk = cast(int, row[ar_pk])
			return pk
		print(name)
		stmt = insert(artists_tbl).values(
			name = savedName,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		res = self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]
		insertedPk = cast(int, res.lastrowid) #pyright: ignore [reportUnknownMemberType]
		return insertedPk

	def __get_artist_owner__(self, artistId: int) -> OwnerInfo:
		query = select(ar_ownerFk, u_username, u_displayName)\
			.select_from(artists_tbl)\
			.join(user_tbl, u_pk == ar_ownerFk)\
			.where(ab_pk == artistId)
		data = self.conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
		if not data:
			return OwnerInfo(0,"", "")
		return OwnerInfo(
			cast(int, data[ar_ownerFk]),
			cast(str, data[u_username]),
			cast(str, data[u_displayName])
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
			lastModifiedByUserFk = user.id,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		owner = user
		if artistId:
			stmt = stmt.where(ar_pk == artistId)
			owner = self.__get_artist_owner__(artistId)
		else:
			stmt = stmt.values(ownerFk = user.id)
		try:
			res = self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]

			affectedPk: int = artistId if artistId else cast(int, res.lastrowid) #pyright: ignore [reportUnknownMemberType]
			return ArtistInfo(id=affectedPk, name=str(savedName), owner=owner)
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{artistName} is already used.",
					"path->name"
				)]
			)

	def __get_album_owner__(self, albumId: int) -> OwnerInfo:
		query = select(ab_ownerFk, u_username, u_displayName)\
			.select_from(albums_tbl)\
			.join(user_tbl, u_pk == ab_ownerFk)\
			.where(ab_pk == albumId)
		data = self.conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
		if not data:
			return OwnerInfo(0,"", "")
		return OwnerInfo(
			cast(int, data[ab_ownerFk]),
			cast(str, data[u_username]),
			cast(str, data[u_displayName])
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
			albumArtistFk = album.albumArtist.id if album.albumArtist else None,
			lastModifiedByUserFk = user.id,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		owner = user
		if albumId:
			stmt = stmt.where(ab_pk == albumId)
			owner = self.__get_album_owner__(albumId)
		else:
			stmt = stmt.values(ownerFk = user.id)
		try:
			res = self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]

			affectedPk: int = albumId if albumId else cast(int, res.lastrowid) #pyright: ignore [reportUnknownMemberType]
			artist = next(self.get_artists(
				user.id,
				artistKeys=album.albumArtist.id
			), None) if album.albumArtist else None
			return AlbumInfo(affectedPk, str(savedName), owner, album.year, artist)
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
		row = self.conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
		if row:
			pk = cast(int, row[ab_pk])
			return pk
		print(name)
		stmt = insert(albums_tbl).values(
			name = savedName,
			albumArtistFk = artistFk,
			year = year,
			lastModifiedTimestamp = self.get_datetime().timestamp(),
			ownerFk = 1,
			lastModifiedByUserFk = 1
		)
		res = self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]
		insertedPk = cast(int, res.lastrowid) #pyright: ignore [reportUnknownMemberType]
		return insertedPk

	def get_song_refs(
		self,
		songName: Union[Optional[str], Sentinel]=missing,
		page: int=0,
		pageSize: Optional[int]=None,
	) -> Iterator[ScanningSongItem]:
		query = select(
			sg_pk,
			sg_path,
			sg_name
		).select_from(songs_tbl)
		if type(songName) is str or songName is None:
			#allow null through
			savedName = SavedNameString.format_name_for_save(songName) if songName\
				else None
			query = query.where(sg_name == savedName)
		if pageSize:
			offset = page * pageSize
			query = query.limit(pageSize).offset(offset)
		records = self.conn.execute(query) #pyright: ignore reportUnknownMemberType
		for row in cast(Iterable[Row], records):
			yield ScanningSongItem(
					id=cast(int, row[sg_pk]),
					path=cast(str,row[sg_path]),
					name=SavedNameString.format_name_for_save(cast(str,row[sg_name]))
				)

	def update_song_info(self, songInfo: ScanningSongItem) -> int:
		savedName =  SavedNameString.format_name_for_save(songInfo.name)
		timestamp = self.get_datetime().timestamp()
		songUpdate = update(songs_tbl) \
				.where(sg_pk == songInfo.id) \
				.values(
					name = savedName,
					albumFk = songInfo.albumId,
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
		count = cast(int, self.conn.execute(songUpdate).rowcount) #pyright: ignore [reportUnknownMemberType]
		try:
			songComposerInsert = insert(song_artist_tbl)\
				.values(songFk = songInfo.id, artistFk = songInfo.artistId)
			self.conn.execute(songComposerInsert) #pyright: ignore [reportUnknownMemberType]
		except IntegrityError: pass
		try:
			songComposerInsert = insert(song_artist_tbl)\
				.values(
					songFk = songInfo.id,
					artistFk = songInfo.composerId,
					comment = "composer"
				)
			self.conn.execute(songComposerInsert) #pyright: ignore [reportUnknownMemberType]
		except IntegrityError: pass
		return count

	def get_paths_user_can_see(self, userId: int) -> Iterator[PathsActionRule]:
		query = select(pup_path, pup_role, pup_priority, pup_span, pup_count)\
			.where(pup_userFk == userId)\
			.order_by(pup_path)
		records = cast(Iterable[Row], self.conn.execute(query)) #pyright: ignore [reportUnknownMemberType]
		for r in records:
			yield PathsActionRule(
				cast(str,r[pup_role]),
				priority=cast(int,r[pup_priority]) \
					or RulePriorityLevel.STATION_PATH.value,
				span=cast(int,r[pup_span]) or 0,
				count=cast(int,r[pup_count]) or 0,
				path=normalize_opening_slash(cast(str,r[pup_path]))
			)

	def get_rule_path_tree(
		self,
		user: AccountInfo
	) -> ChainedAbsorbentTrie[ActionRule]:
		rules = ActionRule.aggregate(
			user.roles,
			(p for p in self.get_paths_user_can_see(user.id)),
			(p for p in get_path_owner_roles(user.dirRoot))
		)

		pathRuleTree = ChainedAbsorbentTrie[ActionRule](
			(p.path, p) for p in rules if isinstance(p, PathsActionRule) and p.path
		)
		pathRuleTree.add("", (r for r in user.roles \
			if type(r) == ActionRule \
				and (UserRoleDomain.Path.conforms(r.name) \
						or r.name == UserRoleDef.ADMIN.value
				)
		), shouldEmptyUpdateTree=False)
		return pathRuleTree

	def __song_ls_query__(self, prefix: Optional[str]="") -> Select:
		prefix = normalize_opening_slash(prefix, False)
		query = select(
				func.next_directory_level(sg_path, prefix).label("prefix"),
				func.min(sg_name).label("name"),
				func.count(sg_pk).label("totalChildCount"),
				func.max(sg_pk).label("pk"),
				func.max(sg_path).label("control_path")
		).where(sg_path.like(f"{prefix}%"))\
			.group_by(func.next_directory_level(sg_path, prefix))
		return query

	def __query_to_treeNodes__(
		self,
		query: Select,
		permittedPathsTree: ChainedAbsorbentTrie[ActionRule]
	) -> Iterator[SongTreeNode]:
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		for row in cast(Iterable[Row] ,records):
			normalizedPrefix = normalize_opening_slash(cast(str,row["prefix"]))
			if not permittedPathsTree.matches(normalizedPrefix)\
			:
				continue
			if row["control_path"] == row["prefix"]:
				yield SongTreeNode(
					path=cast(str, row["prefix"]),
					totalChildCount=cast(int, row["totalChildCount"]),
					id=cast(int, row["pk"]),
					name=cast(str, row["name"]),
					rules=[r for p in
						permittedPathsTree.values(normalizedPrefix) for r in p
					]
				)
			else:
				yield SongTreeNode(
					path=cast(str, row["prefix"]),
					totalChildCount=cast(int, row["totalChildCount"]),
					rules=[r for p in
						permittedPathsTree.values(normalizedPrefix) for r in p
					]
				)

	def song_ls(
		self,
		user: AccountInfo,
		prefix: Optional[str]=None
	) -> Iterator[SongTreeNode]:
		permittedPathTree = user.get_permitted_paths_tree()
		if type(prefix) == str:
			query = self.__song_ls_query__(prefix)
			yield from self.__query_to_treeNodes__(query, permittedPathTree)
		else:
			prefixes = {
				next((s for s in p.split("/") if s), "") if p else p for p in \
				permittedPathTree.shortest_paths()
			}
			queryList: list[Select] = []
			for p in prefixes:
				queryList.append(self.__song_ls_query__(p))
			if queryList:
				yield from self.__query_to_treeNodes__(
					union_all(*queryList),
					permittedPathTree
				)

	def get_songIds(
		self,
		page: int = 0,
		pageSize: Optional[int]=None,
		stationKey: Union[int, str, None]=None,
		songIds: Optional[Iterable[int]]=None
	) -> Iterator[int]:
		offset = page * pageSize if pageSize else 0
		query = select(sg_pk).select_from(songs_tbl)
		#add joins
		if stationKey:
			query = query.join(stations_songs_tbl, stsg_songFk == sg_pk)
			if type(stationKey) == int:
				query = query.where(stsg_stationFk == stationKey)
			elif type(stationKey) is str:
				query = query.join(stations_tbl, stsg_stationFk == st_pk)
				searchStr = SearchNameString.format_name_for_search(stationKey)
				query = query.join(stations_tbl, st_pk == stsg_stationFk).where(
					func.format_name_for_search(st_name).like(f"%{searchStr}%")
				)
		if songIds:
			query = query.where(sg_pk.in_(songIds))
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (cast(int, row["pk"]) for row in cast(Iterable[Row],records))

	@overload
	def get_song_path(
		self,
		itemIds: int,
		useFullSystemPath: bool=True
	) -> Iterator[str]: ...

	@overload
	def get_song_path(
		self,
		itemIds: Iterable[int],
		useFullSystemPath: bool=True
	) -> Iterator[str]: ...

	def get_song_path(
		self,
		itemIds: Union[Iterable[int], int],
		useFullSystemPath: bool=True
	) -> Iterator[str]:
		query = select(sg_path)
		if isinstance(itemIds, Iterable):
			query = query.where(sg_pk.in_(itemIds))
		else:
			query = query.where(sg_pk == itemIds)
		results = cast(Iterable[Row], self.conn.execute(query)) #pyright: ignore reportUnknownMemberType
		if useFullSystemPath:
			yield from (f"{EnvManager.search_base}/{row[sg_path]}" \
				for row in results
			)
		else:
			yield from (cast(str,row[sg_path]) for row in results)

	def get_station_songs(
		self,
		songIds: Union[int, Iterable[int], None]=None,
		stationIds: Union[int, Iterable[int], None]=None,
	) -> Iterable[StationSongTuple]:
		query = select(
			stsg_stationFk,
			stsg_songFk
		)

		if type(songIds) == int:
			query = query.where(stsg_songFk == songIds)
		elif isinstance(songIds, Iterable):
			query = query.where(stsg_songFk.in_(songIds))
		if type(stationIds) == int:
			query = query.where(stsg_stationFk == stationIds)
		elif isinstance(stationIds, Iterable):
			query = query.where(stsg_stationFk.in_(stationIds))
		query = query.order_by(stsg_songFk)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (StationSongTuple(
				cast(int, row[stsg_songFk]),
				cast(int, row[stsg_stationFk]),
				True
			)
			for row in cast(Iterable[Row],records))

	def remove_songs_for_stations(
		self,
		stationSongs: Iterable[Union[StationSongTuple, Tuple[int, int]]],
	) -> int:
		stationSongs = stationSongs or []
		delStmt = delete(stations_songs_tbl)\
			.where(dbTuple(stsg_songFk, stsg_stationFk).in_(stationSongs))
		return cast(int, self.conn.execute(delStmt).rowcount) #pyright: ignore [reportUnknownMemberType]

	def validate_stations_songs(
		self,
		stationSongs: Iterable[StationSongTuple]
	) -> Iterable[StationSongTuple]:
		if not stationSongs:
			return iter([])
		query = select(
			sg_pk,
			st_pk
		).where(dbTuple(sg_pk, st_pk).in_(stationSongs))

		records = self.conn.execute(query) #pyright: ignore reportUnknownMemberType
		yield from (StationSongTuple(
			cast(int, row[sg_pk]),
			cast(int, row[st_pk])
		) for row in cast(Iterable[Row],records))

	def link_songs_with_stations(
		self,
		stationSongs: Iterable[StationSongTuple],
		userId: Optional[int]=None
	) -> Iterable[StationSongTuple]:
		if not stationSongs:
			return []
		uniquePairs = set(self.validate_stations_songs(stationSongs))
		if not uniquePairs:
			return []
		existingPairs = set(self.get_station_songs(
			songIds={st.songId for st in uniquePairs}
		))
		outPairs = existingPairs - uniquePairs
		inPairs = uniquePairs - existingPairs
		self.remove_songs_for_stations(outPairs)
		if not inPairs: #if no songs - stations have been linked
			return existingPairs - outPairs
		params = [{
			"songFk": p.songId,
			"stationFk": p.stationId,
			"lastModifiedByUserFk": userId,
			"lastModifiedTimestamp": self.get_datetime().timestamp()
		} for p in inPairs]
		stmt = insert(stations_songs_tbl)
		self.conn.execute(stmt, params) #pyright: ignore [reportUnknownMemberType]
		return self.get_station_songs(
			songIds={st.songId for st in uniquePairs}
		)

	def get_albums(self,
		page: int = 0,
		pageSize: Optional[int]=None,
		albumKeys: Union[int, str, Iterable[int], None]=None,
		userId: Optional[int]=None
	) -> Iterator[AlbumInfo]:
		album_owner = cast(TblCols, user_tbl.alias("albumOwner")) #pyright: ignore [reportUnknownMemberType]
		albumOwnerId = cast(Column, album_owner.c.pk) #pyright: ignore [reportUnknownMemberType]
		artist_owner = cast(TblCols,user_tbl.alias("artistOwner")) #pyright: ignore [reportUnknownMemberType]
		artistOwnerId = cast(Column, artist_owner.c.pk) #pyright: ignore [reportUnknownMemberType]
		query = select(
			ab_pk.label("id"), #pyright: ignore [reportUnknownMemberType]
			ab_name.label("name"), #pyright: ignore [reportUnknownMemberType]
			ab_year.label("year"), #pyright: ignore [reportUnknownMemberType]
			ab_albumArtistFk.label("albumArtistId"), #pyright: ignore [reportUnknownMemberType]
			ab_ownerFk.label("album.ownerId"), #pyright: ignore [reportUnknownMemberType]
			album_owner.c.username.label("album.ownerName"), #pyright: ignore [reportUnknownMemberType]
			album_owner.c.displayName.label("album.ownerDisplayName"), #pyright: ignore [reportUnknownMemberType]
			ar_name.label("artist.name"), #pyright: ignore [reportUnknownMemberType]
			ar_ownerFk.label("artist.ownerId"), #pyright: ignore [reportUnknownMemberType]
			artist_owner.c.username.label("artist.ownerName"), #pyright: ignore [reportUnknownMemberType]
			artist_owner.c.displayName.label("artist.ownerDisplayName") #pyright: ignore [reportUnknownMemberType]
		).select_from(albums_tbl)\
			.join(artists_tbl, ar_pk == ab_albumArtistFk, isouter=True) \
			.join(album_owner, albumOwnerId == ab_ownerFk, isouter=True) \
			.join(artist_owner, artistOwnerId == ar_ownerFk, isouter=True)
		if type(albumKeys) == int:
			query = query.where(ab_pk == albumKeys)
		elif isinstance(albumKeys, Iterable):
			query = query.where(ab_pk.in_(albumKeys))
		elif type(albumKeys) is str:
			searchStr = SearchNameString.format_name_for_search(albumKeys)
			query = query\
				.where(func.format_name_for_search(ab_name).like(f"%{searchStr}%"))
		if userId:
			query = query.where(ab_ownerFk == userId)
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (AlbumInfo(
			cast(int,row["id"]),
			cast(str,row["name"]),
			OwnerInfo(
				cast(int,row["album.ownerId"]),
				cast(str, row["album.ownerName"]),
				cast(str, row["album.ownerDisplayName"])
			),
			cast(int,row["year"]),
			ArtistInfo(
				cast(int,row["albumArtistId"]),
				cast(str,row["artist.name"]),
				OwnerInfo(
					cast(int,row["artist.ownerId"]),
					cast(str, row["artist.ownerName"]),
					cast(str, row["artist.ownerDisplayName"])
				)
			) if row["albumArtistId"] else None
			) for row in cast(Iterable[Row], records))

	def get_artists(self,
		page: int = 0,
		pageSize: Optional[int]=None,
		artistKeys: Union[int, Iterable[int], str, None]=None,
		userId: Optional[int]=None
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
		#check speficially if instance because [] is falsy
		elif isinstance(artistKeys, Iterable) :
			query = query.where(ar_pk.in_(artistKeys))
		elif type(artistKeys) is str:
			searchStr = SearchNameString.format_name_for_search(artistKeys)
			query = query\
				.where(func.format_name_for_search(ar_name).like(f"%{searchStr}%"))
		if userId:
			query = query.where(ar_ownerFk == userId)
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]

		yield from (ArtistInfo(
			cast(int, row[ar_pk]),
			cast(str, row[ar_name]),
			OwnerInfo(
				cast(int, row[ar_ownerFk]),
				cast(str, row[u_username]),
				cast(str, row[u_displayName])
			)
		)
			for row in cast(Iterable[Row],records))

	def get_song_artists(
		self,
		songIds: Union[int, Iterable[int],None]=None,
		artistIds: Union[int, Iterable[int],None]=None,
	) -> Iterable[SongArtistTuple]:
		query = select(
			sgar_artistFk,
			sgar_songFk,
			sgar_isPrimaryArtist
		)

		if type(songIds) == int:
			query = query.where(sgar_songFk == songIds)
		elif isinstance(songIds, Iterable):
			query = query.where(sgar_songFk.in_(songIds))
		if type(artistIds) == int:
			query = query.where(sgar_artistFk == artistIds)
		elif isinstance(artistIds, Iterable):
			query = query.where(sgar_artistFk.in_(artistIds))
		query = query.order_by(sgar_songFk)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		yield from (SongArtistTuple(
				cast(int, row[sgar_songFk]),
				cast(int, row[sgar_artistFk]),
				cast(bool, row[sgar_isPrimaryArtist])
			)
			for row in cast(Iterable[Row],records))

	def remove_songs_for_artists(
		self,
		songArtists: Iterable[Union[SongArtistTuple, Tuple[int, int]]],
	) -> int:
		songArtists = songArtists or []
		delStmt = delete(song_artist_tbl)\
			.where(dbTuple(sgar_songFk, sgar_artistFk).in_(songArtists))
		count = cast(int, self.conn.execute(delStmt).rowcount) #pyright: ignore [reportUnknownMemberType]
		return count

	def validate_song_artists(
		self,
		songArtists: Iterable[SongArtistTuple]
	) -> Iterable[SongArtistTuple]:
		if not songArtists:
			return iter([])
		songArtistsSet = set(songArtists)
		primaryArtistId = next(
			(sa.artistId for sa in songArtistsSet if sa.isPrimaryArtist),
			-1
		)
		query = select(
			sg_pk,
			ar_pk
		).where(dbTuple(sg_pk, ar_pk).in_(songArtistsSet))

		records = self.conn.execute(query) #pyright: ignore reportUnknownMemberType
		yield from (SongArtistTuple(
			cast(int, row[sg_pk]),
			cast(int, row[ar_pk]),
			isPrimaryArtist=cast(int, row[ar_pk]) == primaryArtistId
		) for row in cast(Iterable[Row],records))

	def __are_all_primary_artist_single(
		self,
		songArtists: Iterable[SongArtistTuple]
	) -> bool:
		songKey: Callable[[SongArtistTuple],int] = lambda a: a.songId
		artistsGroups = groupby(sorted(songArtists, key=songKey), key=songKey)
		for _, g in artistsGroups:
			if len([sa for sa in g if sa.isPrimaryArtist]) > 1:
				return False
		return True

	def link_songs_with_artists(
		self,
		songArtists: Iterable[SongArtistTuple],
		userId: Optional[int]=None
	) -> Iterable[SongArtistTuple]:
		if not songArtists:
			return []
		uniquePairs = set(self.validate_song_artists(songArtists))

		if not self.__are_all_primary_artist_single(uniquePairs):
			raise ValueError("Only one artist can be the primary artist")
		existingPairs = set(self.get_song_artists(
			songIds={sa.songId for sa in uniquePairs}
		))
		outPairs = existingPairs - uniquePairs
		inPairs = uniquePairs - existingPairs
		self.remove_songs_for_artists(outPairs)
		if not inPairs: #if no songs - artist have been linked
			return existingPairs - outPairs
		params = [{
			"songFk": p.songId,
			"artistFk": p.artistId,
			"isPrimaryArtist": p.isPrimaryArtist,
			"lastModifiedByUserFk": userId,
			"lastModifiedTimestamp": self.get_datetime().timestamp()
		} for p in inPairs]
		stmt = insert(song_artist_tbl)
		self.conn.execute(stmt, params) #pyright: ignore [reportUnknownMemberType]
		return self.get_song_artists(
			songIds={sa.songId for sa in uniquePairs}
		)

	def _prepare_song_row_for_model(self, row: Row) -> dict[str, Any]:
		songDict: dict[Any, Any] = {**row}
		albumArtistId = songDict.pop("album.albumArtistId", None)
		albumArtistName = songDict.pop("album.albumArtist.name", "")
		albumArtistOwner = OwnerInfo(
			songDict.pop("album.albumArtist.ownerId", 0),
			songDict.pop("album.albumArtist.ownerName", ""),
			songDict.pop("album.albumArtist.ownerDisplayName", ""),
		)
		album = AlbumInfo(
			songDict.pop("album.id", None),
			songDict.pop("album.name", None),
			OwnerInfo(
				songDict.pop("album.ownerId", 0),
				songDict.pop("album.ownerName", ""),
				songDict.pop("album.ownerDisplayName", ""),
			),
			songDict.pop("album.year", None),
			ArtistInfo(
				albumArtistId,
				albumArtistName,
				albumArtistOwner,
			) if albumArtistId else None
		)
		if album.id:
			songDict["album"] = album
		songDict.pop("artist.id", None)
		songDict.pop("artist.name", None)
		songDict.pop("artist.ownerId", None)
		songDict.pop("artist.ownerName", None)
		songDict.pop("artist.ownerDisplayName", None)
		songDict.pop("station.id", None)
		songDict.pop("station.name", None)
		songDict.pop("station.displayName", None)
		songDict.pop("station.ownerId", None)
		songDict.pop("station.ownerName", None)
		songDict.pop("station.ownerDisplayName", None)
		songDict.pop(sgar_isPrimaryArtist.description, None) #pyright: ignore reportUnknownMemberType
		return songDict

	def __get_query_for_songs_for_edit__(
		self,
		songIds: Iterable[int]
	) -> Select:
		album_artist = cast(TblCols,artists_tbl.alias("albumArtist")) #pyright: ignore [reportUnknownMemberType]
		albumArtistId = cast(Column, album_artist.c.pk) #pyright: ignore [reportUnknownMemberType]
		albumArtistOwnerId = cast(Column, album_artist.c.ownerFk) #pyright: ignore [reportUnknownMemberType]
		albumOwner = cast(TblCols, user_tbl.alias("albumOwner")) #pyright: ignore [reportUnknownMemberType]
		albumOwnerId = cast(Column, albumOwner.c.pk) #pyright: ignore [reportUnknownMemberType]
		albumArtistOwner = cast(TblCols,user_tbl.alias("albumArtistOwner")) #pyright: ignore [reportUnknownMemberType]
		albumArtistOwnerUserId = cast(Column, albumArtistOwner.c.pk) #pyright: ignore [reportUnknownMemberType]
		artistOwner = cast(TblCols, user_tbl.alias("artistOwner")) #pyright: ignore [reportUnknownMemberType]
		artistOwnerId = cast(Column, artistOwner.c.pk) #pyright: ignore [reportUnknownMemberType]
		stationOwner = cast(TblCols, user_tbl.alias("stationOwner")) #pyright: ignore [reportUnknownMemberType]
		stationOwnerId = cast(Column, stationOwner.c.pk) #pyright: ignore [reportUnknownMemberType]
		query = select(
			sg_pk.label("id"), #pyright: ignore [reportUnknownMemberType]
			sg_name.label("name"), #pyright: ignore [reportUnknownMemberType]
			sg_path.label("path"), #pyright: ignore [reportUnknownMemberType]
			sg_track.label("track"), #pyright: ignore [reportUnknownMemberType]
			sg_disc.label("disc"), #pyright: ignore [reportUnknownMemberType]
			sg_genre.label("genre"), #pyright: ignore [reportUnknownMemberType]
			sg_explicit.label("explicit"), #pyright: ignore [reportUnknownMemberType]
			sg_bitrate.label("bitrate"), #pyright: ignore [reportUnknownMemberType]
			sg_comment.label("comment"), #pyright: ignore [reportUnknownMemberType]
			sg_lyrics.label("lyrics"), #pyright: ignore [reportUnknownMemberType]
			sg_duration.label("duration"), #pyright: ignore [reportUnknownMemberType]
			sg_sampleRate.label("sampleRate"), #pyright: ignore [reportUnknownMemberType]
			ab_pk.label("album.id"), #pyright: ignore [reportUnknownMemberType]
			ab_name.label("album.name"), #pyright: ignore [reportUnknownMemberType]
			ab_ownerFk.label("album.ownerId"), #pyright: ignore [reportUnknownMemberType]
			albumOwner.c.username.label("album.ownerName"), #pyright: ignore [reportUnknownMemberType]
			albumOwner.c.displayName.label("album.ownerDisplayName"), #pyright: ignore [reportUnknownMemberType]
			ab_year.label("album.year"), #pyright: ignore [reportUnknownMemberType]
			ab_albumArtistFk.label("album.albumArtistId"), #pyright: ignore [reportUnknownMemberType]
			album_artist.c.name.label("album.albumArtist.name"), #pyright: ignore [reportUnknownMemberType]
			album_artist.c.ownerFk.label("album.albumArtist.ownerId"), #pyright: ignore [reportUnknownMemberType]
			albumArtistOwner.c.username.label("album.albumArtist.ownerName"), #pyright: ignore [reportUnknownMemberType]
			albumArtistOwner.c.displayName.label("album.albumArtist.ownerDisplayName"), #pyright: ignore [reportUnknownMemberType]
			sgar_isPrimaryArtist,
			ar_pk.label("artist.id"), #pyright: ignore [reportUnknownMemberType]
			ar_name.label("artist.name"), #pyright: ignore [reportUnknownMemberType]
			ar_ownerFk.label("artist.ownerId"), #pyright: ignore [reportUnknownMemberType]
			artistOwner.c.username.label("artist.ownerName"), #pyright: ignore [reportUnknownMemberType]
			artistOwner.c.displayName.label("artist.ownerDisplayName"), #pyright: ignore [reportUnknownMemberType]
			st_pk.label("station.id"), #pyright: ignore [reportUnknownMemberType]
			st_name.label("station.name"), #pyright: ignore [reportUnknownMemberType]
			st_ownerFk.label("station.ownerId"), #pyright: ignore [reportUnknownMemberType]
			stationOwner.c.username.label("station.ownerName"), #pyright: ignore [reportUnknownMemberType]
			stationOwner.c.displayName.label("station.ownerDisplayName"), #pyright: ignore [reportUnknownMemberType]
			st_displayName.label("station.displayName") #pyright: ignore [reportUnknownMemberType]
		).select_from(songs_tbl)\
				.join(song_artist_tbl, sg_pk == sgar_songFk, isouter=True)\
				.join(artists_tbl, ar_pk == sgar_artistFk, isouter=True)\
				.join(albums_tbl, sg_albumFk == ab_pk, isouter=True)\
				.join(stations_songs_tbl, sg_pk == stsg_songFk, isouter=True)\
				.join(stations_tbl, stsg_stationFk ==  st_pk, isouter=True)\
				.join(albumOwner, albumOwnerId == ab_ownerFk, isouter=True) \
				.join(artistOwner, artistOwnerId ==  ar_ownerFk, isouter=True)\
				.join(stationOwner, stationOwnerId == st_ownerFk, isouter=True)\
				.join(
					album_artist,
					ab_albumArtistFk == albumArtistId,
					isouter=True
				)\
				.join(albumArtistOwner,
					albumArtistOwnerUserId == albumArtistOwnerId,
					isouter=True
				) \
				.where(sg_pk.in_(songIds))\
				.order_by(sg_pk)
		return query

	def get_songs_for_edit(
		self,
		songIds: Iterable[int],
		user: AccountInfo,
	) -> Iterator[SongEditInfo]:
		rulePathTree = self.get_rule_path_tree(user)
		query = self.__get_query_for_songs_for_edit__(songIds)
		records = self.conn.execute(query).fetchall() #pyright: ignore [reportUnknownMemberType]
		currentSongRow = None
		artists: set[ArtistInfo] = set()
		stations: set[StationInfo] = set()
		primaryArtist: Optional[ArtistInfo] = None
		for row in records:
			if not currentSongRow:
				currentSongRow = row
			elif row["id"] != currentSongRow["id"]:
				songDict = self._prepare_song_row_for_model(currentSongRow)
				rules = [*rulePathTree.valuesFlat(songDict["path"])]
				yield SongEditInfo(**songDict,
					primaryArtist=primaryArtist,
					artists=list(artists),
					stations=list(stations),
					rules=rules
				)
				currentSongRow = row
				artists =  set()
				stations = set()
				primaryArtist = None
			if row[sgar_isPrimaryArtist]:
				primaryArtist = ArtistInfo(
					cast(int, row["artist.id"]),
					cast(str, row["artist.name"]),
					OwnerInfo(
						cast(int, row["artist.ownerId"]),
						cast(str, row["artist.ownerName"]),
						cast(str, row["artist.ownerDisplayName"])
					)
				)
			elif row["artist.id"]:
				artists.add(ArtistInfo(
						cast(int, row["artist.id"]),
						cast(str, row["artist.name"]),
						OwnerInfo(
							cast(int, row["artist.ownerId"]),
							cast(str, row["artist.ownerName"]),
							cast(str, row["artist.ownerDisplayName"])
						)
					)
				)
			if row["station.id"]:
				stations.add(StationInfo(
					cast(int, row["station.id"]),
					cast(str, row["station.name"]),
					cast(str, row["station.displayName"]),
					owner=OwnerInfo(
						cast(int, row["station.ownerId"]),
						cast(str, row["station.ownerName"]),
						cast(str, row["station.ownerDisplayName"])
					)
				))
		if currentSongRow:
			songDict = self._prepare_song_row_for_model(currentSongRow)
			rules = [*rulePathTree.valuesFlat(songDict["path"])]
			yield SongEditInfo(**songDict,
					primaryArtist=primaryArtist,
					artists=sorted(artists, key=lambda a: a.id if a else 0),
					stations=sorted(stations, key=lambda t: t.id if t else 0),
					rules=rules
				)

	def save_songs(
		self,
		ids: Iterable[int],
		songInfo: SongAboutInfo,
		user: AccountInfo
	) -> Iterator[SongEditInfo]:
		if not ids:
			return iter([])
		if not songInfo:
			return self.get_songs_for_edit(ids, user)
		if not songInfo.touched:
			songInfo.touched = {f.name for f in fields(SongAboutInfo)}
		ids = list(ids)
		songInfo.name = str(SavedNameString(songInfo.name))
		songInfoDict = asdict(songInfo)
		songInfoDict.pop("artists", None)
		songInfoDict.pop("primaryArtist", None)
		songInfoDict.pop("tags", None)
		songInfoDict.pop("id", None)
		songInfoDict.pop("album", None)
		songInfoDict.pop("stations", None)
		songInfoDict.pop("covers", None)
		songInfoDict.pop("touched", None)
		songInfoDict["albumFk"] = songInfo.album.id if songInfo.album else None
		songInfoDict["lastModifiedByUserFk"] = user.id
		songInfoDict["lastModifiedTimestamp"] = self.get_datetime().timestamp()
		if "album" in songInfo.touched:
			songInfo.touched.add("albumFk")
		stmt = update(songs_tbl).values(
			**{k:v for k,v in songInfoDict.items() if k in songInfo.touched}
		).where(sg_pk.in_(ids))
		self.conn.execute(stmt) #pyright: ignore reportUnknownMemberType
		if "artists" in songInfo.touched or "primaryArtist" in songInfo.touched:
			self.link_songs_with_artists(
				chain(
					(SongArtistTuple(sid, a.id) for a in songInfo.artists or []
						for sid in ids
					) if "artists" in songInfo.touched else (),
					#we can't use allArtists here bc we need the primaryArtist selection
					(SongArtistTuple(sid, songInfo.primaryArtist.id, True) for sid in ids)
						if "primaryArtist" in
						songInfo.touched and songInfo.primaryArtist else ()
				),
				user.id
			)
		if "stations" in songInfo.touched:
			self.link_songs_with_stations(
				(StationSongTuple(sid, t.id)
					for t in (songInfo.stations or []) for sid in ids),
				user.id
			)

		if len(ids) < 2:
			yield from self.get_songs_for_edit(ids, user)
		else:
			fetched = self.get_songs_for_multi_edit(ids, user)
			if fetched:
				yield fetched

	def get_songs_for_multi_edit(
		self,
		songIds: Iterable[int],
		user: AccountInfo
	) -> Optional[SongEditInfo]:
		if not songIds:
			return None
		commonSongInfo = None
		touched = {f.name for f in fields(SongAboutInfo) }
		removedFields: set[str] = set()
		rules = None
		for songInfo in self.get_songs_for_edit(songIds, user):
			if rules is None: #empty set means no permissions. Don't overwrite
				rules = set(songInfo.rules)
			else:
				# only keep the set of rules that are common to
				# each song
				rules = rules & set(songInfo.rules)
			songInfoDict = asdict(songInfo)
			if not commonSongInfo:
				commonSongInfo = songInfoDict
				continue
			for field in touched:
				isUniqueField = field in { "touched" }
				if isUniqueField or songInfoDict[field] != commonSongInfo[field]:
					removedFields.add(field)
					commonSongInfo.pop(field, None)
			touched -= removedFields
			removedFields.clear()
		if commonSongInfo:
			commonSongInfo["id"] = 0
			commonSongInfo["path"] = ""
			del commonSongInfo["rules"]
			return SongEditInfo(
				**commonSongInfo,
				touched=touched,
				rules=list(rules or [])
			)
		else:
			return SongEditInfo(id=0, path="", touched=touched)

	def get_path_users(
		self,
		prefix: str,
		userId: Optional[int]=None,
		owner: Optional[AccountInfo]=None
	) -> Iterator[AccountInfo]:
		addSlash = True
		normalizedPrefix = normalize_opening_slash(prefix)
		rulesQuery = build_rules_query(UserRoleDomain.Path).cte() #pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
		query = select(
			u_pk,
			u_username,
			u_displayName,
			u_email,
			u_dirRoot,
			rulesQuery.c.rule_userFk, #pyright: ignore [reportUnknownMemberType]
			rulesQuery.c.rule_name, #pyright: ignore [reportUnknownMemberType]
			rulesQuery.c.rule_count, #pyright: ignore [reportUnknownMemberType]
			rulesQuery.c.rule_span, #pyright: ignore [reportUnknownMemberType]
			rulesQuery.c.rule_priority, #pyright: ignore [reportUnknownMemberType]
			rulesQuery.c.rule_domain #pyright: ignore [reportUnknownMemberType]
		).select_from(user_tbl).join(
			rulesQuery,
			or_(
				and_(
					func.substring(
						normalizedPrefix,
						0,
						func.length(
							func.normalize_opening_slash(u_dirRoot, addSlash)
						) + 1
					) == func.normalize_opening_slash(u_dirRoot, addSlash),
					rulesQuery.c.rule_userFk == 0 #pyright: ignore [reportUnknownMemberType]
				),
				and_(
					rulesQuery.c.rule_userFk == u_pk,  #pyright: ignore [reportUnknownMemberType]
						func.substring(
							normalizedPrefix,
							0,
							func.length(
								func.normalize_opening_slash(rulesQuery.c.rule_path, addSlash) #pyright: ignore [reportUnknownMemberType]
							) + 1
						) == func.normalize_opening_slash(rulesQuery.c.rule_path, addSlash) #pyright: ignore [reportUnknownMemberType]
				),
			),
			isouter=True
		).where(or_(u_disabled.is_(None), u_disabled == False))\
		.where(
			or_(
				coalesce(
					rulesQuery.c.rule_priority, #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
					RulePriorityLevel.SITE.value
				) > MinItemSecurityLevel.INVITED_USER.value,
					func.substring(
						prefix,
						0,
						func.length(
							func.normalize_opening_slash(u_dirRoot, addSlash)
						) + 1
					) == func.normalize_opening_slash(u_dirRoot, addSlash)
			)
		)
		if userId is not None:
			query = query.where(u_pk == userId)
		query = query.order_by(u_username)
		records = self.conn.execute(query).fetchall() #pyright: ignore [reportUnknownMemberType]
		yield from generate_user_and_rules_from_rows(
			records,
			UserRoleDomain.Path,
			owner.id if owner else None,
			prefix
		)

	def add_user_rule_to_path(
		self,
		addedUserId: int,
		prefix: str,
		rule: ActionRule
	) -> PathsActionRule:
		stmt = insert(path_user_permissions_tbl).values(
			userFk = addedUserId,
			path = prefix,
			role = rule.name,
			span = rule.span,
			count = rule.count,
			priority = None,
			creationTimestamp = self.get_datetime().timestamp()
		)
		self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]
		return PathsActionRule(
			rule.name,
			rule.span,
			rule.count,
			RulePriorityLevel.STATION_PATH.value,
			path=prefix
		)

	def remove_user_rule_from_path(
		self,
		userId: int,
		prefix: str,
		ruleName: Optional[str]
	):
		delStmt = delete(path_user_permissions_tbl)\
			.where(pup_userFk == userId)\
			.where(pup_path == prefix)
		if ruleName:
			delStmt = delStmt.where(pup_role == ruleName)
		self.conn.execute(delStmt) #pyright: ignore [reportUnknownMemberType]