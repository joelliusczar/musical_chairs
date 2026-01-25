from typing import Optional, cast, Iterable, Iterator, Tuple
from sqlalchemy.sql.expression import Select, false, CompoundSelect
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.schema import Column
from sqlalchemy.engine.row import RowMapping
from sqlalchemy import (
	select,
	union_all,
	literal as dbLiteral,
	case,
	or_
)
from sqlalchemy import Integer, String, Float
from musical_chairs_libs.tables import (
	ur_userFk, ur_role, ur_count, ur_span, ur_priority,
	u_username, u_pk, u_displayName, u_email, u_dirRoot,
	pup_role, pup_userFk, pup_count, pup_span, pup_priority, pup_path
)
from .user_role_def import (
	UserRoleDef,
	RulePriorityLevel,
)
from .action_rule_dtos import (
	ActionRule,
)
from .account_dtos import (
	AccountInfo,
	get_station_owner_rules,
	get_path_owner_roles,
	get_playlist_owner_roles
)
from .constants import UserRoleDomain
from .simple_functions import normalize_opening_slash



__path_permissions_query__ = select(
	pup_userFk.label("rule_userfk"),
	pup_role.label("rule_name"),
	pup_count.label("rule_count"),
	pup_span.label("rule_span"),
	coalesce[Integer](
		pup_priority,
		RulePriorityLevel.STATION_PATH.value
	).label("rule_priority"),
	dbLiteral(UserRoleDomain.Path.value).label("rule_domain"),
	pup_path.label("rule_path")
)

def build_placeholder_select(
	ruleNameValue: str
) -> Select[Tuple[int, str, float, float, int, str]]:

	query = select(
		dbLiteral(0).label("rule_userfk"),
		dbLiteral(ruleNameValue).label("rule_name"),
		cast(Column[float],dbLiteral(0)).label("rule_count"),
		cast(Column[float],dbLiteral(0)).label("rule_span"),
		dbLiteral(0).label("rule_priority"),
		dbLiteral("shim").label("rule_domain"),
	)

	return query



def build_path_rules_query(
	userId: Optional[int]=None
) -> CompoundSelect[
			Tuple[
				Integer, String, Float[float], Float[float], Integer, str, String
			]
		]:

	user_rules_query = select(
		ur_userFk.label("rule_userfk"),
		ur_role.label("rule_name"),
		ur_count.label("rule_count"),
		ur_span.label("rule_span"),
		coalesce[Integer](
			ur_priority,
			case(
				(ur_role == UserRoleDef.ADMIN.value, RulePriorityLevel.SUPER.value),
				else_=RulePriorityLevel.SITE.value
			)
		).label("rule_priority"),
		dbLiteral(UserRoleDomain.Site.value).label("rule_domain"),
		dbLiteral(None).label("rule_path")
	).where(or_( #this part is only applies if there is a user id
			ur_role.like(f"{UserRoleDomain.Path.value}:%"),
			ur_role == UserRoleDef.ADMIN.value
		)
	)

	path_permissions_query = __path_permissions_query__
	placeholder_select = build_placeholder_select(
		UserRoleDef.PATH_VIEW.value
	).add_columns(
		dbLiteral(None).label("rule_path")
	)

	if userId is not None:
		path_permissions_query =\
			path_permissions_query.where(pup_userFk == userId)
		user_rules_query = user_rules_query.where(ur_userFk == userId)
	else:
		user_rules_query = user_rules_query.where(false())

	query = union_all(
		path_permissions_query,
		user_rules_query,
		placeholder_select
	)
	return query

def build_site_rules_query(
	userId: Optional[int]=None
) -> Select[Tuple[Integer, String, Float[float], Float[float], Integer, str]]:

	user_rules_query = select(
		ur_userFk.label("rule.userfk"),
		ur_role.label("rule.name"),
		ur_count.label("rule.count"),
		ur_span.label("rule.span"),
		coalesce[Integer](
			ur_priority,
			case(
				(ur_role == UserRoleDef.ADMIN.value, RulePriorityLevel.SUPER.value),
				else_=RulePriorityLevel.SITE.value
			)
		).label("rule.priority"),
		dbLiteral(UserRoleDomain.Site.value).label("rule.domain"),
	)

	if userId is not None:
		user_rules_query = user_rules_query.where(ur_userFk == userId)

	return user_rules_query

def row_to_user(row: RowMapping) -> AccountInfo:
	return AccountInfo(
		id=row[u_pk],
		username=row[u_username],
		displayname=row[u_displayName],
		email=row[u_email],
		dirroot=row[u_dirRoot],
	)

def row_to_action_rule(row: RowMapping) -> ActionRule:

	return ActionRule(
		name=row["rule.name"],
		span=row["rule.span"],
		count=row["rule.count"],
		#if priortity is explict use that
		#otherwise, prefer station specific rule vs non station specific rule
		priority=cast(int,row["rule.priority"]) if row["rule.priority"] \
			else RulePriorityLevel.STATION_PATH.value,
		domain=row["rule.domain"]
	)

def generate_station_user_and_rules_from_rows(
	rows: Iterable[RowMapping],
	ownerId: Optional[int]=None,
	prefix: Optional[str]=None
) -> Iterator[AccountInfo]:
	currentUser = None
	for row in rows:
		if not currentUser or currentUser.id != cast(int,row[u_pk]):
			if currentUser:
				if currentUser.id == ownerId:
					currentUser.roles.extend(get_station_owner_rules())
				yield currentUser
			currentUser = row_to_user(row)
			if row["rule.domain"] != "shim":
				currentUser.roles.append(row_to_action_rule(row))
		elif row["rule.domain"] != "shim":
			currentUser.roles.append(row_to_action_rule(row))
	if currentUser:
		if currentUser.id == ownerId:
			currentUser.roles.extend(get_station_owner_rules())
		yield currentUser

def generate_playlist_user_and_rules_from_rows(
	rows: Iterable[RowMapping],
	ownerId: Optional[int]=None,
	prefix: Optional[str]=None
) -> Iterator[AccountInfo]:
	currentUser = None
	for row in rows:
		if not currentUser or currentUser.id != cast(int,row[u_pk]):
			if currentUser:
				if currentUser.id == ownerId:
					currentUser.roles.extend(get_playlist_owner_roles())
				yield currentUser
			currentUser = row_to_user(row)
			if row["rule.domain"] != "shim":
				currentUser.roles.append(row_to_action_rule(row))
		elif row["rule.domain"] != "shim":
			currentUser.roles.append(row_to_action_rule(row))
	if currentUser:
		if currentUser.id == ownerId:
			currentUser.roles.extend(get_playlist_owner_roles())
		yield currentUser

def generate_path_user_and_rules_from_rows(
	rows: Iterable[RowMapping],
	ownerId: Optional[int]=None,
	prefix: Optional[str]=None
) -> Iterator[AccountInfo]:
	currentUser = None
	normalizedPrefix = normalize_opening_slash(prefix)
	for row in rows:
		if not currentUser or currentUser.id != cast(int,row[u_pk]):
			if currentUser:
				if normalizedPrefix and currentUser.dirroot is not None \
						and normalizedPrefix.startswith(
							normalize_opening_slash(
								currentUser.dirroot
							)
						)\
					:
						currentUser.roles.extend(get_path_owner_roles(prefix))
				yield currentUser
			currentUser = row_to_user(row)
			if row["rule.domain"] != "shim":
				currentUser.roles.append(row_to_action_rule(row))
		elif row["rule.domain"] != "shim":
				currentUser.roles.append(row_to_action_rule(row))
	if currentUser:
		if normalizedPrefix and currentUser.dirroot \
				and normalizedPrefix.startswith(
					normalize_opening_slash(
						currentUser.dirroot)
					)\
			:
				currentUser.roles.extend(get_path_owner_roles(prefix))
		yield currentUser
		