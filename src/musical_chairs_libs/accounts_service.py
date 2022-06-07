#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
import bcrypt
import os
from datetime import timedelta
from typing import Any, List, Optional
from musical_chairs_libs.dtos import\
	AccountInfo,\
	UserRoleDef,\
	SaveAccountInfo
from musical_chairs_libs.env_manager import EnvManager
from sqlalchemy.engine import Connection
from sqlalchemy.sql import ColumnCollection
from sqlalchemy.engine.row import Row
from musical_chairs_libs.tables import users,\
	userRoles,\
	station_queue,\
	stations_history
from musical_chairs_libs.simple_functions import get_datetime,\
	format_name_for_save
from musical_chairs_libs.errors import AlreadyUsedError
from sqlalchemy import select, insert, desc, func, delete
from jose import jwt
from email_validator import validate_email, EmailNotValidError #pyright: ignore reportUnknownVariableType

ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM = "HS256"
SECRET_KEY=os.environ["RADIO_AUTH_SECRET_KEY"]

u: ColumnCollection = users.columns
ur: ColumnCollection = userRoles.columns
q: ColumnCollection = station_queue.columns
hist: ColumnCollection = stations_history.columns

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
		cleanedUserName = format_name_for_save(userName)
		if not cleanedUserName:
			return None
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

	def create_account(self, accountInfo: SaveAccountInfo) -> SaveAccountInfo:
		cleanedUsername = format_name_for_save(accountInfo.username)
		cleanedEmail: str = validate_email(accountInfo.email).email #pyright: ignore reportUnknownMemberType
		if self._is_username_used(cleanedUsername):
			raise AlreadyUsedError(
				f"Username {accountInfo.username} is already used."
			)
		if self._is_email_used(cleanedEmail):
			raise AlreadyUsedError(f"Email {accountInfo.email} is already used.")
		hash = bcrypt.hashpw(accountInfo.password.encode(), bcrypt.gensalt(12))
		stmt = insert(users).values(
			userName=cleanedUsername,
			displayName=accountInfo.displayName,
			hashedPW=hash,
			email=cleanedEmail,
			creationTimestamp = self.get_datetime().timestamp(),
			isActive = True
		)
		res = self.conn.execute(stmt)
		insertedPk: int = res.lastrowid
		insertedRows = self.save_roles(
			insertedPk,
			[UserRoleDef.SONG_REQUEST.modded_value("60")]
		)
		resultDto = accountInfo.copy(update={
			"id": insertedPk,
			"roles": insertedRows
		}, exclude={ "password"})
		return resultDto

	def remove_all_roles(self, userId: int) -> int:
		if not userId:
			return 0
		delStmt = delete(userRoles).where(ur.userFk == userId)
		return self.conn.execute(delStmt).rowcount #pyright: ignore [reportUnknownVariableType]

	def save_roles(self, userId: int, roles: List[str]) -> List[str]:
		if not userId or not roles:
			return []
		self.remove_all_roles(userId)
		uniqueRoles = list(UserRoleDef.remove_repeat_roles(roles))
		roleParams = list(map(
			lambda r: {
				"userFk": userId,
				"role": r,
				"isActive": True
			},
			uniqueRoles
		))
		stmt = insert(userRoles	)
		self.conn.execute(stmt, roleParams)
		return uniqueRoles


	def create_access_token(self, userName: str) -> str:
		expire = self.get_datetime() \
			+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
		token: str = jwt.encode({
				"sub": format_name_for_save(userName),
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

	def time_til_user_can_make_request(
		self,
		user: AccountInfo
	) -> int:
		if not user:
			return -1
		if user.isAdmin:
			return 0
		requestRoles = list(filter(
			lambda r: r.startswith(UserRoleDef.SONG_REQUEST.modded_value()),
			user.roles
		))
		if not any(requestRoles):
			return -1
		timeout = min(
			map(
				lambda r: UserRoleDef.extract_role_segments(r)[1] or -1,
				requestRoles
			)
		) * 60
		queueLatestQuery = select(func.max(q.requestedTimestamp))\
			.select_from(station_queue)\
			.where(q.requestedByUserFk == user.id)
		queueLatestHistory = select(func.max(hist.requestedTimestamp))\
			.select_from(stations_history)\
			.where(hist.requestedByUserFk == user.id)
		lastRequestedInQueue = self.conn.execute(queueLatestQuery).scalar()
		lastRequestedInHistory = self.conn.execute(queueLatestHistory).scalar()
		lastRequested = max(
			(lastRequestedInQueue or 0),
			(lastRequestedInHistory or 0)
		)
		timeLeft = lastRequested + timeout - self.get_datetime().timestamp()
		return int(timeLeft) if timeLeft > 0 else 0

	def _is_username_used(self, username: str) -> bool:
		queryAny: str = select(func.count(1)).select_from(users)\
				.where(func.lower(u.userName) == func.lower(username))
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False

	def is_username_used(self, username: str) -> bool:
		cleanedUserName = format_name_for_save(username)
		if not cleanedUserName:
			return True
		return self._is_username_used(cleanedUserName)

	def _is_email_used(self, email: str) -> bool:
		queryAny: str = select(func.count(1)).select_from(users)\
				.where(func.lower(u.email) == func.lower(email))
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False

	def is_email_used(self, email: str) -> bool:
		try:
			cleanedEmail: str = validate_email(email).email #pyright: ignore reportUnknownMemberType
			if not cleanedEmail:
				return True
			return self._is_email_used(cleanedEmail)
		except EmailNotValidError:
			return False


