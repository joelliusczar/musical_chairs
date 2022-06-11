#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
import bcrypt
import os
from datetime import timedelta
from typing import Any, Iterable, Optional, Sequence
from musical_chairs_libs.dtos import\
	AccountInfo,\
	SearchNameString,\
	SavedNameString,\
	UserRoleDef,\
	SaveAccountInfo,\
	RoleInfo
from musical_chairs_libs.env_manager import EnvManager
from sqlalchemy.engine import Connection
from sqlalchemy.sql import ColumnCollection
from sqlalchemy.engine.row import Row
from musical_chairs_libs.tables import users,\
	userRoles,\
	station_queue,\
	stations_history
from musical_chairs_libs.simple_functions import get_datetime, build_error_obj
from musical_chairs_libs.errors import AlreadyUsedError
from sqlalchemy import select, insert, desc, func, delete
from jose import jwt
from email_validator import validate_email #pyright: ignore reportUnknownVariableType
from email_validator import\
	EmailNotValidError,\
	ValidatedEmail


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
		cleanedUserName = SavedNameString(userName)
		if not cleanedUserName:
			return None
		query = select(u.pk, u.username, u.hashedPW, u.email)\
			.select_from(users) \
			.where(u.isDisabled != True)\
			.where(u.hashedPW != None) \
			.where(func.format_name_for_save(u.username) \
				== str(cleanedUserName)) \
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
			roles=[r.role for r in self._get_roles(pk)]
		)

	def authenticate_user(self,
		username: str,
		guess: bytes
	) -> Optional[AccountInfo]:
		user = self.get_account(username)
		if not user:
			return None
		if user.hash:
			user.isAuthenticated = bcrypt.checkpw(guess, user.hash)
		else:
			user.isAuthenticated = False
		return user

	def create_account(self, accountInfo: SaveAccountInfo) -> SaveAccountInfo:
		cleanedUsername = SearchNameString(accountInfo.username)
		cleanedEmail: ValidatedEmail = validate_email(accountInfo.email)
		if self._is_username_used(cleanedUsername):
			raise AlreadyUsedError([
				build_error_obj(f"{accountInfo.username} is already used.", "username")
			])
		if self._is_email_used(cleanedEmail):
			raise AlreadyUsedError([
				build_error_obj(f"{accountInfo.email} is already used.", "email")
			])
		hash = bcrypt.hashpw(accountInfo.password.encode(), bcrypt.gensalt(12))
		stmt = insert(users).values(
			username=SavedNameString.format_name_for_save(accountInfo.username),
			displayName=SavedNameString.format_name_for_save(accountInfo.displayName),
			hashedPW=hash,
			email=cleanedEmail.email,
			creationTimestamp = self.get_datetime().timestamp(),
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

	def remove_roles_for_user(self, userId: int, roles: Iterable[str]) -> int:
		if not userId:
			return 0
		roles = roles or []
		delStmt = delete(userRoles).where(ur.userFk == userId)\
			.where(ur.role in roles)
		return self.conn.execute(delStmt).rowcount #pyright: ignore [reportUnknownVariableType]

	def save_roles(self, userId: int, roles: Sequence[str]) -> Iterable[str]:
		if not userId or not roles:
			return []
		uniqueRoles = set(UserRoleDef.remove_repeat_roles(roles))
		existingRoles = set((r.role for r in self._get_roles(userId)))
		outRoles = existingRoles - uniqueRoles
		inRoles = uniqueRoles - existingRoles
		self.remove_roles_for_user(userId, outRoles)
		roleParams = list(map(
			lambda r: {
				"userFk": userId,
				"role": r,
				"creationTimestamp": self.get_datetime().timestamp()
			},
			inRoles
		))
		stmt = insert(userRoles	)
		self.conn.execute(stmt, roleParams)
		return uniqueRoles


	def create_access_token(self, userName: str) -> str:
		expire = self.get_datetime() \
			+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
		token: str = jwt.encode({
				"sub": SavedNameString.format_name_for_save(userName),
				"exp": expire
			},
			SECRET_KEY,
			ALGORITHM
		)
		return token

	def get_user_from_token(self, token: str) -> Optional[AccountInfo]:
		decoded: dict[Any, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		userName = decoded.get("sub") or ""
		user = self.get_account(userName)
		if not user:
			return None
		user.isAuthenticated = True
		return user

	def _get_roles(self, userPk: int) -> Iterable[RoleInfo]:
		query = select(ur.role, ur.creationTimestamp)\
			.select_from(userRoles) \
			.where(ur.userFk == userPk)
		rows: Iterable[Row] = self.conn.execute(query).fetchall()
		return map(
				lambda r: RoleInfo(userPk,
					r.role, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
					r.creationTimestamp #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
				),
				rows
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
			roles=[r.role for r in self._get_roles(pk)]
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

	def _is_username_used(self, username: SearchNameString) -> bool:
		queryAny: str = select(func.count(1)).select_from(users)\
				.where(func.format_name_for_search(u.username) == str(username))
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False

	def is_username_used(self, username: str) -> bool:
		cleanedUserName = SearchNameString(username)
		if not cleanedUserName:
			return True
		return self._is_username_used(cleanedUserName)

	def _is_email_used(self, email: ValidatedEmail) -> bool:
		emailStr = email.email #pyright: ignore reportUnknownMemberType
		queryAny: str = select(func.count(1)).select_from(users)\
				.where(func.lower(u.email) == emailStr)
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False

	def is_email_used(self, email: str) -> bool:
		try:
			cleanedEmail:ValidatedEmail  = validate_email(email)
			if not cleanedEmail:
				return True
			return self._is_email_used(cleanedEmail)
		except EmailNotValidError:
			return False


