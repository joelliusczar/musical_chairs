#pyright: reportMissingTypeStubs=false
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Security, Body
from fastapi.security import OAuth2PasswordRequestForm
from musical_chairs_libs.accounts_service import AccountsService,\
	ACCESS_TOKEN_EXPIRE_MINUTES
from musical_chairs_libs.dtos import\
	AccountCreationInfo,\
	AccountInfo,\
	AuthenticatedAccount,\
	UserRoleDef,\
	TableData
from api_dependencies import accounts_service, get_current_user, get_account_if_can_edit
from musical_chairs_libs.errors import AlreadyUsedError
from musical_chairs_libs.simple_functions import build_error_obj
from email_validator import EmailNotValidError #pyright: ignore reportUnknownVariableType



router = APIRouter(prefix=f"/accounts")


@router.post("/open")
def login(
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
	return AuthenticatedAccount(
		access_token=token,
		token_type="bearer",
		username=user.username,
		roles=user.roles,
		lifetime=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
		displayName=user.displayName,
		email=user.email
	)

@router.get("/check")
def is_phrase_used(
	username: str = "",
	email: str = "",
	accountsService: AccountsService = Depends(accounts_service)
) -> dict[str, bool]:
	return {
		"username": accountsService.is_username_used(username),
		"email": accountsService.is_email_used(email)
	}

@router.post("/new")
def create_new_account(
	accountInfo: AccountCreationInfo,
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	try:
		return accountsService.create_account(accountInfo)
	except (AlreadyUsedError, EmailNotValidError) as ex:
		raise HTTPException(
			status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail = ex.args[0]
		)

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

@router.put("/update-email/{userId}")
def update_email(
	email: str = Body(default="", embed=True),
	prev: AccountInfo = Depends(get_account_if_can_edit),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	try:
		return accountsService.update_email(email, prev)
	except (AlreadyUsedError, EmailNotValidError) as ex:
		raise HTTPException(
			status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail = ex.args[0]
		)

@router.put("/update-roles/{userId}")
def update_roles(
	roles: list[str],
	prev: AccountInfo = Depends(get_account_if_can_edit),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	addedRoles = accountsService.save_roles(prev.id, roles)
	prev.roles = list(addedRoles)
	return prev

@router.get("/{userId}")
def get_account(
	accountInfo: AccountInfo = Depends(get_account_if_can_edit)
) -> AccountInfo:
	return accountInfo