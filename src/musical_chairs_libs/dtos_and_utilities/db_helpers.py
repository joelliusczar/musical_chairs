from typing import (
	Any,
	Callable,
	Collection,
	cast,
	Optional,
	Iterable,
	Iterator,
	TypeVar,
)
from sqlalchemy.sql.expression import Select
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
from sqlalchemy import Integer
from musical_chairs_libs.tables import (
	ur_userFk, ur_role, ur_quota, ur_span, ur_priority, ur_keypath, ur_sphere,
	u_username, u_pk, u_displayName, u_publictoken, u_dirRoot
)
from .user_role_def import (
	UserRoleDef,
	RulePriorityLevel,
)
from .action_rule_dtos import (
	ActionRule,
)
from .account_dtos import (
	RoledUser,
	RuledOwnedTokenEntity,
)
from .constants import UserRoleSphere
from .default_rule_providers import get_path_owner_roles
from .simple_functions import normalize_opening_slash, encode_id

RuledOwnedType = TypeVar("RuledOwnedType", bound=RuledOwnedTokenEntity)

def build_shim_select(
	ruleNameValue: str
) -> Select[Any]:

	query = select(
		dbLiteral(0).label("rule>userfk"),
		dbLiteral(ruleNameValue).label("rule>name"),
		cast(Column[float],dbLiteral(0)).label("rule>quota"),
		cast(Column[float],dbLiteral(0)).label("rule>span"),
		dbLiteral(0).label("rule>priority"),
		dbLiteral("shim").label("rule>sphere"),
		dbLiteral(None).label("rule>keypath")
	)

	return query

def build_base_rules_query(
	sphere: UserRoleSphere,
	userId: int | None=None
):
	user_rules_query = select(
		ur_userFk.label("rule>userfk"),
		ur_role.label("rule>name"),
		ur_quota.label("rule>quota"),
		ur_span.label("rule>span"),
		coalesce[Integer](
			ur_priority,
			case(
				(ur_role == UserRoleDef.ADMIN.value, RulePriorityLevel.SUPER.value),
				(
					ur_sphere == sphere.value, 
					RulePriorityLevel.INVITED_USER.value
				),
				else_=RulePriorityLevel.SITE.value
			)
		).label("rule>priority"),
		ur_sphere.label("rule>sphere"),
		ur_keypath.label("rule>keypath")
	).where(or_( #this part is only applies if there is a user id
			ur_role.like(f"{sphere.value}:%"),
			ur_role == UserRoleDef.ADMIN.value
		)
	)\
	.where(
		ur_sphere.in_([UserRoleSphere.Site.value, sphere.value])
	)


	placeholder_select = build_shim_select(
		UserRoleDef.combine(sphere, "view").value
	)

	if userId is not None:
		user_rules_query = user_rules_query.where(ur_userFk == userId)

	query = union_all(
		user_rules_query,
		placeholder_select
	)
	return query


def build_site_rules_query(
	userId: Optional[int]=None
) -> Select[Any]:

	user_rules_query = select(
		ur_userFk.label("rule>userfk"),
		ur_role.label("rule>name"),
		ur_quota.label("rule>quota"),
		ur_span.label("rule>span"),
		coalesce[Integer](
			ur_priority,
			case(
				(ur_role == UserRoleDef.ADMIN.value, RulePriorityLevel.SUPER.value),
				else_=RulePriorityLevel.SITE.value
			)
		).label("rule>priority"),
		ur_sphere.label("rule>sphere"),
	)\
	.where(ur_sphere == UserRoleSphere.Site.value)

	if userId is not None:
		user_rules_query = user_rules_query.where(ur_userFk == userId)

	return user_rules_query


def row_to_user(row: RowMapping) -> RoledUser:
	return RoledUser(
		id=row[u_pk],
		username=row[u_username],
		displayname=row[u_displayName],
		publictoken=row[u_publictoken],
		dirroot=row[u_dirRoot],
	)


def row_to_action_rule(row: RowMapping) -> ActionRule:

	return ActionRule(
		name=row["rule>name"],
		span=row["rule>span"],
		quota=row["rule>quota"],
		#if priortity is explict use that
		#otherwise, prefer station specific rule vs non station specific rule
		priority=cast(int,row["rule>priority"]) if row["rule>priority"] \
			else RulePriorityLevel.INVITED_USER.value,
		sphere=row["rule>sphere"]
	)


def generate_domain_user_and_rules_from_rows(
	rows: Iterable[RowMapping],
	ownerRuleProvider: Callable[[],Iterator[ActionRule]],
	ownerId: int | None=None,
) -> Iterator[RoledUser]:
	currentUser = None
	for row in rows:
		if not currentUser or currentUser.id != cast(int,row[u_pk]):
			if currentUser:
				if currentUser.id == ownerId:
					currentUser.roles.extend(ownerRuleProvider())
				yield currentUser
			currentUser = row_to_user(row)
			if row["rule>sphere"] != "shim":
				currentUser.roles.append(row_to_action_rule(row))
		elif row["rule>sphere"] != "shim":
			currentUser.roles.append(row_to_action_rule(row))
	if currentUser:
		if currentUser.id == ownerId:
			currentUser.roles.extend(ownerRuleProvider())
		yield currentUser


def generate_owned_and_rules_from_rows(
	rows: Iterable[RowMapping],
	transformer: Callable[[RowMapping], RuledOwnedType],
	ownerRuleProvider: Callable[[Collection[str] | None], Iterator[ActionRule]],
	scopes: Collection[str] | None = None,
	userId: int | None = None,
) -> Iterator[RuledOwnedType]:
	current = None
	for row in rows:
		if not current or current.id != encode_id(row["id"]):
			if current:
				owner = current.owner
				if owner and owner.id == userId:
					current.rules.extend(ownerRuleProvider(scopes))
				current.rules = ActionRule.sorted(current.rules)
				yield current
			current = transformer(row)
			if cast(str,row["rule>sphere"]) != "shim":
				current.rules.append(row_to_action_rule(row))
		elif cast(str,row["rule>sphere"]) != "shim":
			current.rules.append(row_to_action_rule(row))
	if current:
		owner = current.owner
		if owner and owner.id == userId:
			current.rules.extend(ownerRuleProvider(scopes))
		current.rules = ActionRule.sorted(current.rules)
		yield current


def generate_path_user_and_rules_from_rows(
	rows: Iterable[RowMapping],
	prefix: str | None=None
) -> Iterator[RoledUser]:
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
			if row["rule>sphere"] != "shim":
				currentUser.roles.append(row_to_action_rule(row))
		elif row["rule>sphere"] != "shim":
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
		