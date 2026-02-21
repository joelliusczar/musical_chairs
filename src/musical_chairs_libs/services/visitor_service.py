import hashlib
import unicodedata
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	TrackingInfo,
)
from musical_chairs_libs.tables import (
	user_agents, uag_pk, uag_content, uag_hash, uag_length, uag_ipv4Address,
	uag_ipv6Address,
)
from sqlalchemy import (
	select,
	insert,
)
from sqlalchemy.engine import Connection
from typing import Any



class VisitorService:

	def __init__(self,
		conn: Connection,
		globalStore: dict[str, Any] | None = None
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime
		if globalStore is not None:
			self.__cache__ = globalStore
		else:
			self.__cache__: dict[str, Any] = {}


	def check_cache(self, trackingInfo: TrackingInfo) -> int | None:
		if trackingInfo.ipv6Address in self.__cache__:
			return self.__cache__[trackingInfo.ipv6Address]\
				.get(trackingInfo.userAgent, None)
		if trackingInfo.ipv4Address in self.__cache__:
			return self.__cache__[trackingInfo.ipv4Address]\
				.get(trackingInfo.userAgent, None)


	def add_to_cache(self, visitorId: int, trackingInfo: TrackingInfo):
		if trackingInfo.ipv6Address:
			self.__cache__[trackingInfo.ipv6Address] = {
				trackingInfo.userAgent: visitorId
			}
		if trackingInfo.ipv4Address:
			self.__cache__[trackingInfo.ipv4Address] = {
				trackingInfo.userAgent: visitorId
			}


	def add_visitor(self, trackingInfo: TrackingInfo) -> int:
		cached = self.check_cache(trackingInfo)
		if cached:
			return cached
		userAgentHash = hashlib.md5(trackingInfo.userAgent.encode()).digest()
		userAgentLen = len(trackingInfo.userAgent)
		with self.conn.begin() as transaction:
			query = select(uag_pk, uag_content)\
				.where(uag_ipv6Address == trackingInfo.ipv6Address)\
				.where(uag_ipv4Address == trackingInfo.ipv4Address)\
				.where(uag_hash == userAgentHash)\
				.where(uag_length == userAgentLen)
			results = self.conn.execute(query).mappings().fetchall()
			for row in results:
				if trackingInfo.userAgent == row[uag_content]:
					self.add_to_cache(row[uag_pk], trackingInfo)
					return row[uag_pk]
			stmt = insert(user_agents).values(
				useragenttxt = unicodedata.normalize("NFC", trackingInfo.userAgent),
				hashua = userAgentHash,
				lengthua = userAgentLen,
				ipv4address = trackingInfo.ipv4Address,
				ipv6address = trackingInfo.ipv6Address
			)
			insertedIdRow = self.conn.execute(stmt).inserted_primary_key
			if insertedIdRow:
				self.add_to_cache(insertedIdRow[0], trackingInfo)
				transaction.commit()
				return insertedIdRow[0]
			else:
				transaction.rollback()
				raise RuntimeError("Failed to create visitor id")