#pyright: reportMissingTypeStubs=false
import os
from dataclasses import asdict
from datetime import timedelta, datetime, timezone
from typing import (
	Any,
	Iterable,
	Iterator,
	Optional,
	Tuple,
	cast,
	Union
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	SearchNameString,
	SavedNameString,
	AccountCreationInfo,
	get_datetime,
	build_error_obj,
	hashpw,
	checkpw,
	validate_email,
	AccountInfoBase,
	PasswordInfo,
	ActionRule,
	AlreadyUsedError,
	RulePriorityLevel
)
from .env_manager import EnvManager
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import Row
from sqlalchemy.sql.functions import coalesce
from musical_chairs_libs.tables import (
	users, u_pk, u_username, u_hashedPW, u_email, u_dirRoot, u_disabled,
	u_creationTimestamp, u_displayName,
	userRoles, ur_userFk, ur_role, ur_span, ur_count, ur_priority,
	station_queue, q_requestedTimestamp, q_requestedByUserFk, q_playedTimestamp
)
from sqlalchemy import select, insert, desc, func, delete, update
from jose import jwt
from email_validator import (
	EmailNotValidError,
	ValidatedEmail
)


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


	def get_account_for_login(
		self,
		username: str
	) -> Tuple[Optional[AccountInfo], Optional[bytes]]:
		cleanedUserName = SavedNameString(username)
		if not cleanedUserName:
			return (None, None)
		query = select(u_pk, u_username, u_hashedPW, u_email, u_dirRoot)\
			.select_from(users) \
			.where((u_disabled != True) | (u_disabled.is_(None)))\
			.where(u_hashedPW.is_not(None)) \
			.where(func.format_name_for_save(u_username) \
				== str(cleanedUserName)) \
			.order_by(desc(u_creationTimestamp)) \
			.limit(1)
		row = self.conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
		if not row:
			return (None, None)
		pk = cast(int,row[u_pk])
		hashedPw = cast(bytes, row[u_hashedPW])
		accountInfo = AccountInfo(
			id=cast(int,row[u_pk]),
			username=cast(str,row[u_username]),
			email=cast(str,row[u_email]),
			roles=[*self.__get_roles__(pk)],
			dirRoot=cast(str, row[u_dirRoot])
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
		hashed = hashpw(accountInfo.password.encode())
		stmt = insert(users).values(
			username=SavedNameString.format_name_for_save(accountInfo.username),
			displayName=SavedNameString.format_name_for_save(accountInfo.displayName),
			hashedPW=hashed,
			email=cleanedEmail.email,
			creationTimestamp = self.get_datetime().timestamp(),
			dirRoot = SavedNameString.format_name_for_save(accountInfo.username)
		)
		res = self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]
		insertedPk = cast(int, res.lastrowid) #pyright: ignore [reportUnknownMemberType]
		# insertedRows = self.save_roles(
		# 	insertedPk,
		# 	[UserRoleDef.STATION_REQUEST.v]
		# )
		accountDict = accountInfo.scrubed_dict()
		accountDict["id"] = insertedPk #pyright: ignore [reportGeneralTypeIssues]
		# accountDict["roles"] = insertedRows #pyright: ignore [reportGeneralTypeIssues]
		resultDto = AccountInfo(**accountDict)
		return resultDto

	def remove_roles_for_user(
		self,
		userId: int,
		roles: Iterable[str]
	) -> int:
		if not userId:
			return 0
		roles = roles or []
		delStmt = delete(userRoles).where(ur_userFk == userId)\
			.where(ur_role.in_(roles))
		return self.conn.execute(delStmt).rowcount #pyright: ignore [reportUnknownVariableType, reportUnknownMemberType]

	def save_roles(
		self,
		userId: Optional[int],
		roles: Iterable[ActionRule]
	) -> Iterable[ActionRule]:
		if userId is None or not roles:
			return []
		uniqueRoles = set(roles)
		existingRoles = set(self.__get_roles__(userId))
		outRoles = existingRoles - uniqueRoles
		inRoles = uniqueRoles - existingRoles
		self.remove_roles_for_user(userId, (r.name for r in outRoles))
		if not inRoles:
			return uniqueRoles
		roleParams = [{
				"userFk": userId,
				"role": r.name,
				"span": r.span,
				"count": r.count,
				"priority": r.priority,
				"creationTimestamp": self.get_datetime().timestamp()
			} for r in inRoles
		]
		stmt = insert(userRoles)
		self.conn.execute(stmt, roleParams) #pyright: ignore [reportUnknownMemberType]
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

	def get_user_from_token(
		self,
		token: str
	) -> Tuple[Optional[AccountInfo], float]:
		if not token:
			return None, 0
		decoded: dict[Any, Any] = jwt.decode(
			token,
			SECRET_KEY,
			algorithms=[ALGORITHM]
		)
		expiration = decoded.get("exp") or 0
		if self.has_expired(expiration):
			return None, 0
		userName = decoded.get("sub") or ""
		user, _ = self.get_account_for_login(userName)
		if not user:
			return None, 0
		return user, expiration

	def __get_roles__(self, userId: int) -> Iterable[ActionRule]:
		query = select(ur_role, ur_span, ur_count, ur_priority)\
			.select_from(userRoles) \
			.where(ur_userFk == userId)
		rows = cast(Iterable[Row], self.conn.execute(query).fetchall()) #pyright: ignore [reportUnknownMemberType]
		return (ActionRule(
					cast(str, r[ur_role]),
					cast(int, r[ur_span]),
					cast(int, r[ur_count]),
					cast(int, r[ur_priority]) or RulePriorityLevel.SITE.value
				) for r in rows)

	def last_request_timestamp(self, user: AccountInfo) -> int:
		if not user:
			return 0
		queueLatestQuery = select(func.max(q_requestedTimestamp))\
			.select_from(station_queue)\
			.where(q_requestedByUserFk == user.id)
		queueLatestHistory = select(func.max(q_requestedTimestamp))\
			.select_from(station_queue)\
			.where(q_playedTimestamp.isnot(None))\
			.where(q_requestedByUserFk == user.id)
		lastRequestedInQueue = self.conn.execute(queueLatestQuery).scalar() #pyright: ignore [reportUnknownMemberType]
		lastRequestedInHistory = self.conn.execute(queueLatestHistory).scalar() #pyright: ignore [reportUnknownMemberType]
		lastRequested = max(
			(lastRequestedInQueue or 0),
			(lastRequestedInHistory or 0)
		)
		return lastRequested

	def _is_username_used(self, username: SearchNameString) -> bool:
		queryAny: str = select(func.count(1)).select_from(users)\
				.where(func.format_name_for_search(u_username) == str(username))
		countRes = self.conn.execute(queryAny).scalar() #pyright: ignore [reportUnknownMemberType]
		return countRes > 0 if countRes else False

	def is_username_used(
		self,
		username: str,
		loggedInUser: Optional[AccountInfo]=None
	) -> bool:
		cleanedUserName = SearchNameString(username)
		if not cleanedUserName:
			#if absent, assume we're not checking this right now
			#to avoid false negatives
			return True
		loggedInUsername = loggedInUser.username if loggedInUser else None
		return loggedInUsername != cleanedUserName and\
			self._is_username_used(cleanedUserName)

	def _is_email_used(self, email: ValidatedEmail) -> bool:
		emailStr = email.email #pyright: ignore reportUnknownMemberType
		queryAny: str = select(func.count(1)).select_from(users)\
				.where(func.lower(u_email) == emailStr)
		countRes = self.conn.execute(queryAny).scalar() #pyright: ignore [reportUnknownMemberType]
		return countRes > 0 if countRes else False

	def is_email_used(
		self,
		email: str,
		loggedInUser: Optional[AccountInfo]=None
	) -> bool:
		try:
			cleanedEmail  = validate_email(email)
			if not cleanedEmail:
				#if absent, assume we're not checking this right now
				#to avoid false negatives
				return True

			logggedInEmail = loggedInUser.email if loggedInUser else None
			cleanedEmailStr = cast(str, cleanedEmail.email)
			return logggedInEmail != cleanedEmailStr and\
				self._is_email_used(cleanedEmail)
		except EmailNotValidError:
			return False

	def get_accounts_count(self) -> int:
		query = select(func.count(1)).select_from(users)
		count = self.conn.execute(query).scalar() or 0 #pyright: ignore [reportUnknownMemberType]
		return count

	def get_account_list(
		self,
		searchTerm: Optional[str]=None,
		page: int = 0,
		pageSize: Optional[int]=None
	) -> Iterator[AccountInfo]:
		offset = page * pageSize if pageSize else 0
		query = select(
			u_pk.label("id"), #pyright: ignore [reportUnknownMemberType]
			u_username,
			u_displayName,
			u_email
		).offset(offset)

		if searchTerm is not None:
			normalizedStr = SearchNameString.format_name_for_search(searchTerm)\
				.replace(" ","")
			query = query.where(
				func.replace(
					func.format_name_for_search(
						coalesce(u_displayName, u_username)
					),
					" ",""
					)
					.like(f"{normalizedStr}%")
			)
		query = query.limit(pageSize)
		records = self.conn.execute(query) #pyright: ignore [reportUnknownMemberType]
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield AccountInfo(**row) #pyright: ignore [reportUnknownArgumentType]

	def get_account_for_edit(
		self,
		key: Union[int, str]
	) -> Optional[AccountInfo]:
		if not key:
			return None
		query = select(
			u_pk.label("id"), #pyright: ignore [reportUnknownMemberType]
			u_username,
			u_displayName,
			u_email
		)
		if type(key) == int:
			query = query.where(u_pk == key)
		elif type(key) == str:
			query = query.where(u_username == key)
		else:
			raise ValueError("Either username or id must be provided")
		row = self.conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
		if not row:
			return None
		roles = [*self.__get_roles__(cast(int,row["id"]))]
		return AccountInfo(
			**row, #pyright: ignore [reportGeneralTypeIssues]
			roles=roles,
		)

	def update_account_general_changes(
		self,
		updatedInfo: AccountInfoBase,
		currentUser: AccountInfo
	) -> AccountInfo:
		if not updatedInfo:
			return currentUser
		validEmail = validate_email(updatedInfo.email)
		updatedEmail = cast(str, validEmail.email)
		if updatedEmail != currentUser.email and self._is_email_used(validEmail):
			raise AlreadyUsedError([
				build_error_obj(f"{updatedInfo.email} is already used.", "email")
			])
		stmt = update(users).values(
			displayName = updatedInfo.displayName,
			email = updatedEmail
		).where(u_pk == currentUser.id)
		self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]
		return AccountInfo(
			**{**asdict(currentUser), #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]
				"displayName": updatedInfo.displayName,
				"email": updatedEmail
			}
		)

	def update_password(
		self,
		passwordInfo: PasswordInfo,
		currentUser: AccountInfo
	) -> bool:
		authenticated = self.authenticate_user(
			currentUser.username,
			passwordInfo.oldPassword.encode()
		)
		if not authenticated:
			return False
		hash = hashpw(passwordInfo.newPassword.encode())
		stmt = update(users).values(hashedPW = hash).where(u_pk == currentUser.id)
		self.conn.execute(stmt) #pyright: ignore [reportUnknownMemberType]
		return True
