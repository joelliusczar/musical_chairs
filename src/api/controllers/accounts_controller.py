#pyright: reportMissingTypeStubs=false
from fastapi import APIRouter, Depends, HTTPException, status
from musical_chairs_libs.accounts_service import AccountsService
from musical_chairs_libs.dtos import SaveAccountInfo
from api_dependencies import accounts_service
from musical_chairs_libs.errors import AlreadyUsedError
from email_validator import EmailNotValidError #pyright: ignore reportUnknownVariableType



router = APIRouter(prefix=f"/accounts")


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
			detail = str(ex)
		)
