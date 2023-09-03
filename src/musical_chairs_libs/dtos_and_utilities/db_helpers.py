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
from sqlalchemy import Integer, String
from musical_chairs_libs.tables import (
	stup_role, stup_stationFk, stup_userFk, stup_count, stup_span, stup_priority,
	ur_userFk, ur_role, ur_count, ur_span, ur_priority,
	u_username, u_pk, u_displayName, u_email, u_dirRoot,
	pup_role, pup_userFk, pup_count, pup_span, pup_priority, pup_path
)
from .user_role_def import (
	UserRoleDef,
	UserRoleDomain,
	RulePriorityLevel,
)
from .action_rule_dtos import (
	ActionRule,
	action_rule_class_map,
)
from .account_dtos import (
	AccountInfo,
	get_station_owner_rules,
	get_path_owner_roles
)
from .simple_functions import normalize_opening_slash

__station_permissions_query__ = select(
	stup_userFk.label("rule_userFk"),
	stup_role.label("rule_name"),
	stup_count.label("rule_count"),
	stup_span.label("rule_span"),
	coalesce[Integer](
		stup_priority,
		RulePriorityLevel.STATION_PATH.value
	).label("rule_priority"),
	dbLiteral(UserRoleDomain.Station.value).label("rule_domain"),
	stup_stationFk.label("rule_stationFk")
)

__path_permissions_query__ = select(
	pup_userFk.label("rule_userFk"),
	pup_role.label("rule_name"),
	pup_count.label("rule_count"),
	pup_span.label("rule_span"),
	coalesce[Integer](
		pup_priority,
		RulePriorityLevel.STATION_PATH.value
	).label("rule_priority"),
	dbLiteral(UserRoleDomain.Path.value).label("rule_domain"), #pyright: ignore [reportUnknownMemberType]
	pup_path.label("rule_path") #pyright: ignore [reportUnknownMemberType]
)

def __build_placeholder_select__(
	domain:UserRoleDomain
) -> Select[Tuple[int, String, float, float, int, str]]:
	ruleNameCol = cast(Column[String], dbLiteral(UserRoleDef.STATION_VIEW.value) \
		if domain == UserRoleDomain.Station \
			else dbLiteral(UserRoleDef.PATH_VIEW.value))
	query = select(
		dbLiteral(0).label("rule_userFk"), #pyright: ignore [reportUnknownMemberType]
		ruleNameCol.label("rule_name"), #pyright: ignore [reportUnknownMemberType]
		cast(Column[float],dbLiteral(0)).label("rule_count"), #pyright: ignore [reportUnknownMemberType]
		cast(Column[float],dbLiteral(0)).label("rule_span"), #pyright: ignore [reportUnknownMemberType]
		dbLiteral(0).label("rule_priority"), #pyright: ignore [reportUnknownMemberType]
		dbLiteral("shim").label("rule_domain"), #pyright: ignore [reportUnknownMemberType]
	)

	return query

#int, String, int, int, int, str]]:

def build_rules_query(
	domain:UserRoleDomain,
	userId: Optional[int]=None
) -> CompoundSelect:

	user_rules_base_query = select(
		ur_userFk.label("rule_userFk"),
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
		dbLiteral(UserRoleDomain.Site.value).label("rule_domain"), #pyright: ignore [reportUnknownMemberType]
	).where(ur_userFk == userId)


	placeholder_select = __build_placeholder_select__(domain)
	domain_permissions_query =  placeholder_select.where(false()) #pyright: ignore [reportUnknownMemberType]
	path_permissions_query = placeholder_select.where(false()) #pyright: ignore [reportUnknownMemberType]
	user_rules_query = user_rules_base_query \
		if userId else placeholder_select.where(false()) #pyright: ignore [reportUnknownMemberType]

	if domain == UserRoleDomain.Station:
		placeholder_select = placeholder_select.add_columns( #pyright: ignore [reportUnknownMemberType]
			dbLiteral(None).label("rule_stationFk") #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
		)
		user_rules_query = user_rules_query.add_columns( #pyright: ignore [reportUnknownMemberType]
			dbLiteral(-1).label("rule_stationFk") #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
		).where(or_(
				ur_role.like(f"{domain.value}:%"),
				ur_role == UserRoleDef.ADMIN.value
			),
		)
		domain_permissions_query = __station_permissions_query__
		path_permissions_query = path_permissions_query.add_columns( #pyright: ignore [reportUnknownMemberType]
			dbLiteral(None).label("rule_stationFk") #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
		)
	elif domain == UserRoleDomain.Site:
		#don't want the shim if only selecting on userRoles
		placeholder_select = placeholder_select.where(false()) #pyright: ignore [reportUnknownMemberType]
	elif domain == UserRoleDomain.Path:
		placeholder_select = placeholder_select.add_columns( #pyright: ignore [reportUnknownMemberType]
			dbLiteral(None).label("rule_path") #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
		)
		user_rules_query = user_rules_query.add_columns( #pyright: ignore [reportUnknownMemberType]
			dbLiteral(None).label("rule_path") #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
		).where(or_(
				ur_role.like(f"{domain.value}:%"),
				ur_role == UserRoleDef.ADMIN.value
			),
		)
		path_permissions_query = __path_permissions_query__
		domain_permissions_query = domain_permissions_query.add_columns( #pyright: ignore [reportUnknownMemberType]
			dbLiteral(None).label("rule_path") #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
		)

	if userId is not None:
		domain_permissions_query = \
			domain_permissions_query.where(stup_userFk == userId) #pyright: ignore [reportUnknownMemberType]
		path_permissions_query =\
			path_permissions_query.where(pup_userFk == userId) #pyright: ignore [reportUnknownMemberType]

	query = union_all(
		domain_permissions_query,
		path_permissions_query,
		user_rules_query,
		placeholder_select
	)
	return query

def row_to_user(row: RowMapping) -> AccountInfo:
	return AccountInfo(
		id=cast(int,row[u_pk]),
		username=cast(str,row[u_username]),
		displayName=cast(str,row[u_displayName]),
		email=cast(str,row[u_email]),
		dirRoot=cast(str,row[u_dirRoot]),
	)

def row_to_action_rule(row: RowMapping) -> ActionRule:
	clsConstructor = action_rule_class_map.get(
		cast(str, row["rule_domain"]),
		ActionRule
	)

	return clsConstructor(
		cast(str,row["rule_name"]),
		cast(int,row["rule_span"]),
		cast(int,row["rule_count"]),
		#if priortity is explict use that
		#otherwise, prefer station specific rule vs non station specific rule
		cast(int,row["rule_priority"]) if row["rule_priority"] \
			else RulePriorityLevel.STATION_PATH.value
	)

def generate_user_and_rules_from_rows(
	rows: Iterable[RowMapping],
	domain: UserRoleDomain,
	ownerId: Optional[int]=None,
	prefix: Optional[str]=None
) -> Iterator[AccountInfo]:
	currentUser = None
	normalizedPrefix = normalize_opening_slash(prefix)
	for row in rows:
		if not currentUser or currentUser.id != cast(int,row[u_pk]):
			if currentUser:
				if currentUser.id == ownerId and domain == UserRoleDomain.Station:
					currentUser.roles.extend(get_station_owner_rules())
				elif domain == UserRoleDomain.Path:
					if normalizedPrefix and currentUser.dirRoot is not None \
						and normalizedPrefix.startswith(
							normalize_opening_slash(
								currentUser.dirRoot
							)
						)\
					:
						currentUser.roles.extend(get_path_owner_roles(prefix))
				yield currentUser
			currentUser = row_to_user(row)
			if cast(str,row["rule_domain"]) != "shim":
				currentUser.roles.append(row_to_action_rule(row))
		elif cast(str,row["rule_domain"]) != "shim":
			currentUser.roles.append(row_to_action_rule(row))
	if currentUser:
		if currentUser.id == ownerId and domain == UserRoleDomain.Station:
			currentUser.roles.extend(get_station_owner_rules())
		elif domain == UserRoleDomain.Path:
			if normalizedPrefix and currentUser.dirRoot \
				and normalizedPrefix.startswith(
					normalize_opening_slash(
						currentUser.dirRoot)
					)\
			:
				currentUser.roles.extend(get_path_owner_roles(prefix))
		yield currentUser