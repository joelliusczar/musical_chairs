from typing import Optional, Iterator, cast, Iterable
from .env_manager import EnvManager
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import Row
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	UserHistoryActionItem,
	ActionRule,
	IllegalOperationError
)
from sqlalchemy import (
	select,
	insert
)
from musical_chairs_libs.tables import (
	user_action_history, uah_userFk, uah_action, uah_timestamp
)


class UserActionsHistoryService:

	def __init__(self,
		conn: Optional[Connection]=None,
		envManager: Optional[EnvManager]=None
	) -> None:
		if not conn:
			if not envManager:
				envManager = EnvManager()
			conn = envManager.get_configured_db_connection()
		self.conn = conn
		self.get_datetime = get_datetime

	def get_user_action_history(
		self,
		userId: int,
		fromTimestamp: float,
		action: Optional[str]=None,
		limit: Optional[int]=None,
	) -> Iterator[UserHistoryActionItem]:
		query = select(uah_action, uah_timestamp).select_from(user_action_history)\
			.where(uah_timestamp >= fromTimestamp)\
			.where(uah_userFk == userId)
		if action != None:
			query = query.where(uah_action == action)
		query = query.order_by(uah_timestamp)\
			.limit(limit)
		records = self.conn.execute(query) #pyright: ignore reportUnknownMemberType
		yield from (
			UserHistoryActionItem(
				userId,
				cast(str,row[uah_action]),
				cast(float,row[uah_timestamp])
			)
			for row in cast(Iterable[Row], records)
		)

	def add_user_action_history_item(self, userId: int, action: str):
		stmt = insert(user_action_history).values(
			userFk = userId,
			action = action,
			timestamp = self.get_datetime().timestamp(),
		)
		res = self.conn.execute(stmt) #pyright: ignore reportUnknownMemberType

	def calc_when_user_can_next_do_action(
		self,
		userId: int,
		selectedRule: ActionRule,
	) -> float:
		if selectedRule.noLimit:
			return 0
		if selectedRule.blocked:
			raise IllegalOperationError(
				f"{userId} cannot do this action: {selectedRule.name}"
			)
		currentTimestamp = self.get_datetime().timestamp()
		fromTimestamp = currentTimestamp - selectedRule.span
		prevActions = [
				r for r in
				self.get_user_action_history(
					userId,
					fromTimestamp,
					selectedRule.name,
					selectedRule.count
				)
			]
		if len(prevActions) == 0:
			return 0
		if len(prevActions) == selectedRule.count:
			return prevActions[0].timestamp + selectedRule.span
		return 0