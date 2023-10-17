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
from .file_service_protocol import FileServiceBase
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	normalize_opening_slash,
	squash_sequential_duplicate_chars,
	PathsActionRule,
	ChainedAbsorbentTrie,
	SongTreeNode,
	normalize_closing_slash,
	AccountInfo
)
from sqlalchemy import (
	select,
	insert,
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
)
from ..env_manager import EnvManager

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


	def create_directory(self, prefix: str, suffix: str, userId: int):
		path = normalize_opening_slash(
			squash_sequential_duplicate_chars(f"{prefix}/{suffix}/", "/"),
			addSlash=False
		)
		stmt = insert(songs_tbl).values(
			path = path,
			isdirectoryplaceholder = True,
			lastmodifiedbyuserfk = userId,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		self.conn.execute(stmt)
		self.conn.commit()

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