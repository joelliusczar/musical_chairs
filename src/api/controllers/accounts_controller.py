#pyright: reportMissingTypeStubs=false
from fastapi import APIRouter, Depends, HTTPException, status
from musical_chairs_libs.accounts_service import AccountsService
from musical_chairs_libs.dtos import SaveAccountInfo
from api_dependencies import accounts_service



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
) -> int:
	if(accountsService.is_username_used(accountInfo.username)):
		raise HTTPException(
			status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail = f"Username {accountInfo.username} is already used."
		)
	if(accountsService.is_email_used(accountInfo.email)):
		raise HTTPException(
			status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail = f"Email {accountInfo.email} is already used."
		)
	return accountsService.create_account(accountInfo)
