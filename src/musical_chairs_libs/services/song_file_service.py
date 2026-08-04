#pyright: reportMissingTypeStubs=false
import re
import uuid
import hashlib
import itertools
import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.tables as tbl
import pathlib
import sqlalchemy as sa
import tempfile
import tinytag
import typing
import unicodedata
import unidecode
from .current_user_provider import CurrentUserProvider
from sqlalchemy.engine import Connection
from musical_chairs_libs.protocols import FileService
from sqlalchemy.sql.expression import (
	Select
)
from .song_artist_service import SongArtistService
from .jobs_service import JobsService
from .path_rule_service import PathRuleService
from .album_service import AlbumService
from .artist_service import ArtistService

class SongFileService:

	def __init__(
		self,
		conn: Connection,
		fileService: FileService,
		artistService: ArtistService,
		albumService: AlbumService,
		currentUserProvider: CurrentUserProvider,
		pathRuleService: PathRuleService,
		songArtistService: SongArtistService | None=None,
		jobService: JobsService | None=None,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.file_service = fileService
		self.get_datetime = dtos.get_datetime
		if not songArtistService:
			songArtistService = SongArtistService(conn, currentUserProvider)
		if not jobService:
			jobService = JobsService(conn, fileService)
		self.song_artist_service = songArtistService
		self.job_service = jobService
		self.artist_service = artistService
		self.album_service = albumService
		self.current_user_provider = currentUserProvider
		self.path_rule_service =  pathRuleService


	def __create_directory_in_trx__(
		self,
		prefix: str,
		suffix: str,
		name: str,
	):
		user = self.current_user_provider.current_user()

		path = dtos.normalize_opening_slash(
			dtos.squash_chars(f"{prefix}/{suffix}/", "/"),
			addSlash=False
		)
		self.delete_overlaping_placeholder_dirs_in_trx(path)
		stmt = sa.insert(tbl.songs).values(
			treepath = unicodedata.normalize("NFC", path),
			internalpath = str(uuid.uuid4()),
			name = unicodedata.normalize("NFC", name),
			lastmodifiedbyuserfk = user.id,
			lastmodifiedtimestamp = self.get_datetime().timestamp()
		)
		self.conn.execute(stmt)


	def create_directory(
		self,
		prefix: str,
		suffix: str,
	) -> typing.Mapping[str, typing.Collection[dtos.SongTreeNode]]:
		with self.conn.begin() as transaction:
			self.__create_directory_in_trx__(prefix, suffix, suffix)
			transaction.commit()
		return self.song_ls_parents(prefix, includeTop=False)


	def __rename_directory_in_trx__(
		self,
		prefix: str,
		suffix: str,
		name: str,
	) -> str:
		user = self.current_user_provider.current_user()
		pathObj = pathlib.Path(prefix)
		parent = str(pathObj.parent)
		newPath = dtos.normalize_opening_slash(
			dtos.squash_chars(f"{parent}/{suffix}/", "/"),
			addSlash=True
		)
		nOldPath = dtos.normalize_opening_slash(prefix)
		lOldPath = nOldPath.replace("_","\\_").replace("%","\\%")

		addSlash = True
		nameUpdateStmt = sa.update(tbl.songs)\
			.where(sa.func.normalize_opening_slash(
				tbl.sg_path,
				addSlash
			) == nOldPath)\
			.values(
				lastmodifiedbyuserfk = user.id,
				lastmodifiedtimestamp = self.get_datetime().timestamp(),
				name = name
			)
		childrenUpdateStmt = sa.update(tbl.songs)\
			.where(sa.func.normalize_opening_slash(
				tbl.sg_path,
				addSlash
			).like(f"{lOldPath}%", escape="\\"))\
			.values(
				treepath = tbl.sg_path.regexp_replace(
					f"^/?{re.escape(dtos.normalize_opening_slash(
						prefix,
						addSlash=False
					))}",
					newPath
				),
				lastmodifiedbyuserfk = user.id,
				lastmodifiedtimestamp = self.get_datetime().timestamp(),
			)
		self.conn.execute(nameUpdateStmt)
		self.conn.execute(childrenUpdateStmt)
		return newPath


	def rename_directory(
		self,
		prefix: str,
		suffix: str,
	) -> typing.Mapping[str, typing.Collection[dtos.SongTreeNode]]:
		with self.conn.begin() as transaction:
			newPath = self.__rename_directory_in_trx__(prefix, suffix, suffix)
			transaction.commit()
			return self.song_ls_parents(newPath, includeTop=False)


	def extract_song_info(self, file: typing.IO[bytes]) -> dtos.SongAboutInfo:
		try:
			tag = typing.cast(typing.Any, tinytag.TinyTag.get(file_obj=file)) #pyright: ignore [reportUnknownMemberType]
			songAboutInfo = dtos.SongAboutInfo(name=tag.title)
			artist = next(
				self.artist_service.get_artists(
					artistKeys=tag.artist,
					pageSize=1,
					exactStrMatch=True
				),
				None
			)
			album = next(
				self.album_service.get_albums(
					albumKeys=tag.album,
					pageSize=1,
					exactStrMatch=True
				),
				None
			)
			songAboutInfo.primaryartist = artist
			songAboutInfo.album = album
			songAboutInfo.bitrate = float(tag.bitrate) \
				if type(tag.bitrate) == float else None #pyright: ignore [reportUnknownArgumentType, reportUnknownMemberType]
			try:
				songAboutInfo.discnum = int(tag.disc or "")
			except:
				pass
			songAboutInfo.genre = tag.genre
			songAboutInfo.duration = tag.duration \
				if type(tag.duration) == float else None #pyright: ignore [reportUnknownArgumentType, reportUnknownMemberType]
			songAboutInfo.name = tag.title
			songAboutInfo.track = tag.track
			return songAboutInfo
		except Exception as e:
			print(e)
			return dtos.SongAboutInfo(name="missing")


	def save_song_file(
			self,
			file: typing.BinaryIO,
			prefix: str,
			suffix: str,
		) -> dtos.SongTreeNode:
		with self.conn.begin() as transaction:
			path = dtos.normalize_opening_slash(
				dtos.squash_chars(f"{prefix}/{suffix}", "/"),
				addSlash=False
			)
			if self.__is_path_used__(treepath=dtos.SavedNameString(path)):
				raise dtos.AlreadyUsedError.build_error(
					f"{path} is already used",
					"suffix"
				)
			user = self.current_user_provider.current_user()
			self.delete_overlaping_placeholder_dirs_in_trx(path)
			
			with tempfile.TemporaryFile() as tmp:
				for chunk in file:
					tmp.write(chunk)
				tmp.seek(0)
				
				hasher = hashlib.sha256()
				for chunk in tmp:
					hasher.update(chunk)
				fileHash = hasher.digest()
				tmp.seek(0)

				pathObj = pathlib.Path(suffix)
				extension = pathObj.suffix
				stem = pathObj.stem
				cleanedSuffix = re.sub(
					r"[^a-zA-Z?]+",
					"",
					unidecode.unidecode(stem, errors="replace")
				).casefold() or "--"
				internalDirs = "/".join([*cleanedSuffix[:10]])
				internalPath = f"{user.hiddentoken}/{internalDirs}/"\
					+ f"{str(uuid.uuid4())}-{cleanedSuffix}{extension}"
				
				songAboutInfo = self.extract_song_info(tmp)
				stmt = sa.insert(tbl.songs).values(
					treepath = unicodedata.normalize("NFC", path),
					internalpath = unicodedata.normalize("NFC", internalPath),
					name = unicodedata.normalize("NFC", songAboutInfo.name),
					albumfk = songAboutInfo.album.decoded_id()\
						if songAboutInfo.album else None,
					track = songAboutInfo.track,
					tracknum = dtos.int_or_default(songAboutInfo.track),
					discnum = songAboutInfo.discnum,
					bitrate = songAboutInfo.bitrate,
					genre = unicodedata.normalize("NFC", songAboutInfo.genre)\
						if songAboutInfo.genre else None,
					duration = songAboutInfo.duration,
					lastmodifiedbyuserfk = user.id,
					lastmodifiedtimestamp = self.get_datetime().timestamp(),
					filehash = fileHash
				)
				result = self.conn.execute(stmt)
				if result.inserted_primary_key and songAboutInfo.primaryartist:
					self.song_artist_service.link_songs_with_artists_in_trx(
						[dtos.SongArtistTuple(
							typing.cast(int,result.inserted_primary_key[0]),
							dtos.decode_id(songAboutInfo.primaryartist.id),
							isprimaryartist=True
						)]
					)
				tmp.seek(0)
				self.file_service.save_song(
					dtos.squash_chars(internalPath, "/"),
					tmp
				)
				transaction.commit()
				return dtos.SongTreeNode(
					treepath=dtos.normalize_closing_slash(path),
					totalChildCount=1,
					id=dtos.encode_song_id(result.lastrowid)
				)


	def __song_ls_query__(
		self,
		prefix: str | None=""
	) -> Select[typing.Any]:
		hasOpenSlash = False
		prefix = dtos.normalize_opening_slash(
			prefix or "",
			hasOpenSlash
		)
		likePrefix = prefix.replace("_","\\_").replace("%","\\%")
		query = sa.select(
				sa.func.next_directory_level(
					sa.func.normalize_opening_slash(tbl.sg_path, hasOpenSlash),
					prefix,
					type_=sa.String
				).label("prefix"),
				sa.func.min(tbl.sg_name).label("name"),
				sa.func.count(tbl.sg_pk).label("totalChildCount"),
				sa.func.max(tbl.sg_pk).label("pk"),
				sa.func.max(tbl.sg_path).label("control_path")
		)\
			.where(tbl.sg_deletedTimstamp.is_(None))\
			.where(
				sa.or_(
					tbl.sg_path.like(f"{likePrefix}%", escape="\\"),
					tbl.sg_path.like(f"/{likePrefix}%", escape="\\")
				)
			)\
			.group_by("prefix")
		return query


	def __query_to_treeNodes__(
		self,
		query: Select[
				typing.Tuple[str, sa.String | None, int, sa.Integer, sa.String]
			] 
			| sa.CompoundSelect[typing.Any],
		permittedPathsTree: dtos.ChainedAbsorbentTrie[dtos.ActionRule]
	) -> typing.Iterator[dtos.SongTreeNode]:
		records = self.conn.execute(query).mappings().fetchall()
		for row in records:
			normalizedPrefix = dtos.normalize_opening_slash(
				typing.cast(str, row["prefix"])
			)
			if not permittedPathsTree.matches(normalizedPrefix)\
			:
				continue
			nomalizedControlPath = dtos.normalize_opening_slash(
				typing.cast(str, row["control_path"])
			)
			if nomalizedControlPath == normalizedPrefix:
				yield dtos.SongTreeNode(
					treepath=typing.cast(str, row["prefix"]),
					totalChildCount=typing.cast(int, row["totalChildCount"]),
					id=dtos.encode_song_id(row["pk"]),
					name=typing.cast(str, row["name"]),
					rules=[r for p in
						permittedPathsTree.values(normalizedPrefix) for r in p
					]
				)
			else: #directories
				yield dtos.SongTreeNode(
					treepath=dtos.normalize_closing_slash(
						typing.cast(str, row["prefix"])
					),
					totalChildCount=typing.cast(int, row["totalChildCount"]),
					rules=[r for p in
						permittedPathsTree.values(normalizedPrefix) for r in p
					]
				)

	"""
		Lists the items in a "directory".
	"""
	def song_ls(
		self,
		prefix: str | None=None
	) -> list[dtos.SongTreeNode]:
		with dtos.open_transaction(self.conn):
			user = self.current_user_provider.get_path_rule_loaded_current_user()\
				.to_roled_user()
			permittedPathTree = self.path_rule_service.get_permitted_paths_tree(user)
			if type(prefix) == str:
				query = self.__song_ls_query__(prefix)
				return [*self.__query_to_treeNodes__(query, permittedPathTree)]
			else:
				prefixes = {
					next((s for s in p.split("/") if s), "") if p else p for p in \
					permittedPathTree.shortest_paths()
				}
				queryList: list[Select[typing.Tuple[
					str, sa.String | None, int, sa.Integer, sa.String]]
				] = []
				for p in prefixes:
					queryList.append(self.__song_ls_query__(p))
				if queryList:
					return [*self.__query_to_treeNodes__(
						sa.union_all(*queryList),
						permittedPathTree
					)]
				return []


	def __prefix_split__(self, prefix: str) -> typing.Iterator[str]:
		split = prefix.split("/")
		it = iter((p for p in split if p))
		combined = next(it, "")
		if combined:
			yield "/"
		yield dtos.squash_chars(f"/{combined}/", "/")
		for part in it:
			combined += f"/{part}"
			yield dtos.squash_chars(f"/{combined}/", "/")


	def __build_song_tree_dict__(
		self,
		nodes: typing.Iterable[dtos.SongTreeNode]
	) -> typing.Mapping[str, typing.Collection[dtos.SongTreeNode]]:
		result: dict[str, set[dtos.SongTreeNode]] = {}
		for node in nodes:
			parent = re.sub(r"/?[^/]+/?$", "/", node.treepath)
			if parent in result:
				result[parent].add(node)
			else:
				result[parent] = set([node])
		return result


	def song_ls_parents(
		self,
		prefix: str,
		includeTop: bool=True
	) -> typing.Mapping[str, typing.Collection[dtos.SongTreeNode]]:
		with dtos.open_transaction(self.conn):
			user = self.current_user_provider.get_path_rule_loaded_current_user()\
				.to_roled_user()
			permittedPathTree = self.path_rule_service.get_permitted_paths_tree(user)
			queryList: list[
				Select[typing.Tuple[str, sa.String | None, int, sa.Integer, sa.String]]
			] = []

			prefixSplit = reversed([p for p in self.__prefix_split__(prefix)])

			limited = prefixSplit if includeTop else itertools.islice(prefixSplit, 3)
			for p in limited:
					queryList.append(self.__song_ls_query__(p))
			nodes = self.__query_to_treeNodes__(
				sa.union_all(*queryList),
				permittedPathTree
			)
			result = self.__build_song_tree_dict__(nodes)
			return result


	def get_internal_song_paths(
		self,
		itemIds: typing.Iterable[int] | int,
	) -> list[str]:
		with dtos.open_transaction(self.conn):
			query = sa.select(tbl.sg_internalpath)\
				.where(tbl.sg_deletedTimstamp.is_(None))
			if isinstance(itemIds, typing.Iterable):
				query = query.where(tbl.sg_pk.in_(itemIds))
			else:
				query = query.where(tbl.sg_pk == itemIds)
			results = self.conn.execute(query).fetchall()
			return [self.file_service.song_absolute_path(typing.cast(str,row[0])) \
				for row in results
			]


	def get_parents_of_path(self, path: str) -> list[typing.Tuple[int, str]]:
		normalizedPrefix = dtos.normalize_opening_slash(path)
		addSlash = True
		query = sa.select(tbl.sg_pk, tbl.sg_path)\
			.where(tbl.sg_deletedTimstamp.is_(None))\
			.where(sa.func.substring(
				normalizedPrefix,
				1,
				sa.func.CHAR_LENGTH(
					sa.func.normalize_opening_slash(tbl.sg_path, addSlash)
				)
			) == sa.func.normalize_opening_slash(tbl.sg_path, addSlash))
		with dtos.open_transaction(self.conn):
			results = self.conn.execute(query).fetchall()
			return [(row[0], row[1]) for row in results]


	def delete_overlaping_placeholder_dirs_in_trx(self, treepath: str):
		with dtos.open_transaction(self.conn):
			overlap = [*self.get_parents_of_path(treepath)]
			if any(r for r in overlap if not r[1].endswith("/")):
				raise RuntimeError("Cannot delete song entries")
			stmt = sa.delete(tbl.songs)\
				.where(tbl.sg_deletedTimstamp.is_(None))\
				.where(tbl.sg_pk.in_(r[0] for r in overlap))
			self.conn.execute(stmt)


	def __is_path_used__(
		self,
		treepath: dtos.SavedNameString,
		id: int | None = None,
	) -> bool:
		queryAny = sa.select(sa.func.count(1))\
				.where(tbl.sg_deletedTimstamp.is_(None))\
				.where(tbl.sg_path == str(treepath))\
				.where(tbl.st_pk != id)
		with dtos.open_transaction(self.conn):
			countRes = self.conn.execute(queryAny).scalar()
			return countRes > 0 if countRes else False


	def __is_prefix_for_any__(self, prefix: str) -> bool:
		lPrefix = dtos.normalize_opening_slash(prefix)\
			.replace("_","\\_").replace("%","\\%")
		addSlash = True
		queryAny = sa.select(sa.func.count(1))\
			.where(tbl.sg_deletedTimstamp.is_(None))\
			.where(
				sa.func.normalize_opening_slash(tbl.sg_path, addSlash)
				.like(f"{lPrefix}%", escape="\\")
			)
		with dtos.open_transaction(self.conn):
			countRes = self.conn.execute(queryAny).scalar()
			return countRes > 0 if countRes else False


	def __are_paths_used__(
		self,
		treepaths: dtos.ReusableIterable[dtos.TreePathInfo]
	) -> dict[str, bool]:
		addSlash=True
		query = sa.select(tbl.sg_pk, tbl.sg_path)\
			.where(tbl.sg_deletedTimstamp.is_(None))\
			.where(
			sa.func.normalize_opening_slash(
				tbl.sg_path,
				addSlash
			).in_(p.treepath for p in treepaths))
		with dtos.open_transaction(self.conn):
			rows = self.conn.execute(query).fetchall()
			pathToId = {
				dtos.normalize_opening_slash(
					typing.cast(str, r[1])): typing.cast(int, r[0]
				)
				for r in rows
			}
			return {
				pathlib.Path(p.treepath).name : 
					(pathToId.get(p.treepath, p.decoded_id()) != p.decoded_id())
				for p in treepaths
			}


	def are_paths_used(
		self,
		prefix: str,
		suffixes: typing.Iterable[dtos.SongSuffix]
	) -> dict[str, bool]:
		cleanedPaths = [
			dtos.TreePathInfo(
				id=p.id,
				treepath=str(dtos.SavedNameString(
						dtos.normalize_opening_slash(
							dtos.squash_chars(f"{prefix}/{p.suffix}", "/")
						)
					)
				),
			)
			for p in suffixes
		]
		return self.__are_paths_used__(cleanedPaths)


	def is_path_used(
		self,
		id: int | None,
		prefix: str,
		suffix: str
	) -> bool:
		path = dtos.squash_chars(f"{prefix}/{suffix}/", "/")
		cleanedPath = dtos.SavedNameString(path)
		if not cleanedPath:
			return True
		return self.__is_path_used__(cleanedPath, id)


	def __remove_song_references_in_trx__(self, songId: int):
		stmt = sa.delete(tbl.song_artist).where(tbl.sgar_songFk == songId)
		self.conn.execute(stmt)
		stmt = sa.delete(tbl.station_queue).where(tbl.q_songFk == songId)
		self.conn.execute(stmt)
		stmt = sa.delete(tbl.stations_songs).where(tbl.stsg_songFk == songId)
		self.conn.execute(stmt)


	def delete_prefix(
		self,
		prefix: str,
	) -> typing.Mapping[str, typing.Collection[dtos.SongTreeNode]]:
		_prefix = dtos.normalize_opening_slash(
				dtos.squash_chars(prefix, "/")
			)\
				.replace("_","\\_")\
				.replace("%","\\%")
		addSlash = True
		query = sa.select(tbl.sg_pk, tbl.sg_internalpath)\
			.where(sa.func.normalize_opening_slash(
				tbl.sg_path,
				addSlash
			).like(f"{_prefix}%", escape="\\"))
		with self.conn.begin() as transaction:
			rows = self.conn.execute(query).fetchall()
			if len(rows) == 1:
				songId = typing.cast(int, rows[0][0])
				if not prefix.endswith("/"):
					self.file_service.delete_song(rows[0][1])
					self.__remove_song_references_in_trx__(songId)
				stmt = sa.delete(tbl.songs).where(tbl.sg_pk == songId)
				self.conn.execute(stmt)
				self.conn.commit()
			else:
				self.job_service.add(r[1] for r in rows)
				self.soft_delete_songs_in_trx((r[0] for r in rows))
				transaction.commit()
			parentPrefix = str(pathlib.Path(prefix).parent)
		return self.song_ls_parents(parentPrefix, includeTop=False)


	def move_path(
		self,
		transfer: dtos.DirectoryTransfer,
	) -> typing.Mapping[str, typing.Collection[dtos.SongTreeNode]]:
		if not transfer.newprefix or transfer.newprefix.isspace():
			raise ValueError("Cannot move to that directory")
		user = self.current_user_provider.current_user()
		isSrcPathBlank= not transfer.treepath or transfer.treepath.isspace()
		if isSrcPathBlank or transfer.treepath == user.dirroot:
			raise ValueError("Cannot move that directory")
		newprefix = dtos.normalize_opening_slash(
			dtos.squash_chars(transfer.newprefix, "/")
		)
		path = dtos.squash_chars(transfer.treepath, "/")
		prefix = dtos.normalize_opening_slash(
			dtos.normalize_closing_slash(str(pathlib.Path(path).parent)),
			addSlash=False
		)
		nPath = dtos.normalize_opening_slash(path)
		lPath = nPath.replace("_","\\_").replace("%","\\%")
		addSlash = True
		with self.conn.begin() as transaction:
			self.delete_overlaping_placeholder_dirs_in_trx(newprefix)
			statement = sa.update(tbl.songs)\
				.where(sa.func.normalize_opening_slash(
					tbl.sg_path,
					addSlash
				).like(f"{lPath}%", escape="\\"))\
				.values(
					treepath = sa.func.regexp_replace(
						tbl.sg_path,
						f"^/?{re.escape(prefix)}",
						newprefix
					)
				)
			self.conn.execute(statement)
			if not self.__is_prefix_for_any__(prefix):
				self.__create_directory_in_trx__(
					prefix="",
					suffix=prefix,
					name=pathlib.Path(prefix).stem,
				)
			transaction.commit()

		return self.song_ls_parents(newprefix, includeTop=False)
	


	def soft_delete_songs_in_trx(self, songIds: typing.Iterable[int]):
		user = self.current_user_provider.get_path_rule_loaded_current_user()
		stmt = sa.update(tbl.songs).values(
			deletedtimestamp = self.get_datetime().timestamp(),
			deletedbyuserfk = user.id
		)\
		.where(tbl.sg_pk.in_(songIds))
		self.conn.execute(stmt)