import hashlib
from typing import (
	Optional,
)
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
)
from sqlalchemy import (
	select,
	insert,
)
from .actions_history_query_service import (ActionsHistoryQueryService)
from musical_chairs_libs.protocols import (
	TrackingInfoProvider,
	UserProvider
)
from musical_chairs_libs.tables import (
	user_action_history, 
	user_agents, uag_pk, uag_content, uag_hash, uag_length
)



class ActionsHistoryManagementService(ActionsHistoryQueryService):

	def __init__(self,
		conn: Connection,
		trackingInfoProvider: TrackingInfoProvider,
		userProvider: UserProvider,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime
		self.tracking_info_provider = trackingInfoProvider
		self.user_provider = userProvider


	def add_user_agent(self, userAgent: str) -> Optional[int]:
		userAgentHash = hashlib.md5(userAgent.encode()).digest()
		userAgentLen = len(userAgent)
		query = select(uag_pk, uag_content)\
			.where(uag_hash == userAgentHash)\
			.where(uag_length == userAgentLen)
		results = self.conn.execute(query).mappings()
		for row in results:
			if userAgent == row[uag_content]:
				return row[uag_pk]
		stmt = insert(user_agents).values(
			content = userAgent,
			hash = userAgentHash,
			length = userAgentLen
		)
		insertedIdRow = self.conn.execute(stmt).inserted_primary_key
		if insertedIdRow:
			return insertedIdRow[0]


	def add_user_action_history_item(
			self,
			action: str,
		) -> Optional[int]:
		trackingInfo = self.tracking_info_provider.tracking_info()
		userId = self.user_provider.current_user().id
		userAgentId = self.add_user_agent(trackingInfo.userAgent)
		timestamp = self.get_datetime().timestamp()
		stmt = insert(user_action_history).values(
			userfk = userId,
			action = action,
			queuedtimestamp = timestamp,
			ipv4address = trackingInfo.ipv4Address,
			ipv6address = trackingInfo.ipv6Address,
			useragentsfk = userAgentId
		)
		insertedIdRow = self.conn.execute(stmt).inserted_primary_key
		if insertedIdRow:
			return insertedIdRow[0]
