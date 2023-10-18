from typing import (
	BinaryIO,
	Iterator,
	cast,
	Optional,
	Tuple,
	Union,
	Iterable,
	overload
)
from sqlalchemy.engine import Connection
from .saving.file_service_protocol import FileServiceBase
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	normalize_opening_slash,
	squash_sequential_duplicate_chars,
	PathsActionRule,
	ChainedAbsorbentTrie,
	SongTreeNode,
	normalize_closing_slash,
	AccountInfo,
	SavedNameString
)
from sqlalchemy import (
	select,
	insert,
	delete,
	func,
	union_all,
	String,
	CompoundSelect
)
from sqlalchemy.sql.expression import (
	Select
)
from musical_chairs_libs.tables import (
	songs as songs_tbl,
	sg_pk, sg_name, sg_path,
	st_pk
)
from .env_manager import EnvManager

class SongFileService:

	def __init__(
		self,
		conn: Connection,
		fileService: FileServiceBase
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.file_service = fileService
		self.get_datetime = get_datetime


	def create_directory(
		self,
		prefix: str,
		suffix: str,
		userId: int
	) -> SongTreeNode:
		path = normalize_opening_slash(
			squash_sequential_duplicate_chars(f"{prefix}/{suffix}/", "/"),
			addSlash=False
		)
		self.delete_overlaping_placeholder_dirs(path)
		stmt = insert(songs_tbl).values(
			path = path,
			isdirectoryplaceholder = True,
			lastmodifiedbyuserfk = userId,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		result = self.conn.execute(stmt)
		self.conn.commit()
		return SongTreeNode(
			path=normalize_closing_slash(path),
			totalChildCount=1,
			id=result.lastrowid
		)

	def save_song_file(
			self,
			file: BinaryIO,
			prefix: str,
			suffix: str,
			userId: int
		):
		path = normalize_opening_slash(
			squash_sequential_duplicate_chars(f"{prefix}/{suffix}", "/"),
			addSlash=False
		)
		self.delete_overlaping_placeholder_dirs(path)
		self.file_service.save_song(path, file)
		stmt = insert(songs_tbl).values(
			path = path,
			isdirectoryplaceholder = False,
			lastmodifiedbyuserfk = userId,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		self.conn.execute(stmt)
		self.conn.commit()


	def __song_ls_query__(
		self,
		prefix: Optional[str]=""
	) -> Select[Tuple[str, str, int, int, str]]:
		prefix = normalize_opening_slash(prefix, False)
		query = select(
				func.next_directory_level(
					sg_path,
					prefix,
					type_=String
				).label("prefix"),
				func.min(sg_name).label("name"),
				func.count(sg_pk).label("totalChildCount"),
				func.max(sg_pk).label("pk"),
				func.max(sg_path).label("control_path")
		).where(func.normalize_opening_slash(sg_path, False).like(f"{prefix}%"))\
			.group_by(func.next_directory_level(sg_path, prefix))
		return query

	def __query_to_treeNodes__(
		self,
		query: Union[Select[Tuple[str, str, int, int, str]], CompoundSelect],
		permittedPathsTree: ChainedAbsorbentTrie[PathsActionRule]
	) -> Iterator[SongTreeNode]:
		records = self.conn.execute(query).mappings()
		for row in records:
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
			else: #directories
				yield SongTreeNode(
					path=normalize_closing_slash(cast(str, row["prefix"])),
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
			queryList: list[Select[Tuple[str, str, int, int, str]]] = []
			for p in prefixes:
				queryList.append(self.__song_ls_query__(p))
			if queryList:
				yield from self.__query_to_treeNodes__(
					union_all(*queryList),
					permittedPathTree
				)

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
		results = self.conn.execute(query)
		if useFullSystemPath:
			yield from (f"{EnvManager.search_base}/{row[0]}" \
				for row in results
			)
		else:
			yield from (cast(str,row[0]) for row in results)

	def get_parents_of_path(self, path: str) -> Iterator[Tuple[int, str]]:
		normalizedPrefix = normalize_opening_slash(path)
		addSlash = True
		query = select(sg_pk, sg_path)\
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
		stmt = delete(songs_tbl).where(sg_pk.in_(r[0] for r in overlap))
		self.conn.execute(stmt)

	def __is_path_used(
		self,
		id: Optional[int],
		path: SavedNameString
	) -> bool:
		queryAny = select(func.count(1))\
				.where(sg_path == str(path))\
				.where(st_pk != id)
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False

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
		return self.__is_path_used(id, cleanedPath)