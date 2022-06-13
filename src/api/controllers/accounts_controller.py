#pyright: reportMissingTypeStubs=false
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Security, Body
from fastapi.security import OAuth2PasswordRequestForm
from musical_chairs_libs.accounts_service import AccountsService,\
	ACCESS_TOKEN_EXPIRE_MINUTES
from musical_chairs_libs.dtos import\
	AccountInfo,\
	SaveAccountInfo,\
	AuthenticatedAccount,\
	UserRoleDef
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
	if not user or not user.isAuthenticated:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail=[build_error_obj("Incorrect username or password")],
			headers={"WWW-Authenticate": "Bearer"}
		)
	token = accountService.create_access_token(user.userName)
	return AuthenticatedAccount(
		token,
		"bearer",
		user.userName,
		user.roles,
		ACCESS_TOKEN_EXPIRE_MINUTES * 60,
		user.displayName
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
	accountInfo: SaveAccountInfo,
	accountsService: AccountsService = Depends(accounts_service)
) -> SaveAccountInfo:
	try:
		return accountsService.create_account(accountInfo)
	except (AlreadyUsedError, EmailNotValidError) as ex:
		raise HTTPException(
			status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail = ex.args[0]
		)

@router.get("/list")
def get_user_list(
	page: int = 0,
	pageSize: Optional[int] = None,
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.USER_LIST.value]
	),
	accountsService: AccountsService = Depends(accounts_service)
) -> List[SaveAccountInfo]:
	return list(accountsService.get_account_list(page, pageSize))

@router.put("/update-email/{userId}")
def update_email(
	email: Any = Body(default="", embed=True),
	prev: SaveAccountInfo = Depends(get_account_if_can_edit),
	accountsService: AccountsService = Depends(accounts_service)
) -> SaveAccountInfo:
	try:
		return accountsService.update_email(email, prev)
	except (AlreadyUsedError, EmailNotValidError) as ex:
		raise HTTPException(
			status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail = ex.args[0]
		)