#pyright: reportMissingTypeStubs=false
from typing import (
	Any,
	Iterable,
	Iterator,
	Optional,
	cast,
	Union
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	SavedNameString,
	AccountCreationInfo,
	get_datetime,
	get_starting_site_roles,
	hashpw,
	validate_email,
	AccountInfoBase,
	PasswordInfo,
	ActionRule,
	AlreadyUsedError,
	build_site_rules_query,
	row_to_action_rule,
	RulePriorityLevel,
	generate_path_user_and_rules_from_rows,
	NotFoundError,
)
from musical_chairs_libs.dtos_and_utilities.constants import UserActions
from .current_user_provider import CurrentUserProvider
from .actions_history_management_service import ActionsHistoryManagementService
from .account_access_service import AccountAccessService
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import coalesce
from musical_chairs_libs.tables import (
	users, u_pk, u_username, u_email, u_dirRoot, u_disabled,
	u_displayName,
	userRoles, ur_userFk, ur_role
)
from sqlalchemy import select, insert, func, delete, update, or_
from email_validator import (
	EmailNotValidError,
	ValidatedEmail
)


ACCESS_TOKEN_EXPIRE_MINUTES=(24 * 60 * 7)
ALGORITHM = "HS256"



class AccountManagementService:

	def __init__(self,
		conn: Connection,
		userProvider: CurrentUserProvider,
		accountAccessService :AccountAccessService,
		actionsHistoryManagementService: ActionsHistoryManagementService
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime
		self.actions_history_management_service = actionsHistoryManagementService
		self.account_access_service = accountAccessService
		self.user_provider = userProvider


	def create_account(self, accountInfo: AccountCreationInfo) -> AccountInfo:
		cleanedEmail: ValidatedEmail = validate_email(accountInfo.email)
		if self.__is_username_used__(accountInfo.username):
			raise AlreadyUsedError.build_error(
				f"{accountInfo.username} is already used.",
				"body->username"
			)
		if self.__is_email_used__(cleanedEmail):
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
		self.save_roles(
			insertedPk,
			get_starting_site_roles()
		)
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


	def __get_roles__(self, userId: int) -> Iterable[ActionRule]:
		rulesQuery = build_site_rules_query(userId=userId)
		rows = self.conn.execute(rulesQuery).mappings().fetchall()

		return (row_to_action_rule(r) for r in rows)


	def __is_username_used__(self, username: str) -> bool:
		queryAny = select(func.count(1)).select_from(users)\
				.where(u_username == username)
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False


	def is_username_used(
		self,
		username: str,
	) -> bool:
		if not username:
			#if absent, assume we're not checking this right now
			#to avoid false negatives
			return True
		loggedInUser = self.user_provider.current_user(optional=True)
		loggedInUsername = loggedInUser.username if loggedInUser else None
		return loggedInUsername != username and\
			self.__is_username_used__(username)


	def __is_email_used__(self, email: ValidatedEmail) -> bool:
		emailStr = email.email
		queryAny = select(func.count(1)).select_from(users)\
				.where(func.lower(u_email) == emailStr)
		countRes = self.conn.execute(queryAny).scalar()
		return countRes > 0 if countRes else False


	def is_email_used(
		self,
		email: str,
	) -> bool:
		try:
			cleanedEmail  = validate_email(email)
			if not cleanedEmail:
				#if absent, assume we're not checking this right now
				#to avoid false negatives
				return True

			loggedInUser = self.user_provider.current_user(optional=True)
			logggedInEmail = loggedInUser.email if loggedInUser else None
			cleanedEmailStr = cleanedEmail.email
			return logggedInEmail != cleanedEmailStr and\
				self.__is_email_used__(cleanedEmail)
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
	) -> AccountInfo:
		currentUser = self.get_account_for_edit(
			self.user_provider.current_user().id
		)
		if not currentUser:
			raise NotFoundError()
		if not updatedInfo:
			return currentUser
		validEmail = validate_email(updatedInfo.email)
		updatedEmail = validEmail.email
		if updatedEmail != currentUser.email and self.__is_email_used__(validEmail):
			raise AlreadyUsedError.build_error(
				f"{updatedInfo.email} is already used.",
				"body->email"
			)
		stmt = update(users).values(
			displayname = updatedInfo.displayname,
			email = updatedEmail
		).where(u_pk == currentUser.id)
		self.conn.execute(stmt)
		self.actions_history_management_service.add_user_action_history_item(
			UserActions.ACCOUNT_UPDATE.value,
		)
		self.conn.commit()
		return AccountInfo(
			**currentUser.model_dump(exclude=["displayname", "email"]), #pyright: ignore [reportArgumentType]
				displayname = updatedInfo.displayname,
				email = updatedEmail
		)


	def update_password(
		self,
		passwordInfo: PasswordInfo
	) -> bool:
		currentUser = self.get_account_for_edit(
			self.user_provider.current_user().id
		)
		if not currentUser:
			raise NotFoundError()
		authenticated = self.account_access_service.authenticate_user(
			currentUser.username,
			passwordInfo.oldpassword.encode()
		)
		if not authenticated:
			return False
		hash = hashpw(passwordInfo.newpassword.encode())
		stmt = update(users).values(hashedpw = hash).where(u_pk == currentUser.id)
		self.conn.execute(stmt)
		self.actions_history_management_service.add_user_action_history_item(
			UserActions.CHANGE_PASS.value,
		)
		self.conn.commit()
		return True


	def get_site_rule_users(
		self,
		userId: Optional[int]=None,
		owner: Optional[AccountInfo]=None
	) -> Iterator[AccountInfo]:
		rulesQuery = build_site_rules_query().cte()
		query = select(
			u_pk,
			u_username,
			u_displayName,
			u_email,
			u_dirRoot,
			rulesQuery.c.rule_userfk.label("rule.userfk"),
			rulesQuery.c.rule_name.label("rule.name"),
			rulesQuery.c.rule_count.label("rule.count"),
			rulesQuery.c.rule_span.label("rule.span"),
			rulesQuery.c.rule_priority.label("rule.priority"),
			rulesQuery.c.rule_domain.label("rule.domain")
		).select_from(users).join(
			rulesQuery,
			rulesQuery.c.rule_userfk == u_pk,
			isouter=True
		).where(or_(u_disabled.is_(None), u_disabled == False))\
		.where(
			coalesce(
				rulesQuery.c.rule_priority,
				RulePriorityLevel.USER.value
			) > RulePriorityLevel.RULED_USER.value
		)
		if userId is not None:
			query = query.where(u_pk == userId)
		query = query.order_by(u_username)
		records = self.conn.execute(query).mappings().fetchall()
		yield from generate_path_user_and_rules_from_rows(
			records,
			owner.id if owner else None
		)

	def add_user_rule(
		self,
		addedUserId: int,
		rule: ActionRule,
	) -> ActionRule:
		stmt = insert(userRoles).values(
			userfk = addedUserId,
			role = rule.name,
			span = rule.span,
			count = rule.count,
			priority = None,
			creationtimestamp = self.get_datetime().timestamp()
		)
		try:
			self.conn.execute(stmt)
		except IntegrityError:
			raise AlreadyUsedError.build_error(
				f"{rule.name} is already used for user.",
				"body->name"
			)
		self.actions_history_management_service.add_user_action_history_item(
			UserActions.ADD_SITE_RULE.value,
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
		ruleName: Optional[str],
	):
		delStmt = delete(userRoles)\
			.where(ur_userFk == userId)
		if ruleName:
			delStmt = delStmt.where(ur_role == ruleName)
		self.conn.execute(delStmt)
		self.actions_history_management_service.add_user_action_history_item(
			UserActions.REMOVE_SITE_RULE.value,
		)
		self.conn.commit()