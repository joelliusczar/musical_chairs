#pyright: reportMissingTypeStubs=false
from datetime import datetime, timezone
from typing import (
	Any,
	Iterable,
	Tuple,
	cast,
)
from musical_chairs_libs.dtos_and_utilities import (
	ActionRule,
	build_site_rules_query,
	checkpw,
	ConfigAcessors,
	get_datetime,
	InternalUser,
	row_to_action_rule,
	SavedNameString,
	NotFoundError
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	public_token_prefix
)
from sqlalchemy.engine import Connection
from sqlalchemy import select, desc, func
from jose import jwt
import musical_chairs_libs.tables as tbl


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


	def get_internal_user(self, key: int | str) -> InternalUser:

		query = select(
			tbl.u_pk.label("id"), #pyright: ignore [reportUnknownMemberType]
			tbl.u_username,
			tbl.u_displayName,
			tbl.u_email,
			tbl.u_publictoken,
			tbl.u_hiddentoken,
			tbl.u_dirRoot
		)
		if type(key) == int:
			query = query.where(tbl.u_pk == key)	
		elif type(key) == str:
			if key.startswith(public_token_prefix):
				query = query.where(tbl.u_publictoken == key[2:].encode())
			else:
				query = query.where(tbl.u_username == key)
		else:
			raise ValueError("Either username or id must be provided")
		row = self.conn.execute(query).mappings().fetchone()
		if not row:
			raise NotFoundError()
		roles = [*self.__get_roles__(int(row["id"]))]
		return InternalUser(
			**row, #pyright: ignore [reportGeneralTypeIssues]
			roles=roles,
		)


	def get_account_for_login(
		self,
		username: str
	) -> Tuple[InternalUser | None, bytes | None]:
		cleanedUserName = SavedNameString(username)
		if not cleanedUserName:
			return (None, None)
		query = select(
			tbl.u_pk,
			tbl.u_username,
			tbl.u_hashedPW,
			tbl.u_publictoken,
			tbl.u_hiddentoken,
			tbl.u_email,
			tbl.u_dirRoot
		)\
			.select_from(tbl.users) \
			.where((tbl.u_disabled != True) | (tbl.u_disabled.is_(None)))\
			.where(tbl.u_hashedPW.is_not(None)) \
			.where(tbl.u_username \
				== str(cleanedUserName)) \
			.order_by(desc(tbl.u_creationTimestamp)) \
			.limit(1)
		row = self.conn.execute(query).mappings().fetchone()
		if not row:
			return (None, None)
		pk = cast(int,row[tbl.u_pk])
		hashedPw = cast(bytes, row[tbl.u_hashedPW])
		accountInfo = InternalUser(
			id=pk,
			username=cast(str,row[tbl.u_username]),
			publictoken=row[tbl.u_publictoken],
			hiddentoken=row[tbl.u_hiddentoken],
			email=row[tbl.u_email],
			roles=[*self.__get_roles__(pk)],
			dirroot=row[tbl.u_dirRoot]
		)
		return (accountInfo, hashedPw)


	def authenticate_user(self,
		username: str,
		guess: bytes
	) -> InternalUser | None:
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
	) -> Tuple[InternalUser | None, float]:
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
		user = self.get_internal_user(userName)
		if not user:
			return None, 0
		return user, expiration


	def __get_roles__(self, userId: int) -> Iterable[ActionRule]:
		rulesQuery = build_site_rules_query(userId=userId)
		rows = self.conn.execute(rulesQuery).mappings()

		return (row_to_action_rule(r) for r in rows)



	def get_accounts_count(self) -> int:
		query = select(func.count(1)).select_from(tbl.users)
		count = self.conn.execute(query).scalar() or 0 #pyright: ignore [reportUnknownMemberType]
		return count




