from inspect import signature
from musical_chairs_libs.config_loader import get_configured_db_connection

def _use_connection_or_default(conn, echo = False):
	if conn:
		return conn
	return get_configured_db_connection(echo)

def provide_db_conn(echo = False):
	def inner(func):
		def wrap(*args, **kwargs):
			conn = None
			ownedConn = None
			nargs = args
			if "conn" in kwargs:
				conn = kwargs["conn"]
				ownedConn = _use_connection_or_default(conn)
				kwargs["conn"] = ownedConn
			else:
				sig = signature(func)
				if len(args) == len(sig.parameters):
					conn = args[-1]
					ownedConn = _use_connection_or_default(conn)
					nargs = (*args[:-1], ownedConn)
				elif len(args) < len(sig.parameters):
					ownedConn = get_configured_db_connection(echo)
					kwargs["conn"] = ownedConn
				else:
					raise ValueError("Too many args provided to this method")
			try:
				func(*nargs, **kwargs)
			finally:
				if not conn:
					ownedConn.close()
		return wrap
	return inner
