from typing import\
	Any,\
	Iterable,\
	Iterator,\
	Optional,\
	cast,\
	Union
from sqlalchemy.engine import Connection
from sqlalchemy import select, \
	func, \
	insert, \
	delete, \
	update
from sqlalchemy.sql import ColumnCollection
from sqlalchemy.exc import IntegrityError
from .env_manager import EnvManager
from musical_chairs_libs.dtos_and_utilities import\
	SearchNameString,\
	SavedNameString,\
	Tag,\
	get_datetime,\
	build_error_obj,\
	Sentinel,\
	missing
from musical_chairs_libs.errors import AlreadyUsedError
from musical_chairs_libs.tables import\
	stations as stations_tbl, \
	tags as tags_tbl, \
	stations_tags as stations_tags_tbl, \
	songs_tags

tg: ColumnCollection = tags_tbl.columns #pyright: ignore [reportUnknownMemberType]
#sg: ColumnCollection = songs.columns #pyright: ignore [reportUnknownMemberType]
st: ColumnCollection = stations_tbl.columns #pyright: ignore [reportUnknownMemberType]
sttg: ColumnCollection = stations_tags_tbl.columns #pyright: ignore [reportUnknownMemberType]
sgtg: ColumnCollection = songs_tags.columns #pyright: ignore [reportUnknownMemberType]

tg_pk: Any = tg.pk #pyright: ignore [reportUnknownMemberType]
tg_name: Any = tg.name #pyright: ignore [reportUnknownMemberType]
st_pk: Any = st.pk #pyright: ignore [reportUnknownMemberType]
st_name: Any = st.name #pyright: ignore [reportUnknownMemberType]
sttg_tagFk: Any = sttg.tagFk #pyright: ignore [reportUnknownMemberType]
sttg_stationFk: Any = sttg.stationFk #pyright: ignore [reportUnknownMemberType]


class TagService:

	def __init__(self,
		conn: Optional[Connection]=None,
		envManager: Optional[EnvManager]=None
	):
		if not conn:
			if not envManager:
				envManager = EnvManager()
			conn = envManager.get_configured_db_connection()
		self.conn = conn
		self.get_datetime = get_datetime

	def get_tag_pk(self, tagName: str) -> Optional[int]:
		query = select(tg_pk) \
			.select_from(tags_tbl) \
			.where(func.lower(tg_name) == func.lower(tagName))
		row = self.conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
		pk = row["pk"] if row else None
		return pk

	def get_or_save_tag(self, tagName: str) -> Optional[int]:
		if not tagName:
			return None
		query = select(tg_pk).select_from(tags_tbl) \
			.where(func.lower(tg_name) == func.lower(tagName))
		row = self.conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
		if row:
			pk: int = row["pk"]
			return pk
		stmt = insert(tags_tbl).values(name = tagName)
		res = self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]
		insertedPk: int = res.lastrowid #pyright: ignore [reportUnknownMemberType]
		return insertedPk

	def get_tags_count(self) -> int:
		query = select(func.count(1)).select_from(tags_tbl)
		count = self.conn.execute(query).scalar() or 0 #pyright: ignore [reportUnknownMemberType]
		return count

	def get_tags(
		self,
		page: int = 0,
		pageSize: Optional[int]=None,
		stationId: Union[Optional[int], Sentinel]=missing,
		stationName: Union[Optional[str], Sentinel]=missing,
		tagId: Union[Optional[int], Sentinel]=missing,
		tagIds: Optional[Iterable[int]]=None
	) -> Iterator[Tag]:
		offset = page * pageSize if pageSize else 0
		query = select(tg_pk, tg_name).select_from(tags_tbl)
		if stationId:
			query = query.join(stations_tags_tbl, tg_pk == sttg_tagFk)\
				.where(sttg_stationFk == stationId)
		elif stationName and type(stationName) is str:
			searchStr = SearchNameString.format_name_for_search(stationName)
			query = query.join(stations_tags_tbl, tg_pk == sttg_tagFk)\
				.join(stations_tbl, sttg_stationFk == st_pk)\
				.where(func.format_name_for_search(st_name).like(f"%{searchStr}%"))
		if tagId:
			query = query.where(tg_pk == tagIds)
		elif tagIds:
			query = query.where(tg_pk.in_(tagIds))
		query = query.order_by(tg_name).offset(offset).limit(pageSize)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield Tag(
				id=row["pk"], #pyright: ignore [reportUnknownArgumentType]
				name=row["name"] #pyright: ignore [reportUnknownArgumentType]
			)

	def remove_tags_for_station(
		self,
		stationId: int,
		tagIds: Iterable[int]
	) -> int:
		if not stationId:
			return 0
		tagIds = tagIds or []
		delStmt = delete(stations_tags_tbl).where(sttg_stationFk == stationId)\
			.where(sttg_tagFk.in_(tagIds))
		return cast(int, self.conn.execute(delStmt).rowcount) #pyright: ignore [reportUnknownMemberType]

	def add_tags_to_station(
		self,
		stationId: int,
		tags: Optional[Iterable[Tag]],
		userId: Optional[int]=None
	) -> Iterable[Tag]:
		if stationId is None or not tags:
			return []
		uniqueTagIds = {t.id for t in tags}
		existingTags = list(self.get_tags(stationId=stationId))
		existingTagIds = {t.id for t in existingTags}
		outTagIds = existingTagIds - uniqueTagIds
		inTagIds = uniqueTagIds - existingTagIds
		self.remove_tags_for_station(stationId, outTagIds)
		if not inTagIds: #if no tags have been added
			return (t for t in existingTags if t.id not in outTagIds)
		tagParams = [{
			"stationFk": stationId,
			"tagFk": t,
			"lastModifiedByUserFk": userId,
			"lastModifiedTimestamp": self.get_datetime().timestamp()
		} for t in inTagIds]
		stmt = insert(stations_tags_tbl)
		self.conn.execute(stmt, tagParams) #pyright: ignore [reportUnknownMemberType]
		return self.get_tags(stationId=stationId)

	def save_tag(
		self,
		tagName: str,
		tagId: Optional[int]=None,
		userId: Optional[int]=None
	) -> Tag:
		if not tagName and not tagId:
			return Tag(id=-1, name="")
		upsert = update if tagId else insert
		savedName = SavedNameString(tagName)
		stmt = upsert(tags_tbl).values(
			name = str(savedName),
			lastModifiedByUserFk = userId,
			lastModifiedTimestamp = self.get_datetime().timestamp()
		)
		if tagId:
			stmt = stmt.where(tg_pk == tagId)
		try:
			res = self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]

			affectedPk: int = tagId if tagId else res.lastrowid #pyright: ignore [reportUnknownMemberType]
			return Tag(id=affectedPk, name=str(savedName))
		except IntegrityError:
			raise AlreadyUsedError(
				[build_error_obj(
					f"{tagName} is already used.", "name"
				)]
			)

	def delete_tag(self, tagId: int) -> int:
		stmt = delete(tags_tbl).where(tg_pk == tagId)
		res = self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]
		return cast(int, res.rowcount) or 0 #pyright: ignore [reportUnknownMemberType]


