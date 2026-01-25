#pyright: reportMissingTypeStubs=false
from urllib import parse
from typing import Optional, Callable
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
from musical_chairs_libs.services import (
	AccountAccessService,
	AccountManagementService,
	AccountTokenCreator,
	CurrentUserProvider,
	ACCESS_TOKEN_EXPIRE_MINUTES
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountCreationInfo,
	AccountInfo,
	AuthenticatedAccount,
	UserRoleDef,
	TableData,
	AccountInfoBase,
	build_error_obj,
	PasswordInfo,
	ActionRule,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	UserActions,
	UserRoleDomain
)
from api_dependencies import (
	account_access_service,
	account_management_service,
	account_token_creator,
	current_user_provider,
	check_scope,
	check_subjectuser,
	get_user_from_token,
	get_from_path_subject_user,
	datetime_provider,
)
from api_logging import log_event
from datetime import datetime




router = APIRouter(prefix=f"/accounts")


@router.post("/open", dependencies=[
	Depends(
		log_event(
			UserRoleDomain.User.value,
			UserActions.LOGIN.value
		)
	)
])
def login(
	response: Response,
	formData: OAuth2PasswordRequestForm = Depends(),
	accountAccessService: AccountAccessService = Depends(account_access_service),
	accountTokenCreator: AccountTokenCreator = Depends(account_token_creator),
	getDatetime: Callable[[], datetime] = Depends(datetime_provider),
	currentUserProvider: CurrentUserProvider = Depends(
		current_user_provider
	)
) -> AuthenticatedAccount:
	user = accountAccessService.authenticate_user(
		formData.username,
		formData.password.encode()
	)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail=[build_error_obj("Incorrect username or password")],
			headers={"WWW-Authenticate": "Bearer"}
		)
	currentUserProvider.set_user(user)
	token = accountTokenCreator.create_access_token(user)
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
	loginTimestamp = getDatetime().timestamp()
	response.set_cookie(
		key="login_timestamp",
		value=str(loginTimestamp),
		max_age=tokenLifetime
	)
	return AuthenticatedAccount(
		id = user.id,
		access_token=token,
		token_type="bearer",
		username=user.username,
		roles=user.roles,
		lifetime=tokenLifetime,
		displayname=user.displayname,
		email=user.email,
		login_timestamp=loginTimestamp
	)


@router.post("/open_cookie")
def login_with_cookie(
	access_token: str  = Cookie(default=None),
	login_timestamp: float  = Cookie(default=0),
	accountAccessService: AccountAccessService = Depends(account_access_service)
) -> AuthenticatedAccount:
	uriDecodedToken = parse.unquote(access_token or "")
	try:
		user, expiration = get_user_from_token(uriDecodedToken, accountAccessService)
		return AuthenticatedAccount(
			id = user.id,
			access_token=access_token,
			token_type="bearer",
			username=user.username,
			roles=user.roles,
			lifetime=expiration,
			displayname=user.displayname,
			email=user.email,
			login_timestamp=login_timestamp
		)
	except:
		return AuthenticatedAccount(
			id=0,
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
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
) -> dict[str, bool]:
	return {
		"username": accountManagementService.is_username_used(username),
		"email": accountManagementService.is_email_used(email)
	}


@router.post("/new", dependencies=[
	# Depends(
	# 	log_event(
	# 		UserRoleDomain.User.value,
	# 		UserActions.ACCOUNT_CREATE.value
	# 	)
	# )
])
def create_new_account(
	accountInfo: AccountCreationInfo,
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
) -> AccountInfo:
	return accountManagementService.create_account(accountInfo)


@router.get("/list", dependencies=[
	Security(check_scope, scopes=[UserRoleDef.USER_LIST.value])
])
def get_user_list(
	searchTerm: Optional[str]=None,
	page: int = 0,
	pageSize: Optional[int] = None,
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
) -> TableData[AccountInfo]:
	accounts = list(accountManagementService.get_account_list(
		searchTerm=searchTerm,
		page=page,
		pageSize=pageSize
	))
	totalRows = accountManagementService.get_accounts_count()
	return TableData(totalrows=totalRows, items=accounts)


@router.get("/search", dependencies=[
	Security(
		check_scope,
		scopes=[UserRoleDef.USER_LIST.value]
	)
])
def search_users(
	searchTerm: Optional[str]=None,
	page: int = 0,
	pageSize: Optional[int] = None,
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
) -> list[AccountInfo]:
	accounts = list(accountManagementService.get_account_list(
		searchTerm=searchTerm,
		page=page,
		pageSize=pageSize
	))
	return accounts


@router.put(
	"/account/{subjectuserkey}",
	dependencies=[
		Security(
			check_subjectuser,
			scopes=[UserRoleDef.USER_EDIT.value]
		),
		Depends(
			log_event(UserRoleDomain.User.value, UserActions.ACCOUNT_UPDATE.value,)
		)
	]
)
def update_account(
	updatedInfo: AccountInfoBase,
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
) -> AccountInfo:
	return accountManagementService.update_account_general_changes(
		updatedInfo,
	)


@router.put(
	"/update-password/{subjectuserkey}",
	dependencies=[
		Security(
			check_subjectuser,
			scopes=[UserRoleDef.USER_EDIT.value]
		),
		Depends(
			log_event(UserRoleDomain.User.value, UserActions.CHANGE_PASS.value,)
		)
	]
)
def update_password(
	passwordInfo: PasswordInfo,
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
) -> bool:
	if accountManagementService.update_password(passwordInfo):
		return True
	raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Old password was incorrect.",
					"Password"
				)],
		)


@router.put(
	"/update-roles/{subjectuserkey}",
	dependencies=[
		Security(
			check_subjectuser,
			scopes=[UserRoleDef.USER_EDIT.value]
		)
	]
)
def update_roles(
	roles: list[ActionRule],
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	),
	prev: AccountInfo = Depends(get_from_path_subject_user)
) -> AccountInfo:
	addedRoles = list(accountManagementService.save_roles(prev.id, roles))
	return AccountInfo(**prev.model_dump(exclude=["roles"]), roles = addedRoles) #pyright: ignore [reportArgumentType, reportGeneralTypeIssues]


@router.get(
	"/account/{subjectuserkey}",
	dependencies=[
		Security(
			check_subjectuser,
			scopes=[UserRoleDef.USER_EDIT.value]
		)
	]
)
def get_account(
	accountInfo: AccountInfo = Depends(get_from_path_subject_user)
) -> AccountInfo:
	return accountInfo


@router.get("/site-roles/user_list",dependencies=[
	Security(
		check_subjectuser,
		scopes=[UserRoleDef.USER_USER_LIST.value]
	)
])
def get_path_user_list(
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
) -> TableData[AccountInfo]:
	pathUsers = list(accountManagementService.get_site_rule_users())
	return TableData(items=pathUsers, totalrows=len(pathUsers))


def validate_site_rule(
	rule: ActionRule,
	user: Optional[AccountInfo] = Depends(get_from_path_subject_user),
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
				f"{rule.name} is not a valid rule."
			)],
		)
	return rule


@router.post("/site-roles/user_role/{subjectuserkey}",
	dependencies=[
		Security(
			check_subjectuser,
			scopes=[UserRoleDef.USER_USER_ASSIGN.value]
		),
		Depends(
			log_event(UserRoleDomain.User.value, UserActions.ADD_SITE_RULE.value,)
		)
	]
)
def add_user_rule(
	subjectUser: AccountInfo = Depends(get_from_path_subject_user),
	rule: ActionRule = Depends(validate_site_rule),
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
) -> ActionRule:
	return accountManagementService.add_user_rule(subjectUser.id, rule)


@router.delete("/site-roles/user_role/{subjectuserkey}",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Security(
			check_subjectuser,
			scopes=[UserRoleDef.PATH_USER_ASSIGN.value]
		),
		Depends(
			log_event(UserRoleDomain.User.value, UserActions.REMOVE_SITE_RULE.value)
		)
	]
)
def remove_user_rule(
	rulename: str,
	subjectUser: AccountInfo = Depends(get_from_path_subject_user),
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
):
	if not subjectUser:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				"User is required"
			)],
		)
	accountManagementService.remove_user_site_rule(
		subjectUser.id,
		rulename,
	)