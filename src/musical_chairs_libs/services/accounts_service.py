#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
import os
from dataclasses import asdict
from datetime import timedelta, datetime, timezone
from typing import Any, Iterable, Iterator, Optional, Sequence, Tuple
from musical_chairs_libs.dtos_and_utilities import\
	AccountInfo,\
	SearchNameString,\
	SavedNameString,\
	UserRoleDef,\
	AccountCreationInfo,\
	RoleInfo,\
	get_datetime,\
	build_error_obj,\
	hashpw,\
	checkpw,\
	validate_email
from .env_manager import EnvManager
from sqlalchemy.engine import Connection
from sqlalchemy.sql import ColumnCollection
from sqlalchemy.engine.row import Row
from musical_chairs_libs.tables import users,\
	userRoles,\
	station_queue,\
	stations_history
from musical_chairs_libs.errors import AlreadyUsedError, IllegalOperationError
from sqlalchemy import select, insert, desc, func, delete, update
from jose import jwt
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


	def get_account_for_login(
		self,
		username: str
	) -> Tuple[Optional[AccountInfo], Optional[bytes]]:
		cleanedUserName = SavedNameString(username)
		if not cleanedUserName:
			return (None, None)
		query = select(u.pk, u.username, u.hashedPW, u.email)\
			.select_from(users) \
			.where((u.isDisabled != True) | (u.isDisabled == None))\
			.where(u.hashedPW != None) \
			.where(func.format_name_for_save(u.username) \
				== str(cleanedUserName)) \
			.order_by(desc(u.creationTimestamp)) \
			.limit(1)
		row = self.conn.execute(query).fetchone()
		if not row:
			return (None, None)
		pk: int = row.pk #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
		hashedPw: bytes = row.hashedPW #pyright: ignore [reportGeneralTypeIssues]
		accountInfo = AccountInfo(
			id=pk, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			username=row.username, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			email=row.email, #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
			roles=[r.role for r in self._get_roles(pk)]
		)
		return (accountInfo, hashedPw)

	def authenticate_user(self,
		username: str,
		guess: bytes
	) -> Optional[AccountInfo]:
		user, hashedPw = self.get_account_for_login(username)
		if not user:
			return None
		if hashedPw and checkpw(guess, hashedPw):
			return user
		return None

	def create_account(self, accountInfo: AccountCreationInfo) -> AccountInfo:
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
		hash = hashpw(accountInfo.password.encode())
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
		accountDict = accountInfo.scrubed_dict()
		accountDict["id"] = insertedPk #pyright: ignore [reportGeneralTypeIssues]
		accountDict["roles"] = insertedRows #pyright: ignore [reportGeneralTypeIssues]
		resultDto = AccountInfo(**accountDict)
		return resultDto

	def remove_roles_for_user(self, userId: int, roles: Iterable[str]) -> int:
		if not userId:
			return 0
		roles = roles or []
		delStmt = delete(userRoles).where(ur.userFk == userId)\
			.where(ur.role.in_(roles))
		return self.conn.execute(delStmt).rowcount #pyright: ignore [reportUnknownVariableType]

	def save_roles(
		self,
		userId: Optional[int],
		roles: Sequence[str]
	) -> Iterable[str]:
		if userId is None or not roles:
			return []
		uniqueRoles = set(UserRoleDef.remove_repeat_roles(roles))
		existingRoles = set((r.role for r in self._get_roles(userId)))
		outRoles = existingRoles - uniqueRoles
		inRoles = uniqueRoles - existingRoles
		self.remove_roles_for_user(userId, outRoles)
		if not inRoles:
			return uniqueRoles
		roleParams = [{
				"userFk": userId,
				"role": r,
				"creationTimestamp": self.get_datetime().timestamp()
			} for r in inRoles
		]
		stmt = insert(userRoles)
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

	def has_expired(self, timestamp: float) -> bool:
		dt = datetime.fromtimestamp(timestamp, timezone.utc)
		return dt < self.get_datetime()

	def get_user_from_token(self, token: str) -> Optional[AccountInfo]:
		decoded: dict[Any, Any] = jwt.decode(
			token,
			SECRET_KEY,
			algorithms=[ALGORITHM]
		)
		expiration = decoded.get("exp") or 0
		if self.has_expired(expiration):
			return None
		userName = decoded.get("sub") or ""
		user, _ = self.get_account_for_login(userName)
		if not user:
			return None
		return user

	def _get_roles(self, userPk: int) -> Iterable[RoleInfo]:
		query = select(ur.role, ur.creationTimestamp)\
			.select_from(userRoles) \
			.where(ur.userFk == userPk)
		rows: Iterable[Row] = self.conn.execute(query).fetchall()
		return (RoleInfo(
					userPk=userPk,
					role=r["role"],
					creationTimestamp=r["creationTimestamp"]
				) for r in rows)

	def last_request_timestamp(self, user: AccountInfo) -> int:
		if not user:
			return 0
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
		return lastRequested

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
			cleanedEmail  = validate_email(email)
			if not cleanedEmail:
				return True
			return self._is_email_used(cleanedEmail)
		except EmailNotValidError:
			return False

	def get_accounts_count(self) -> int:
		query = select(func.count(1)).select_from(users)
		count = self.conn.execute(query).scalar() or 0
		return count

	def get_account_list(
		self,
		page: int = 0,
		pageSize: Optional[int]=None
	) -> Iterator[AccountInfo]:
		offset = page * pageSize if pageSize else 0
		query = select(u.pk.label("id"), u.username, u.displayName, u.email)\
			.offset(offset)\
			.limit(pageSize)
		records = self.conn.execute(query)
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield AccountInfo(**row) #pyright: ignore [reportUnknownArgumentType]

	def get_account_for_edit(
		self,
		userId: Optional[int]
	) -> Optional[AccountInfo]:
		if not userId:
			return None
		query = select(u.username, u.displayName, u.email)\
			.where(u.pk == userId)

		row = self.conn.execute(query).fetchone()
		if not row:
			return None
		roles = [r.role for r in self._get_roles(userId)]
		return AccountInfo(
			id=userId,
			roles=roles,
			**row #pyright: ignore [reportGeneralTypeIssues]
		)

	def _get_account_if_can_edit(self,\
		userId: Optional[int],
		currentUser: AccountInfo
	) -> AccountInfo:
		prev = self.get_account_for_edit(userId) if userId else None
		if not prev:
			raise LookupError([build_error_obj(
				f"Account not found"
			)])
		if userId != currentUser.id and not currentUser.isAdmin:
			raise IllegalOperationError([build_error_obj(
				"Only the account owner or an admin can make changes to account"
			)])
		return prev

	def update_email(self,
		email: str,
		prev: AccountInfo
	) -> AccountInfo:
		validEmail = validate_email(email)
		updatedEmail: str = validEmail.email #pyright: ignore [reportGeneralTypeIssues]
		if updatedEmail != prev.email and self._is_email_used(validEmail):
			raise AlreadyUsedError([
				build_error_obj(f"{email} is already used.", "email")
			])
		stmt = update(users).values(email = updatedEmail)\
			.where(u.pk == prev.id)
		self.conn.execute(stmt)
		return AccountInfo(**{**asdict(prev), "email": updatedEmail}) #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]


	def update_account_general_changes(
		self,
		accountInfo: AccountInfo,
		currentUser: AccountInfo
	) -> AccountInfo:
		userId = accountInfo.id if accountInfo else None
		prev = self._get_account_if_can_edit(userId, currentUser)
		stmt = update(users).values(displayName = accountInfo.displayName)
		self.conn.execute(stmt)
		return AccountInfo(**asdict(prev), displayName=accountInfo.displayName)