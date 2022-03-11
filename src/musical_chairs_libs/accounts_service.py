from musical_chairs_libs.dtos import AccountInfo
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import users

class AccountService:

	def __init__(self, conn: Connection) -> None:
		self.conn = conn

	def create_account(accountInfo: AccountInfo):
		pass