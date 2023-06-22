from typing import Optional, Union, Literal, cast, Iterable, Iterator
from sqlalchemy.sql.expression import Select, false
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.schema import Column
from sqlalchemy.engine.row import Row
from sqlalchemy import (
	select,
	union_all,
	literal as dbLiteral  #pyright: ignore [reportUnknownVariableType]
)
from musical_chairs_libs.tables import (
	stup_role, stup_stationFk, stup_userFk, stup_count, stup_span, stup_priority,
	ur_userFk, ur_role, ur_count, ur_span, ur_priority,
	u_username, u_pk, u_displayName, u_email, u_dirRoot,
)
from .user_role_def import (
	UserRoleDef,
	UserRoleDomain,
	RulePriorityLevel,
)
from .action_rule_dtos import ActionRule
from .account_dtos import AccountInfo, get_station_owner_rules

__station_permissions_query__ = select(
	stup_userFk.label("rule_userFk"), #pyright: ignore [reportUnknownMemberType]
	stup_role.label("rule_name"), #pyright: ignore [reportUnknownMemberType]
	stup_count.label("rule_count"), #pyright: ignore [reportUnknownMemberType]
	stup_span.label("rule_span"), #pyright: ignore [reportUnknownMemberType]
	coalesce(
		stup_priority, #pyright: ignore [reportUnknownMemberType]
		RulePriorityLevel.STATION_PATH.value
	).label("rule_priority"),
	dbLiteral(UserRoleDomain.Station.value).label("rule_domain"), #pyright: ignore [reportUnknownMemberType]
	stup_stationFk.label("rule_stationFk") #pyright: ignore [reportUnknownMemberType]
)

def __build_placeholder_select__(domain:Union[
		Literal[UserRoleDomain.Station],
		Literal[UserRoleDomain.Path]
	]) -> Select:
	ruleNameCol = cast(Column, dbLiteral(UserRoleDef.STATION_VIEW.value) \
		if domain == UserRoleDomain.Station \
			else dbLiteral(UserRoleDef.PATH_VIEW.value))
	query = select(
		dbLiteral(0).label("rule_userFk"), #pyright: ignore [reportUnknownMemberType]
		ruleNameCol.label("rule_name"), #pyright: ignore [reportUnknownMemberType]
		dbLiteral(0).label("rule_count"), #pyright: ignore [reportUnknownMemberType]
		dbLiteral(0).label("rule_span"), #pyright: ignore [reportUnknownMemberType]
		dbLiteral(0).label("rule_priority"), #pyright: ignore [reportUnknownMemberType]
		dbLiteral("shim").label("rule_domain"), #pyright: ignore [reportUnknownMemberType]
	)

	return query

def build_rules_query(
	domain:Union[
		Literal[UserRoleDomain.Station],
		Literal[UserRoleDomain.Path]
	],
	userId: Optional[int]=None
) -> Select:

	user_rules_base_query = select(
		ur_userFk.label("rule_userFk"), #pyright: ignore [reportUnknownMemberType]
		ur_role.label("rule_name"), #pyright: ignore [reportUnknownMemberType]
		ur_count.label("rule_count"), #pyright: ignore [reportUnknownMemberType]
		ur_span.label("rule_span"), #pyright: ignore [reportUnknownMemberType]
		coalesce(
			ur_priority, #pyright: ignore [reportUnknownMemberType]
			RulePriorityLevel.SITE.value
		).label("rule_priority"),
		dbLiteral(UserRoleDomain.Site.value).label("rule_domain"), #pyright: ignore [reportUnknownMemberType]
	).where(ur_userFk == userId)\
		.where(ur_role.like(f"{domain.value}:%"))

	placeholder_select = __build_placeholder_select__(domain)
	domain_permissions_query =  placeholder_select.where(false()) #pyright: ignore [reportUnknownMemberType]
	user_rules_query = user_rules_base_query \
		if userId else placeholder_select.where(false()) #pyright: ignore [reportUnknownMemberType]

	if domain == UserRoleDomain.Station:
		placeholder_select = placeholder_select.add_columns( #pyright: ignore [reportUnknownMemberType]
			dbLiteral(None).label("rule_stationFk") #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
		)
		user_rules_query = user_rules_query.add_columns( #pyright: ignore [reportUnknownMemberType]
			dbLiteral(-1).label("rule_stationFk") #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
		)
		domain_permissions_query = __station_permissions_query__

	if userId is not None:
		domain_permissions_query = \
			domain_permissions_query.where(stup_userFk == userId) #pyright: ignore [reportUnknownMemberType]


	query = union_all(
		domain_permissions_query,
		user_rules_query,
		placeholder_select
	)
	return query

def row_to_user(row: Row) -> AccountInfo:
	return AccountInfo(
		id=cast(int,row[u_pk]),
		username=cast(str,row[u_username]),
		displayName=cast(str,row[u_displayName]),
		email=cast(str,row[u_email]),
		dirRoot=cast(str,row[u_dirRoot]),
	)

def row_to_action_rule(row: Row) -> ActionRule:
	return ActionRule(
		cast(str,row["rule_name"]),
		cast(int,row["rule_span"]),
		cast(int,row["rule_count"]),
		#if priortity is explict use that
		#otherwise, prefer station specific rule vs non station specific rule
		cast(int,row["rule_priority"]) if row["rule_priority"] \
			else RulePriorityLevel.STATION_PATH.value,
		domain=cast(str, row["rule_domain"])
	)

def generate_user_and_rules_from_rows(
	rows: Iterable[Row],
	domain: UserRoleDomain,
	ownerId: Optional[int]=None
) -> Iterator[AccountInfo]:
	currentUser = None
	for row in rows:
		if not currentUser or currentUser.id != cast(int,row["rule_userFk"]):
			if currentUser:
				if currentUser.id == ownerId and domain == UserRoleDomain.Station:
					currentUser.roles.extend(get_station_owner_rules())
				yield currentUser
			currentUser = row_to_user(row)
			if cast(str,row["rule_domain"]) != "shim":
				currentUser.roles.append(row_to_action_rule(row))
		elif cast(str,row["rule_domain"]) != "shim":
			currentUser.roles.append(row_to_action_rule(row))
	if currentUser:
		if currentUser.id == ownerId and domain == UserRoleDomain.Station:
			currentUser.roles.extend(get_station_owner_rules())
		yield currentUser