#pyright: reportMissingTypeStubs=false
from datetime import timedelta
from musical_chairs_libs.dtos_and_utilities import (
	SavedNameString,
	get_datetime,
	ConfigAcessors,
	User
)
from sqlalchemy.engine import Connection
from jose import jwt


ACCESS_TOKEN_EXPIRE_MINUTES=(24 * 60 * 7)
ALGORITHM = "HS256"



class AccountTokenCreator:

	def __init__(self,
		conn: Connection,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime



	def create_access_token(
		self,
		user: User,
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
		self.conn.commit()
		return token





