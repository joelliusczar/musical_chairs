#pyright: reportMissingTypeStubs=false
from datetime import timedelta
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	SavedNameString,
	get_datetime,
	ConfigAcessors
)
from musical_chairs_libs.dtos_and_utilities.constants import UserActions
from .actions_history_management_service import ActionsHistoryManagementService
from sqlalchemy.engine import Connection
from jose import jwt


ACCESS_TOKEN_EXPIRE_MINUTES=(24 * 60 * 7)
ALGORITHM = "HS256"



class AccountTokenCreator:

	def __init__(self,
		conn: Connection,
		userActionsHistoryService: ActionsHistoryManagementService
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime
		self.user_actions_history_service = userActionsHistoryService



	def create_access_token(
		self,
		user: AccountInfo,
	) -> str:
		expire = self.get_datetime() \
			+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
		token: str = jwt.encode({
				"sub": SavedNameString.format_name_for_save(user.username),
				"exp": expire
			},
			ConfigAcessors.auth_key(),
			ALGORITHM
		)
		self.user_actions_history_service.add_user_action_history_item(
			UserActions.LOGIN.value
		)
		self.conn.commit()
		return token





