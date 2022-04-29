from typing import Any, List, Optional
from sqlalchemy.engine import Connection, Transaction, Engine
from sqlalchemy.engine.cursor import CursorResult


"""
WrappedDbConnection is just a wrapper around the SqlAlchemy connection
to shut up the pylance from complaining. I think the type annotations 
for it are incomplete
"""
class WrappedDbConnection:

	def __init__(self, conn: Connection) -> None:
			self.conn = conn

	@property
	def engine(self) -> Engine:
		return self.conn.engine

	def execute(self, 
		statement: Any,
		params: Optional[List[Any]]=None
	) -> CursorResult:
		if params:
			return self.conn.execute(statement, params) # type: ignore
		else:
			#apparently can't pass in None for params?
			return self.conn.execute(statement) # type: ignore

	def begin(self) -> Transaction:
		return self.conn.begin()

	def close(self) -> None:
		self.conn.close()

	