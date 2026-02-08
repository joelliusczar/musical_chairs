#pyright: reportMissingTypeStubs=false
import musical_chairs_libs.dtos_and_utilities as dtos
from typing import (
	Any,
	Iterable,
	Iterator,
	Optional,
)

from musical_chairs_libs.dtos_and_utilities import (
	SavedNameString,
	AccountCreationInfo,
	EmailableUser,
	get_datetime,
	get_starting_site_roles,
	hashpw,
	validate_email,
	AccountInfoUpdate,
	PasswordInfo,
	ActionRule,
	AlreadyUsedError,
	build_site_rules_query,
	RulePriorityLevel,
	generate_path_user_and_rules_from_rows,
	NotFoundError,
	User,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	hidden_token_alphabet,
	public_token_alphabet,
	UserRoleSphere,
)
from .current_user_provider import CurrentUserProvider
from .account_access_service import AccountAccessService
from nanoid import generate
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import coalesce
import musical_chairs_libs.tables as tbl
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
		accountAccessService :AccountAccessService
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime
		self.accounts_access_service = accountAccessService
		self.user_provider = userProvider


	def create_account(self, accountInfo: AccountCreationInfo) -> dtos.User:
		cleanedEmail: ValidatedEmail = validate_email(accountInfo.email)
		hashed = hashpw(accountInfo.password.encode())
		attempts = 0
		publicTokenSize = 10
		while True:
			with self.conn.begin() as transaction:
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
				try:
					publicToken = generate(
						size=publicTokenSize + attempts,
						alphabet=public_token_alphabet
					)
					hiddenToken = generate(
						size=16,
						alphabet=hidden_token_alphabet
					)
					stmt = insert(tbl.users).values(
						username=str(SavedNameString(accountInfo.username)),
						displayname=str(SavedNameString(accountInfo.displayname)),
						hashedpw=hashed,
						email=cleanedEmail.email,
						creationtimestamp=self.get_datetime().timestamp(),
						publictoken=publicToken,
						hiddentoken=hiddenToken,
						dirroot=str(SavedNameString(accountInfo.username))
					)
					res = self.conn.execute(stmt)
					insertedPk = res.lastrowid
					accountDict = accountInfo.model_dump(include={
						"username",
						"email",
						"displayname",
						"roles"
					})
					self.__save_roles__(
						insertedPk,
						get_starting_site_roles()
					)
					resultDto = dtos.User(
						id=insertedPk,
						publictoken=publicToken,
						**accountDict
					)
					transaction.commit()
					return resultDto
				except IntegrityError:
					attempts += 1
					transaction.rollback()
					if attempts > 16:
						raise


	def remove_roles_for_user(
		self,
		userId: int,
		roles: Iterable[str]
	) -> int:
		if not userId:
			return 0
		roles = roles or []
		delStmt = delete(tbl.userRoles).where(tbl.ur_userFk == userId)\
			.where(tbl.ur_role.in_(roles))
		return self.conn.execute(delStmt).rowcount


	def __save_roles__(
		self,
		userId: Optional[int],
		roles: Iterable[ActionRule]
	) -> Iterable[ActionRule]:
		if userId is None or not roles:
			return []
		uniqueRoles = set(roles)
		existingRoles = set(self.accounts_access_service.__get_roles__(userId))
		outRoles = existingRoles - uniqueRoles
		inRoles = uniqueRoles - existingRoles
		self.remove_roles_for_user(userId, (r.name for r in outRoles))
		if not inRoles:
			return uniqueRoles
		roleParams: list[dict[str, Any]] = [{
				"userfk": userId,
				"role": r.name,
				"span": r.span,
				"quota": r.quota,
				"priority": r.priority,
				"creationtimestamp": self.get_datetime().timestamp(),
				"sphere": UserRoleSphere.Site.value,
			} for r in inRoles
		]
		stmt = insert(tbl.userRoles)
		self.conn.execute(stmt, roleParams)
		return uniqueRoles


	def save_roles(
		self,
		userId: Optional[int],
		roles: Iterable[ActionRule]
	) -> Iterable[ActionRule]:
		uniqueRoles = self.__save_roles__(userId, roles)
		self.conn.commit()
		return uniqueRoles


	def __is_username_used__(self, username: str) -> bool:
		queryAny = select(func.count(1)).select_from(tbl.users)\
				.where(tbl.u_username == username.encode())
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
		queryAny = select(func.count(1)).select_from(tbl.users)\
				.where(tbl.u_email == emailStr)
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
		query = select(func.count(1)).select_from(tbl.users)
		count = self.conn.execute(query).scalar() or 0 #pyright: ignore [reportUnknownMemberType]
		return count


	def get_account_list(
		self,
		searchTerm: str | None=None,
		page: int = 0,
		pageSize: int | None=None,
	) -> Iterator[User]:
		offset = page * pageSize if pageSize else 0
		query = select(
			tbl.u_pk.label("id"), #pyright: ignore [reportUnknownMemberType]
			tbl.u_username,
			tbl.u_displayName,
			tbl.u_publictoken,
			tbl.u_dirRoot
		).offset(offset)

		if searchTerm is not None:
			normalizedStr = searchTerm.replace(" ","")\
				.replace("_","\\_").replace("%","\\%")
			query = query.where(
				func.replace(coalesce(tbl.u_displayName, tbl.u_username)," ","")
					.like(f"{normalizedStr}%", escape="\\")
			)
		query = query.limit(pageSize)
		records = self.conn.execute(query).mappings()
		for row in records:
			yield User(**row) #pyright: ignore [reportUnknownArgumentType]


	def update_account_general_changes(
		self,
		updatedInfo: AccountInfoUpdate,
	) -> EmailableUser:
		currentUser = self.accounts_access_service.get_internal_user(
			self.user_provider.current_user().id
		).to_emailable_user()
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
		stmt = update(tbl.users).values(
			displayname = updatedInfo.displayname,
			email = updatedEmail
		).where(tbl.u_pk == currentUser.id)
		self.conn.execute(stmt)
		self.conn.commit()
		return EmailableUser(
			**currentUser.model_dump(exclude=["displayname", "email"]), #pyright: ignore [reportArgumentType]
				displayname = updatedInfo.displayname,
				email = updatedEmail
		)


	def update_password(
		self,
		passwordInfo: PasswordInfo
	) -> bool:
		currentUser = self.accounts_access_service.get_internal_user(
			self.user_provider.current_user().id
		).to_user()
		if not currentUser:
			raise NotFoundError()
		authenticated = self.accounts_access_service.authenticate_user(
			currentUser.username,
			passwordInfo.oldpassword.encode()
		)
		if not authenticated:
			return False
		hash = hashpw(passwordInfo.newpassword.encode())
		stmt = update(tbl.users).values(hashedpw = hash)\
			.where(tbl.u_pk == currentUser.id)
		self.conn.execute(stmt)
		self.conn.commit()
		return True


	def get_site_rule_users(
		self,
		userId: int | None=None,
		owner: User | None=None
	) -> Iterator[dtos.RoledUser]:
		rulesQuery = build_site_rules_query().cte()
		query = select(
			tbl.u_pk,
			tbl.u_username,
			tbl.u_displayName,
			tbl.u_email,
			tbl.u_dirRoot,
			rulesQuery.c['rule>userfk'].label("rule>userfk"),
			rulesQuery.c['rule>name'].label("rule>name"),
			rulesQuery.c['rule>quota'].label("rule>quota"),
			rulesQuery.c['rule>span'].label("rule>span"),
			rulesQuery.c['rule>priority'].label("rule>priority"),
			rulesQuery.c['rule>sphere'].label("rule>sphere")
		).select_from(tbl.users).join(
			rulesQuery,
			rulesQuery.c['rule>userfk'] == tbl.u_pk,
			isouter=True
		).where(or_(tbl.u_disabled.is_(None), tbl.u_disabled == False))\
		.where(
			coalesce(
				rulesQuery.c["rule>priority"],
				RulePriorityLevel.USER.value
			) > RulePriorityLevel.RULED_USER.value
		)
		if userId is not None:
			query = query.where(tbl.u_pk == userId)
		query = query.order_by(tbl.u_username)
		records = self.conn.execute(query).mappings().fetchall()
		yield from generate_path_user_and_rules_from_rows(
			records,
			""
		)

	def add_user_rule(
		self,
		addedUserId: int,
		rule: ActionRule
	) -> ActionRule:
		stmt = insert(tbl.userRoles).values(
			userfk = addedUserId,
			role = rule.name,
			span = rule.span,
			quota = rule.quota,
			priority = None,
			keypath = None,
			sphere = UserRoleSphere.Site.value,
			creationtimestamp = self.get_datetime().timestamp()
		)
		try:
			self.conn.execute(stmt)
		except IntegrityError:
			raise AlreadyUsedError.build_error(
				f"{rule.name} is already used for user.",
				"body->name"
			)
		self.conn.commit()

		return ActionRule(
			name=rule.name,
			span=rule.span,
			quota=rule.quota,
			priority=RulePriorityLevel.SITE.value
		)


	def remove_user_site_rule(
		self,
		removedUserId: int,
		ruleName: Optional[str],
	):
		delStmt = delete(tbl.userRoles)\
			.where(tbl.ur_userFk == removedUserId)
		if ruleName:
			delStmt = delStmt.where(tbl.ur_role == ruleName)
		self.conn.execute(delStmt)
		self.conn.commit()