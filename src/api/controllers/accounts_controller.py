#pyright: reportMissingTypeStubs=false
from urllib import parse
from typing import Optional
from dataclasses import asdict
from fastapi import (
	APIRouter,
	Depends,
	HTTPException,
	status,
	Security,
	Response,
	Cookie
)
from fastapi.security import OAuth2PasswordRequestForm
from musical_chairs_libs.services import AccountsService,\
	ACCESS_TOKEN_EXPIRE_MINUTES
from musical_chairs_libs.dtos_and_utilities import (
	AccountCreationInfo,
	AccountInfo,
	AuthenticatedAccount,
	UserRoleDef,
	TableData,
	AccountInfoBase,
	build_error_obj,
	PasswordInfo,
	ActionRule
)
from api_dependencies import (
	accounts_service,
	get_user_with_simple_scopes,
	get_account_if_has_scope,
	get_user_from_token,
	get_optional_user_from_token,
	get_subject_user
)




router = APIRouter(prefix=f"/accounts")


@router.post("/open")
def login(
	response: Response,
	formData: OAuth2PasswordRequestForm=Depends(),
	accountService: AccountsService=Depends(accounts_service)
) -> AuthenticatedAccount:
	user = accountService.authenticate_user(
		formData.username,
		formData.password.encode()
	)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail=[build_error_obj("Incorrect username or password")],
			headers={"WWW-Authenticate": "Bearer"}
		)
	token = accountService.create_access_token(user.username)
	tokenLifetime = ACCESS_TOKEN_EXPIRE_MINUTES * 60
	response.set_cookie(
		key="access_token",
		value=parse.quote(token),
		max_age=tokenLifetime,
		secure=True
	)
	response.set_cookie(
		key="username",
		value=parse.quote(user.username),
		max_age=tokenLifetime
	)
	response.set_cookie(
		key="displayname",
		value=parse.quote(user.displayname or user.username),
		max_age=tokenLifetime
	)
	return AuthenticatedAccount(
		access_token=token,
		token_type="bearer",
		username=user.username,
		roles=user.roles,
		lifetime=tokenLifetime,
		displayname=user.displayname,
		email=user.email
	)

@router.post("/open_cookie")
def login_with_cookie(
	access_token: str  = Cookie(default=None),
	accountsService: AccountsService = Depends(accounts_service)
) -> AuthenticatedAccount:
	uriDecodedToken = parse.unquote(access_token or "")
	try:
		user, expiration = get_user_from_token(uriDecodedToken, accountsService)
		return AuthenticatedAccount(
			access_token=access_token,
			token_type="bearer",
			username=user.username,
			roles=user.roles,
			lifetime=expiration,
			displayname=user.displayname,
			email=user.email
		)
	except:
		return AuthenticatedAccount(
			access_token="",
			token_type="bearer",
			username="",
			roles=[],
			lifetime=0,
			displayname="",
			email=""
		)

@router.get("/check")
def is_phrase_used(
	username: str = "",
	email: str = "",
	loggedInUser: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	accountsService: AccountsService = Depends(accounts_service)
) -> dict[str, bool]:
	return {
		"username": accountsService.is_username_used(username),
		"email": accountsService.is_email_used(email, loggedInUser)
	}

@router.post("/new")
def create_new_account(
	accountInfo: AccountCreationInfo,
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	return accountsService.create_account(accountInfo)

@router.get("/list", dependencies=[
	Security(get_user_with_simple_scopes, scopes=[UserRoleDef.USER_LIST.value])
])
def get_user_list(
	searchTerm: Optional[str]=None,
	page: int = 0,
	pageSize: Optional[int] = None,
	accountsService: AccountsService = Depends(accounts_service)
) -> TableData[AccountInfo]:
	accounts = list(accountsService.get_account_list(
		searchTerm=searchTerm,
		page=page,
		pageSize=pageSize
	))
	totalRows = accountsService.get_accounts_count()
	return TableData(totalrows=totalRows, items=accounts)

@router.get("/search", dependencies=[
	# Security(get_user_with_simple_scopes, scopes=[UserRoleDef.USER_LIST.value])
])
def search_users(
	searchTerm: Optional[str]=None,
	page: int = 0,
	pageSize: Optional[int] = None,
	accountsService: AccountsService = Depends(accounts_service)
) -> list[AccountInfo]:
	accounts = list(accountsService.get_account_list(
		searchTerm=searchTerm,
		page=page,
		pageSize=pageSize
	))
	return accounts

@router.put("/account/{subjectuserkey}")
def update_account(
	updatedInfo: AccountInfoBase,
	prev: AccountInfo = Security(
		get_account_if_has_scope,
		scopes=[UserRoleDef.USER_EDIT.value]
	),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	return accountsService.update_account_general_changes(updatedInfo, prev)


@router.put("/update-password/{subjectuserkey}")
def update_password(
	passwordInfo: PasswordInfo,
	currentUser: AccountInfo = Security(
		get_account_if_has_scope,
		scopes=[UserRoleDef.USER_EDIT.value]
	),
	accountsService: AccountsService = Depends(accounts_service)
) -> bool:
	if accountsService.update_password(passwordInfo, currentUser):
		return True
	raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Old password was incorrect.",
					"Password"
				)],
		)

@router.put("/update-roles/{subjectuserkey}")
def update_roles(
	roles: list[ActionRule],
	prev: AccountInfo = Security(
		get_account_if_has_scope,
		scopes=[UserRoleDef.USER_EDIT.value]
	),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	addedRoles = list(accountsService.save_roles(prev.id, roles))
	return AccountInfo(**{**asdict(prev), "roles": addedRoles}) #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]

@router.get("/account/{subjectuserkey}")
def get_account(
	accountInfo: AccountInfo = Security(
		get_account_if_has_scope,
		scopes=[UserRoleDef.USER_EDIT.value]
	)
) -> AccountInfo:
	return accountInfo

@router.get("/site-roles/user_list",dependencies=[
	Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.SITE_USER_LIST.value]
	)
])
def get_path_user_list(
	accountsService: AccountsService = Depends(accounts_service)
) -> TableData[AccountInfo]:
	pathUsers = list(accountsService.get_site_rule_users())
	return TableData(pathUsers, len(pathUsers))


def validate_site_rule(
	rule: ActionRule,
	user: Optional[AccountInfo] = Depends(get_subject_user),
) -> ActionRule:
	if not user:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				"User is required"
			)],
		)
	valid_name_set = UserRoleDef.as_set()
	if rule.name not in valid_name_set:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				f"{rule.name} is not a valid rule for stations"
			)],
		)
	return rule

@router.post("/site-roles/user_role/{subjectuserkey}",
	dependencies=[
		Security(
			get_user_with_simple_scopes,
			scopes=[UserRoleDef.SITE_USER_ASSIGN.value]
		)
	]
)
def add_user_rule(
	user: AccountInfo = Depends(get_subject_user),
	rule: ActionRule = Depends(validate_site_rule),
	accountsService: AccountsService = Depends(accounts_service),
) -> ActionRule:
	return accountsService.add_user_rule(user.id, rule)


@router.delete("/site-roles/user_role/{subjectuserkey}",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Security(
			get_user_with_simple_scopes,
			scopes=[UserRoleDef.PATH_USER_ASSIGN.value]
		)
	]
)
def remove_user_rule(
	ruleName: str,
	user: AccountInfo = Depends(get_subject_user),
	accountsService: AccountsService = Depends(accounts_service),
):
	if not user:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				"User is required"
			)],
		)
	accountsService.remove_user_site_rule(
		user.id,
		ruleName
	)