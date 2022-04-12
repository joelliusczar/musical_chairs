from fastapi import APIRouter
from constants import api_version
from musical_chairs_libs.dtos import AccountInfo

router = APIRouter(prefix=f"/api/{api_version}/accounts")


@router.post("/create")
def create_account(accountInfo: AccountInfo):
	pass
