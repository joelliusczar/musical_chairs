import re
import uuid
from typing import (
	Any,
	BinaryIO,
	Iterator,
	cast,
	Optional,
	Tuple,
	Union,
	Iterable,
	overload,
	Collection,
	Mapping
)
from pathlib import Path
from sqlalchemy.engine import Connection
from musical_chairs_libs.protocols import FileService
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	normalize_opening_slash,
	squash_sequential_duplicate_chars,
	PathsActionRule,
	ChainedAbsorbentTrie,
	SongTreeNode,
	normalize_closing_slash,
	AccountInfo,
	SavedNameString,
	SongArtistTuple,
	AlreadyUsedError,
	SongPathInfo,
	ReusableIterable,
	DirectoryTransfer,
	int_or_default
)

from sqlalchemy import (
	select,
	insert,
	update,
	delete,
	func,
	union_all,
	String,
	Integer,
	CompoundSelect
)
from sqlalchemy.sql.expression import (
	Select
)
from musical_chairs_libs.tables import (
	songs as songs_tbl,
	sg_pk, sg_name, sg_path, sg_internalpath, sg_deletedTimstamp,
	st_pk,
	song_artist as song_artist_tbl, sgar_songFk,
	stations_songs as stations_songs_tbl, stsg_songFk,
	station_queue as station_queue_tbl, q_songFk,
)
from .env_manager import EnvManager
from .song_artist_service import SongArtistService
from .jobs_service import JobsService
from itertools import islice

class SongFileService:

	def __init__(
		self,
		conn: Connection,
		fileService: FileService,
		songArtistService: Optional[SongArtistService]=None,
		jobService: Optional[JobsService]=None
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.file_service = fileService
		self.get_datetime = get_datetime
		if not songArtistService:
			songArtistService = SongArtistService(conn)
		if not jobService:
			jobService = JobsService(conn, fileService)
		self.song_artist_service = songArtistService
		self.job_service = jobService

	def __create_directory__(
		self,
		prefix: str,
		suffix: str,
		name: str,
		user: AccountInfo,
	):
		path = normalize_opening_slash(
			squash_sequential_duplicate_chars(f"{prefix}/{suffix}/", "/"),
			addSlash=False
		)
		self.delete_overlaping_placeholder_dirs(path)
		stmt = insert(songs_tbl).values(
			path = path,
			internalpath = str(uuid.uuid4()),
			name = name,
			lastmodifiedbyuserfk = user.id,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		self.conn.execute(stmt)

	def create_directory(
		self,
		prefix: str,
		suffix: str,
		user: AccountInfo,
	) -> Mapping[str, Collection[SongTreeNode]]:
		self.__create_directory__(prefix, suffix, suffix, user)
		self.conn.commit()
		return self.song_ls_parents(user, prefix, includeTop=False)

	def save_song_file(
			self,
			file: BinaryIO,
			prefix: str,
			suffix: str,
			userId: int
		) -> SongTreeNode:
		path = normalize_opening_slash(
			squash_sequential_duplicate_chars(f"{prefix}/{suffix}", "/"),
			addSlash=False
		)
		if self.__is_path_used__(path=SavedNameString(path)):
			raise AlreadyUsedError.build_error(
				f"{path} is already used",
				"suffix"
			)
		self.delete_overlaping_placeholder_dirs(path)
		cleanedSuffix = re.sub(r"[^\w\.]+","-",suffix).casefold()
		internalPath = f"{str(uuid.uuid4())}-{cleanedSuffix}"
		songAboutInfo, fileHash = self.file_service.save_song(internalPath, file)
		stmt = insert(songs_tbl).values(
			path = path,
			internalpath = internalPath,
			name = songAboutInfo.name,
			albumfk = songAboutInfo.album.id if songAboutInfo.album else None,
			track = songAboutInfo.track,
			tracknum = int_or_default(songAboutInfo.track),
			disc = songAboutInfo.disc,
			bitrate = songAboutInfo.bitrate,
			genre = songAboutInfo.genre,
			duration = songAboutInfo.duration,
			lastmodifiedbyuserfk = userId,
			lastmodifiedtimestamp = self.get_datetime().timestamp(),
			hash = fileHash
		)
		result = self.conn.execute(stmt)
		if result.inserted_primary_key and songAboutInfo.primaryartist:
			self.song_artist_service.link_songs_with_artists(
				[SongArtistTuple(
					cast(int,result.inserted_primary_key[0]),
					songAboutInfo.primaryartist.id,
					isprimaryartist=True
				)]
			)
		self.conn.commit()
		return SongTreeNode(
			path=normalize_closing_slash(path),
			totalChildCount=1,
			id=result.lastrowid
		)

	def __song_ls_query__(
		self,
		prefix: Optional[str]=""
	) -> Select[Tuple[str, Optional[String], int, Integer, String]]:
		hasOpenSlash = False
		prefix = normalize_opening_slash(
			prefix or "",
			hasOpenSlash
		)
		likePrefix = prefix.replace("_","\\_").replace("%","\\%")
		query = select(
				func.next_directory_level(
					func.normalize_opening_slash(sg_path, hasOpenSlash),
					prefix,
					type_=String
				).label("prefix"),
				func.min(sg_name).label("name"),
				func.count(sg_pk).label("totalChildCount"),
				func.max(sg_pk).label("pk"),
				func.max(sg_path).label("control_path")
		)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(
				func.normalize_opening_slash(
					sg_path,
					hasOpenSlash
				).like(f"{likePrefix}%")
			)\
			.group_by(
				func.next_directory_level(
					func.normalize_opening_slash(sg_path, hasOpenSlash),
					prefix
				)
			)
		return query

	def __query_to_treeNodes__(
		self,
		query: Union[
			Select[Tuple[str, Optional[String], int, Integer, String]], 
			CompoundSelect[Any]
		],
		permittedPathsTree: ChainedAbsorbentTrie[PathsActionRule]
	) -> Iterator[SongTreeNode]:
		records = self.conn.execute(query).mappings()
		for row in records:
			normalizedPrefix = normalize_opening_slash(cast(str, row["prefix"]))
			if not permittedPathsTree.matches(normalizedPrefix)\
			:
				continue
			nomalizedControlPath = normalize_opening_slash(
				cast(str, row["control_path"])
			)
			if nomalizedControlPath == normalizedPrefix:
				yield SongTreeNode(
					path=cast(str, row["prefix"]),
					totalChildCount=cast(int, row["totalChildCount"]),
					id=cast(int, row["pk"]),
					name=cast(str, row["name"]),
					rules=[r for p in
						permittedPathsTree.values(normalizedPrefix) for r in p
					]
				)
			else: #directories
				yield SongTreeNode(
					path=normalize_closing_slash(cast(str, row["prefix"])),
					totalChildCount=cast(int, row["totalChildCount"]),
					rules=[r for p in
						permittedPathsTree.values(normalizedPrefix) for r in p
					]
				)

	"""
		Lists the items in a "directory".
	"""
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
			queryList: list[Select[Tuple[
				str, Optional[String], int, Integer, String]]
			] = []
			for p in prefixes:
				queryList.append(self.__song_ls_query__(p))
			if queryList:
				yield from self.__query_to_treeNodes__(
					union_all(*queryList),
					permittedPathTree
				)

	def __prefix_split__(self, prefix: str) -> Iterator[str]:
		split = prefix.split("/")
		it = iter((p for p in split if p))
		combined = next(it, "")
		if combined:
			yield "/"
		yield squash_sequential_duplicate_chars(f"/{combined}/", "/")
		for part in it:
			combined += f"/{part}"
			yield squash_sequential_duplicate_chars(f"/{combined}/", "/")

	def __build_song_tree_dict__(
		self,
		nodes: Iterable[SongTreeNode]
	) -> Mapping[str, Collection[SongTreeNode]]:
		result: dict[str, set[SongTreeNode]] = {}
		for node in nodes:
			parent = re.sub(r"/?[^/]+/?$", "/", node.path)
			if parent in result:
				result[parent].add(node)
			else:
				result[parent] = set([node])
		return result

	def song_ls_parents(
		self,
		user: AccountInfo,
		prefix: str,
		includeTop: bool=True
	) -> Mapping[str, Collection[SongTreeNode]]:
		permittedPathTree = user.get_permitted_paths_tree()
		queryList: list[
			Select[Tuple[str, Optional[String], int, Integer, String]]
		] = []

		prefixSplit = reversed([p for p in self.__prefix_split__(prefix)])

		limited = prefixSplit if includeTop else islice(prefixSplit, 3)
		for p in limited:
				queryList.append(self.__song_ls_query__(p))
		nodes = self.__query_to_treeNodes__(
			union_all(*queryList),
			permittedPathTree
		)
		result = self.__build_song_tree_dict__(nodes)
		return result


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
		query = select(sg_path).where(sg_deletedTimstamp.is_(None))
		if isinstance(itemIds, Iterable):
			query = query.where(sg_pk.in_(itemIds))
		else:
			query = query.where(sg_pk == itemIds)
		results = self.conn.execute(query)
		if useFullSystemPath:
			yield from (f"{EnvManager.absolute_content_home()}/{row[0]}" \
				for row in results
			)
		else:
			yield from (cast(str,row[0]) for row in results)

	def get_internal_song_paths(
		self,
		itemIds: Union[Iterable[int], int],
		useFullSystemPath: bool=False
	) -> Iterator[str]:
		query = select(sg_internalpath).where(sg_deletedTimstamp.is_(None))
		if isinstance(itemIds, Iterable):
			query = query.where(sg_pk.in_(itemIds))
		else:
			query = query.where(sg_pk == itemIds)
		results = self.conn.execute(query)
		if useFullSystemPath:
			yield from (f"{EnvManager.absolute_content_home()}/{row[0]}" \
				for row in results
			)
		else:
			yield from (cast(str,row[0]) for row in results)

	def get_parents_of_path(self, path: str) -> Iterator[Tuple[int, str]]:
		normalizedPrefix = normalize_opening_slash(path)
		addSlash = True
		query = select(sg_pk, sg_path)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(func.substring(
				normalizedPrefix,
				1,
				func.length(
					func.normalize_opening_slash(sg_path, addSlash)
				)
			) == func.normalize_opening_slash(sg_path, addSlash))
		results = self.conn.execute(query)
		yield from ((row[0], row[1]) for row in results)

	def delete_overlaping_placeholder_dirs(self, path: str):
		overlap = [*self.get_parents_of_path(path)]
		if any(r for r in overlap if not r[1].endswith("/")):
			raise RuntimeError("Cannot delete song entries")
		stmt = delete(songs_tbl)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(sg_pk.in_(r[0] for r in overlap))
		self.conn.execute(stmt)

	def __is_path_used__(
		self,
		path: SavedNameString,
		id: Optional[int] = None,
	) -> bool:
		queryAny = select(func.count(1))\
				.where(sg_deletedTimstamp.is_(None))\
				.where(sg_path == str(path))\
				.where(st_pk != id)
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False

	def __is_prefix_for_any__(self, prefix: str) -> bool:
		lPrefix = normalize_opening_slash(prefix)\
			.replace("_","\\_").replace("%","\\%")
		addSlash = True
		queryAny = select(func.count(1))\
			.where(sg_deletedTimstamp.is_(None))\
			.where(
				func.normalize_opening_slash(sg_path, addSlash)
				.like(f"{lPrefix}%")
			)
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False

	def __are_paths_used__(
		self,
		paths: ReusableIterable[SongPathInfo]
	) -> dict[str, bool]:
		addSlash=True
		query = select(sg_pk, sg_path)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(
			func.normalize_opening_slash(
				sg_path,
				addSlash
			).in_(p.path for p in paths))
		rows = self.conn.execute(query)
		pathToId = {
			normalize_opening_slash(cast(str, r[1])): cast(int, r[0])
			for r in rows
		}
		return {
			Path(p.path).name: (pathToId.get(p.path, p.id) != p.id)
			for p in paths
		}

	def are_paths_used(
		self,
		prefix: str,
		suffixes: Iterable[SongPathInfo]
	) -> dict[str, bool]:
		cleanedPaths = [
			SongPathInfo(
				id=p.id,
				path=str(SavedNameString(
						normalize_opening_slash(
							squash_sequential_duplicate_chars(f"{prefix}/{p.path}", "/")
						)
					)
				),
				internalpath=""
			)
			for p in suffixes
		]
		return self.__are_paths_used__(cleanedPaths)

	def is_path_used(
		self,
		id: Optional[int],
		prefix: str,
		suffix: str
	) -> bool:
		path = squash_sequential_duplicate_chars(f"{prefix}/{suffix}/", "/")
		cleanedPath = SavedNameString(path)
		if not cleanedPath:
			return True
		return self.__is_path_used__(cleanedPath, id)

	def __remove_song_references__(self, songId: int):
		stmt = delete(song_artist_tbl).where(sgar_songFk == songId)
		self.conn.execute(stmt)
		stmt = delete(station_queue_tbl).where(q_songFk == songId)
		self.conn.execute(stmt)
		stmt = delete(stations_songs_tbl).where(stsg_songFk == songId)
		self.conn.execute(stmt)

	def delete_prefix(
		self,
		prefix: str,
		user: AccountInfo
	) -> Mapping[str, Collection[SongTreeNode]]:
		_prefix = normalize_opening_slash(
				squash_sequential_duplicate_chars(prefix, "/")
			)\
				.replace("_","\\_")\
				.replace("%","\\%")
		addSlash = True
		query = select(sg_pk, sg_internalpath)\
			.where(func.normalize_opening_slash(
				sg_path,
				addSlash
			).like(f"{_prefix}%"))
		rows = self.conn.execute(query).fetchall()
		if len(rows) == 1:
			songId = cast(int, rows[0][0])
			if not prefix.endswith("/"):
				self.file_service.delete_song(rows[0][1])
				self.__remove_song_references__(songId)
			stmt = delete(songs_tbl).where(sg_pk == songId)
			self.conn.execute(stmt)
			self.conn.commit()
		else:
			self.job_service.add(r[1] for r in rows)
			self.soft_delete_songs((r[0] for r in rows), user)
			self.conn.commit()
		parentPrefix = str(Path(prefix).parent)
		return self.song_ls_parents(user, parentPrefix, includeTop=False)


	def move_path(
		self,
		transfer: DirectoryTransfer,
		user: AccountInfo
	) -> Mapping[str, Collection[SongTreeNode]]:
		if not transfer.newprefix or transfer.newprefix.isspace():
			raise ValueError("Cannot move to that directory")
		newprefix = normalize_opening_slash(
			squash_sequential_duplicate_chars(transfer.newprefix, "/")
		)
		isSrcPathBlank= not transfer.path or transfer.path.isspace()
		if isSrcPathBlank or transfer.path == user.dirroot:
			raise ValueError("Cannot move that directory")
		path = squash_sequential_duplicate_chars(transfer.path, "/")
		prefix = normalize_opening_slash(
			normalize_closing_slash(str(Path(path).parent)),
			addSlash=False
		)
		nPath = normalize_opening_slash(path)
		lPath = nPath.replace("_","\\_").replace("%","\\%")
		addSlash = True
		self.delete_overlaping_placeholder_dirs(newprefix)
		statement = update(songs_tbl)\
			.where(func.normalize_opening_slash(
				sg_path,
				addSlash
			).like(f"{lPath}%"))\
			.values(
				path = sg_path.regexp_replace(
					f"^/?{prefix}",
					newprefix
				)
			)
		self.conn.execute(statement)
		if not self.__is_prefix_for_any__(prefix):
			self.__create_directory__(
				prefix="",
				suffix=prefix,
				name=Path(prefix).stem,
				user=user
			)
		self.conn.commit()

		return self.song_ls_parents(user, newprefix, includeTop=False)
	


	def soft_delete_songs(self, songIds: Iterable[int], user: AccountInfo):
		stmt = update(songs_tbl).values(
			deletedtimestamp = self.get_datetime().timestamp(),
			deletedbyuserfk = user.id
		)\
		.where(sg_pk.in_(songIds))
		self.conn.execute(stmt)
