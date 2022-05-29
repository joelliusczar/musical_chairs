#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
import bcrypt
import os
from datetime import timedelta
from typing import Any, List, Optional
from musical_chairs_libs.dtos import AccountInfo
from musical_chairs_libs.env_manager import EnvManager
from sqlalchemy.engine import Connection
from sqlalchemy.sql import ColumnCollection
from sqlalchemy.engine.row import Row
from musical_chairs_libs.tables import users, userRoles
from musical_chairs_libs.simple_functions import get_datetime
from sqlalchemy import select, insert, desc, func
from jose import jwt
from enum import Enum

class UserRoleDef(Enum):
	ADMIN = "admin"
	SONG_REQUEST = "song:request:"


ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM = "HS256"
SECRET_KEY=os.environ["RADIO_AUTH_SECRET_KEY"]

class AccountsService:

	def __init__(self,
		conn: Optional[Connection]=None,
		envManager: Optional[EnvManager]=None
	) -> None:
		if not conn:
			if not envManager:
				envManager = EnvManager()
			conn = envManager.get_configured_db_connection()
		self.conn = conn
		self._system_user: Optional[AccountInfo] = None
		self.get_datetime = get_datetime


	def get_account(self, userName: str) -> Optional[AccountInfo]:
		cleanedUserName = userName.strip() if userName else None
		if not cleanedUserName:
			return None
		u: ColumnCollection = users.columns
		query = select(u.pk, u.userName, u.hashedPW, u.email)\
			.select_from(users) \
			.where(u.hashedPW != None) \
			.where(func.lower(u.userName) == func.lower(cleanedUserName)) \
			.order_by(desc(u.creationTimestamp)) \
			.limit(1)
		row = self.conn.execute(query).fetchone()
		if not row:
			return None
		pk: int = row.pk #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
		return AccountInfo(
			pk, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			row.userName, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			row.hashedPW, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			row.email, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			roles=self._get_roles(pk)
		)

	def authenticate_user(self,
		userName: str,
		guess: bytes
	) -> Optional[AccountInfo]:
		user = self.get_account(userName)
		if not user:
			return None
		if user.hash:
			user.isAuthenticated = bcrypt.checkpw(guess, user.hash)
		else:
			user.isAuthenticated = False
		return user

	def create_account(self, userName: str,
		pw: bytes,
		email: Optional[str]=None
	) -> bool:
		cleanedUserName = userName.strip() if userName else None
		if not cleanedUserName:
			return False
		cleanedEmail = email.strip() if email else None
		u: ColumnCollection = users.columns
		queryAny: str = select(func.count(1)).select_from(users)\
			.where(func.lower(u.userName) == func.lower(cleanedUserName))
		countRes = self.conn.execute(queryAny).scalar()
		count: int = countRes if countRes else 0
		if count > 0:
			return False
		hash = bcrypt.hashpw(pw, bcrypt.gensalt(12))
		stmt = insert(users).values(
			userName=cleanedUserName,
			hashedPW=hash,
			email=cleanedEmail,
			creationTimestamp = self.get_datetime().timestamp(),
			isActive = True
		)
		self.conn.execute(stmt)
		return True

	def create_access_token(self, userName: str) -> str:
		expire = self.get_datetime() \
			+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
		token: str = jwt.encode({
				"sub": userName,
				"exp": expire
			},
			SECRET_KEY,
			ALGORITHM
		)
		return token

	def get_user_from_token(self, token: str) -> Optional[AccountInfo]:
		decoded: dict[Any, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		userName = decoded.get("sub")
		user = self.get_account(userName)
		if not user:
			return None
		user.isAuthenticated = True
		return user

	def _get_roles(self, userPk: int) -> List[str]:
		ur: ColumnCollection = userRoles.columns
		query = select(ur.role)\
			.select_from(userRoles) \
			.where(ur.userFk == userPk)
		rows: List[Row] = self.conn.execute(query).fetchall()
		return list(map(
				lambda r: r.role, #pyright: ignore [reportUnknownLambdaType, reportGeneralTypeIssues]
				rows
			)
		)

	@property
	def system_user(self) -> Optional[AccountInfo]:
		if self._system_user:
			return self._system_user
		u: ColumnCollection = users.columns
		query = select(u.pk, u.userName)\
			.select_from(users) \
			.where(func.lower(u.userName) == "system") \
			.order_by(desc(u.creationTimestamp)) \
			.limit(1)
		row = self.conn.execute(query).fetchone()
		if not row:
			return None
		pk: int = row.pk #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
		return AccountInfo(
			pk, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			row.userName, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			None,
			None,
			roles=self._get_roles(pk)
		)