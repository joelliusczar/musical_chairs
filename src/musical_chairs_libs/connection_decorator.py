from inspect import signature
from musical_chairs_libs.config_loader import get_configured_db_connection

def _use_connection_or_default(conn, echo = False):
	if conn:
		return conn
	return get_configured_db_connection(echo)

def provide_db_conn(echo = False):
	def inner(func):
		def wrap(*args, **kwargs):
			conn = args[1]
			ownedConn = _use_connection_or_default(conn)
			nargs = (args[0], ownedConn, *args[1:])
			return func(*nargs, **kwargs)
		return wrap
	return inner
