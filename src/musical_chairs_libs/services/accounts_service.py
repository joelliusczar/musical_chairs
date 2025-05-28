#pyright: reportMissingTypeStubs=false
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
	SavedNameString,
	AccountCreationInfo,
	get_datetime,
	hashpw,
	checkpw,
	validate_email,
	AccountInfoBase,
	PasswordInfo,
	ActionRule,
	AlreadyUsedError,
	build_rules_query,
	row_to_action_rule,
	UserRoleDomain,
	RulePriorityLevel,
	MinItemSecurityLevel,
	generate_user_and_rules_from_rows,
	UserActions
)
from .user_actions_history_service import UserActionsHistoryService
from .env_manager import EnvManager
from sqlalchemy.engine import Connection
from sqlalchemy.sql.functions import coalesce
from musical_chairs_libs.tables import (
	users, u_pk, u_username, u_hashedPW, u_email, u_dirRoot, u_disabled,
	u_creationTimestamp, u_displayName,
	userRoles, ur_userFk, ur_role
)
from sqlalchemy import select, insert, desc, func, delete, update, or_
from jose import jwt
from email_validator import (
	EmailNotValidError,
	ValidatedEmail
)


ACCESS_TOKEN_EXPIRE_MINUTES=(24 * 60 * 7)
ALGORITHM = "HS256"



class AccountsService:

	def __init__(self,
		conn: Connection,
		userActionsHistoryService: Optional[UserActionsHistoryService]=None
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		if not userActionsHistoryService:
			userActionsHistoryService = UserActionsHistoryService(conn)
		self.conn = conn
		self._system_user: Optional[AccountInfo] = None
		self.get_datetime = get_datetime
		self.user_actions_history_service = userActionsHistoryService


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
			.where(u_username \
				== str(cleanedUserName)) \
			.order_by(desc(u_creationTimestamp)) \
			.limit(1)
		row = self.conn.execute(query).mappings().fetchone()
		if not row:
			return (None, None)
		pk = cast(int,row[u_pk])
		hashedPw = cast(bytes, row[u_hashedPW])
		accountInfo = AccountInfo(
			id=cast(int,row[u_pk]),
			username=cast(str,row[u_username]),
			email=cast(str,row[u_email]),
			roles=[*self.__get_roles__(pk)],
			dirroot=cast(str, row[u_dirRoot])
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
		cleanedEmail: ValidatedEmail = validate_email(accountInfo.email)
		if self._is_username_used(accountInfo.username):
			raise AlreadyUsedError.build_error(
				f"{accountInfo.username} is already used.",
				"body->username"
			)
		if self._is_email_used(cleanedEmail):
			raise AlreadyUsedError.build_error(
				f"{accountInfo.email} is already used.",
				"body->email"
			)
		hashed = hashpw(accountInfo.password.encode())
		stmt = insert(users).values(
			username=SavedNameString.format_name_for_save(accountInfo.username),
			displayname=SavedNameString.format_name_for_save(accountInfo.displayname),
			hashedpw=hashed,
			email=cleanedEmail.email,
			creationtimestamp = self.get_datetime().timestamp(),
			dirroot = SavedNameString.format_name_for_save(accountInfo.username)
		)
		res = self.conn.execute(stmt)
		insertedPk = res.lastrowid
		accountDict = accountInfo.scrubed_dict()
		accountDict["id"] = insertedPk #pyright: ignore [reportGeneralTypeIssues]
		resultDto = AccountInfo(**accountDict)
		self.conn.commit()
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
		return self.conn.execute(delStmt).rowcount

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
		roleParams: list[dict[str, Any]] = [{
				"userfk": userId,
				"role": r.name,
				"span": r.span,
				"count": r.count,
				"priority": r.priority,
				"creationtimestamp": self.get_datetime().timestamp()
			} for r in inRoles
		]
		stmt = insert(userRoles)
		self.conn.execute(stmt, roleParams)
		self.conn.commit()
		return uniqueRoles


	def create_access_token(self, user: AccountInfo) -> str:
		expire = self.get_datetime() \
			+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
		token: str = jwt.encode({
				"sub": SavedNameString.format_name_for_save(user.username),
				"exp": expire
			},
			EnvManager.secret_key(),
			ALGORITHM
		)
		self.user_actions_history_service.add_user_action_history_item(
			user.id,
			UserActions.LOGIN.value
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
			EnvManager.secret_key(),
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
		rulesQuery = build_rules_query(UserRoleDomain.Site, userId=userId)
		rows = self.conn.execute(rulesQuery).mappings().fetchall()

		return (row_to_action_rule(r) for r in rows)


	def _is_username_used(self, username: str) -> bool:
		queryAny = select(func.count(1)).select_from(users)\
				.where(u_username == username)
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False

	def is_username_used(
		self,
		username: str,
		loggedInUser: Optional[AccountInfo]=None
	) -> bool:
		if not username:
			#if absent, assume we're not checking this right now
			#to avoid false negatives
			return True
		loggedInUsername = loggedInUser.username if loggedInUser else None
		return loggedInUsername != username and\
			self._is_username_used(username)

	def _is_email_used(self, email: ValidatedEmail) -> bool:
		emailStr = cast(str, email.email)
		queryAny = select(func.count(1)).select_from(users)\
				.where(func.lower(u_email) == emailStr)
		countRes = self.conn.execute(queryAny).scalar()
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
			u_email,
			u_dirRoot
		).offset(offset)

		if searchTerm is not None:
			normalizedStr = searchTerm.replace(" ","")\
				.replace("_","\\_").replace("%","\\%")
			query = query.where(
				func.replace(coalesce(u_displayName, u_username)," ","")
					.like(f"{normalizedStr}%")
			)
		query = query.limit(pageSize)
		records = self.conn.execute(query).mappings()
		for row in records:
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
			u_email,
			u_dirRoot
		)
		if type(key) == int:
			query = query.where(u_pk == key)
		elif type(key) == str:
			query = query.where(u_username == key)
		else:
			raise ValueError("Either username or id must be provided")
		row = self.conn.execute(query).mappings().fetchone()
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
			raise AlreadyUsedError.build_error(
				f"{updatedInfo.email} is already used.",
				"body->email"
			)
		stmt = update(users).values(
			displayname = updatedInfo.displayname,
			email = updatedEmail
		).where(u_pk == currentUser.id)
		self.conn.execute(stmt)
		self.user_actions_history_service.add_user_action_history_item(
			currentUser.id,
			UserActions.ACCOUNT_UPDATE.value
		)
		self.conn.commit()
		return AccountInfo(
			**currentUser.model_dump(exclude=["displayname", "email"]), #pyright: ignore [reportArgumentType]
				displayname = updatedInfo.displayname,
				email = updatedEmail
		)

	def update_password(
		self,
		passwordInfo: PasswordInfo,
		currentUser: AccountInfo
	) -> bool:
		authenticated = self.authenticate_user(
			currentUser.username,
			passwordInfo.oldpassword.encode()
		)
		if not authenticated:
			return False
		hash = hashpw(passwordInfo.newpassword.encode())
		stmt = update(users).values(hashedPW = hash).where(u_pk == currentUser.id)
		self.conn.execute(stmt)
		self.user_actions_history_service.add_user_action_history_item(
			currentUser.id,
			UserActions.CHANGE_PASS.value
		)
		self.conn.commit()
		return True

	def get_site_rule_users(
		self,
		userId: Optional[int]=None,
		owner: Optional[AccountInfo]=None
	) -> Iterator[AccountInfo]:
		rulesQuery = build_rules_query(UserRoleDomain.Site).cte()
		query = select(
			u_pk,
			u_username,
			u_displayName,
			u_email,
			u_dirRoot,
			rulesQuery.c.rule_userfk,
			rulesQuery.c.rule_name,
			rulesQuery.c.rule_count,
			rulesQuery.c.rule_span,
			rulesQuery.c.rule_priority,
			rulesQuery.c.rule_domain
		).select_from(users).join(
			rulesQuery,
			rulesQuery.c.rule_userfk == u_pk,
			isouter=True
		).where(or_(u_disabled.is_(None), u_disabled == False))\
		.where(
			coalesce(
				rulesQuery.c.rule_priority,
				RulePriorityLevel.USER.value
			) > MinItemSecurityLevel.RULED_USER.value
		)
		if userId is not None:
			query = query.where(u_pk == userId)
		query = query.order_by(u_username)
		records = self.conn.execute(query).mappings().fetchall()
		yield from generate_user_and_rules_from_rows(
			records,
			UserRoleDomain.Path,
			owner.id if owner else None
		)

	def add_user_rule(
		self,
		addedUserId: int,
		rule: ActionRule
	) -> ActionRule:
		stmt = insert(userRoles).values(
			userfk = addedUserId,
			role = rule.name,
			span = rule.span,
			count = rule.count,
			priority = None,
			creationtimestamp = self.get_datetime().timestamp()
		)
		self.conn.execute(stmt)
		self.user_actions_history_service.add_user_action_history_item(
			addedUserId,
			UserActions.ADD_SITE_RULE.value
		)
		self.conn.commit()

		return ActionRule(
			name=rule.name,
			span=rule.span,
			count=rule.count,
			priority=RulePriorityLevel.SITE.value
		)

	def remove_user_site_rule(
		self,
		userId: int,
		ruleName: Optional[str]
	):
		delStmt = delete(userRoles)\
			.where(ur_userFk == userId)
		if ruleName:
			delStmt = delStmt.where(ur_role == ruleName)
		self.conn.execute(delStmt)
		self.user_actions_history_service.add_user_action_history_item(
			userId,
			UserActions.REMOVE_SITE_RULE.value
		)
		self.conn.commit()