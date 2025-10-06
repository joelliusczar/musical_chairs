from typing import Optional, cast, Iterable, Iterator, Tuple, Union
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
	stup_userFk.label("rule_userfk"),
	stup_role.label("rule_name"),
	stup_count.label("rule_count"),
	stup_span.label("rule_span"),
	coalesce[Integer](
		stup_priority,
		RulePriorityLevel.STATION_PATH.value
	).label("rule_priority"),
	dbLiteral(UserRoleDomain.Station.value).label("rule_domain"),
	stup_stationFk.label("rule_stationfk")
)

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

def __build_placeholder_select__(
	domain:UserRoleDomain
) -> Select[Tuple[int, str, float, float, int, str]]:
	ruleNameCol = cast(Column[str], dbLiteral(UserRoleDef.STATION_VIEW.value) \
		if domain == UserRoleDomain.Station \
			else dbLiteral(UserRoleDef.PATH_VIEW.value))
	query = select(
		dbLiteral(0).label("rule_userfk"),
		ruleNameCol.label("rule_name"),
		cast(Column[float],dbLiteral(0)).label("rule_count"),
		cast(Column[float],dbLiteral(0)).label("rule_span"),
		dbLiteral(0).label("rule_priority"),
		dbLiteral("shim").label("rule_domain"),
	)

	return query

#int, String, int, int, int, str]]:

def build_rules_query(
	domain:UserRoleDomain,
	userId: Optional[int]=None
) -> Union[
		CompoundSelect[Tuple[int, str, float, float, int, str]],
		CompoundSelect[
			Tuple[
				Integer, String, Float[float], Float[float], Integer, str, Integer]
		]
	]:

	user_rules_base_query = select(
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
	).where(ur_userFk == userId)


	placeholder_select = __build_placeholder_select__(domain)
	domain_permissions_query =  placeholder_select.where(false())
	path_permissions_query = placeholder_select.where(false())
	user_rules_query = user_rules_base_query \
		if userId else placeholder_select.where(false())

	if domain == UserRoleDomain.Station:
		placeholder_select = placeholder_select.add_columns(
			dbLiteral(None).label("rule_stationfk")
		)
		user_rules_query = user_rules_query.add_columns(
			dbLiteral(-1).label("rule_stationfk")
		).where(or_(
				ur_role.like(f"{domain.value}:%"),
				ur_role == UserRoleDef.ADMIN.value
			),
		)
		domain_permissions_query = __station_permissions_query__
		path_permissions_query = path_permissions_query.add_columns(
			dbLiteral(None).label("rule_stationfk")
		)
	elif domain == UserRoleDomain.Site:
		#don't want the shim if only selecting on userRoles
		placeholder_select = placeholder_select.where(false())
	elif domain == UserRoleDomain.Path:
		placeholder_select = placeholder_select.add_columns(
			dbLiteral(None).label("rule_path")
		)
		user_rules_query = user_rules_query.add_columns(
			dbLiteral(None).label("rule_path")
		).where(or_( #this part is only applies if there is a user id
				ur_role.like(f"{domain.value}:%"),
				ur_role == UserRoleDef.ADMIN.value
			),
		)
		path_permissions_query = __path_permissions_query__
		domain_permissions_query = domain_permissions_query.add_columns(
			dbLiteral(None).label("rule_path")
		)

	if userId is not None:
		domain_permissions_query = \
			domain_permissions_query.where(stup_userFk == userId)
		path_permissions_query =\
			path_permissions_query.where(pup_userFk == userId)

	query = union_all(
		domain_permissions_query,
		path_permissions_query,
		user_rules_query,
		placeholder_select
	)
	return query

def row_to_user(row: RowMapping) -> AccountInfo:
	return AccountInfo(
		id=row[u_pk],
		username=row[u_username],
		displayname=row[u_displayName],
		email=row[u_email],
		dirroot=row[u_dirRoot],
	)

def row_to_action_rule(row: RowMapping) -> ActionRule:
	clsConstructor = action_rule_class_map.get(
		row["rule_domain"],
		ActionRule
	)

	return clsConstructor(
		name=row["rule_name"],
		span=row["rule_span"],
		count=row["rule_count"],
		#if priortity is explict use that
		#otherwise, prefer station specific rule vs non station specific rule
		priority=cast(int,row["rule_priority"]) if row["rule_priority"] \
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
			if row["rule_domain"] != "shim":
				currentUser.roles.append(row_to_action_rule(row))
		elif row["rule_domain"] != "shim":
			currentUser.roles.append(row_to_action_rule(row))
	if currentUser:
		if currentUser.id == ownerId and domain == UserRoleDomain.Station:
			currentUser.roles.extend(get_station_owner_rules())
		elif domain == UserRoleDomain.Path:
			if normalizedPrefix and currentUser.dirroot \
				and normalizedPrefix.startswith(
					normalize_opening_slash(
						currentUser.dirroot)
					)\
			:
				currentUser.roles.extend(get_path_owner_roles(prefix))
		yield currentUser