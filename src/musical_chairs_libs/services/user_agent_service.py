import hashlib
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
from typing import Optional



class UserAgentService:

	def __init__(self,
		conn: Connection,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime


	def add_user_agent(self, trackingInfo: TrackingInfo) -> Optional[int]:
		userAgentHash = hashlib.md5(trackingInfo.userAgent.encode()).digest()
		userAgentLen = len(trackingInfo.userAgent)
		query = select(uag_pk, uag_content)\
			.where(uag_hash == userAgentHash)\
			.where(uag_length == userAgentLen)\
			.where(uag_ipv4Address == trackingInfo.ipv4Address)\
			.where(uag_ipv6Address == trackingInfo.ipv6Address)
		results = self.conn.execute(query).mappings()
		for row in results:
			if trackingInfo.userAgent == row[uag_content]:
				return row[uag_pk]
		stmt = insert(user_agents).values(
			content = trackingInfo.userAgent,
			hash = userAgentHash,
			length = userAgentLen,
			ipv4address = trackingInfo.ipv4Address,
			ipv6address = trackingInfo.ipv6Address
		)
		insertedIdRow = self.conn.execute(stmt).inserted_primary_key
		if insertedIdRow:
			return insertedIdRow[0]