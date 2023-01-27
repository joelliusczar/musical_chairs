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
	PasswordInfo
)
from api_dependencies import (
	accounts_service,
	get_current_user,
	get_account_if_can_edit,
	get_user_from_token,
	get_user_from_token_optional
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
		key="displayName",
		value=parse.quote(user.displayName or user.username),
		max_age=tokenLifetime
	)
	return AuthenticatedAccount(
		access_token=token,
		token_type="bearer",
		username=user.username,
		roles=user.roles,
		lifetime=tokenLifetime,
		displayName=user.displayName,
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
			displayName=user.displayName,
			email=user.email
		)
	except:
		return AuthenticatedAccount(
			access_token="",
			token_type="bearer",
			username="",
			roles=[],
			lifetime=0,
			displayName="",
			email=""
		)

@router.get("/check")
def is_phrase_used(
	username: str = "",
	email: str = "",
	loggedInUser: Optional[AccountInfo] = Depends(get_user_from_token_optional),
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
	Security(get_current_user, scopes=[UserRoleDef.USER_LIST.value])
])
def get_user_list(
	page: int = 0,
	pageSize: Optional[int] = None,
	accountsService: AccountsService = Depends(accounts_service)
) -> TableData[AccountInfo]:
	accounts = list(accountsService.get_account_list(page, pageSize))
	totalRows = accountsService.get_accounts_count()
	return TableData(totalRows=totalRows, items=accounts)

@router.put("")
def update_account(
	updatedInfo: AccountInfoBase,
	prev: AccountInfo = Depends(get_account_if_can_edit),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	return accountsService.update_account_general_changes(updatedInfo, prev)


@router.put("/update-password/")
def update_password(
	passwordInfo: PasswordInfo,
	currentUser: AccountInfo = Depends(get_account_if_can_edit),
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


@router.put("/update-roles/{userId}")
def update_roles(
	roles: list[str],
	prev: AccountInfo = Depends(get_account_if_can_edit),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	addedRoles = list(accountsService.save_roles(prev.id, roles))
	return AccountInfo(**{**asdict(prev), "roles": addedRoles}) #pyright: ignore [reportUnknownArgumentType, reportGeneralTypeIssues]

@router.get("")
def get_account(
	accountInfo: AccountInfo = Depends(get_account_if_can_edit)
) -> AccountInfo:
	return accountInfo