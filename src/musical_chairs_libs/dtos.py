from pydantic import BaseModel

class AccountInfo(BaseModel):
	username: str
	password: bytearray
	email: str