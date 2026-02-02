#pyright: reportMissingTypeStubs=false
from datetime import datetime, timezone
from typing import (
	Any,
	Iterable,
	Optional,
	Tuple,
	cast,
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	SavedNameString,
	get_datetime,
	checkpw,
	ActionRule,
	build_site_rules_query,
	row_to_action_rule,
	ConfigAcessors
)
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import (
	users, u_pk, u_username, u_hashedPW, u_email, u_dirRoot, u_disabled,
	u_creationTimestamp,
)
from sqlalchemy import select, desc, func
from jose import jwt


ACCESS_TOKEN_EXPIRE_MINUTES=(24 * 60 * 7)
ALGORITHM = "HS256"



class AccountAccessService:

	def __init__(self,
		conn: Connection
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
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
			ConfigAcessors.auth_key(),
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
		rulesQuery = build_site_rules_query(userId=userId)
		rows = self.conn.execute(rulesQuery).mappings()

		return (row_to_action_rule(r) for r in rows)



	def get_accounts_count(self) -> int:
		query = select(func.count(1)).select_from(users)
		count = self.conn.execute(query).scalar() or 0 #pyright: ignore [reportUnknownMemberType]
		return count





