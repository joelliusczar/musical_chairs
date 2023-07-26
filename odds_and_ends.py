import re
from musical_chairs_libs.services import EnvManager
from io import StringIO
from typing import Iterable, cast
from sqlalchemy.engine.row import Row
from musical_chairs_libs.tables import metadata
from contextlib import redirect_stdout
from src.tests.mocks.db_population import *
from src.tests.mocks.constant_values_defs import (
	mock_ordered_date_list,
	primary_user,
	mock_password
)


conn = EnvManager.get_configured_db_connection(inMemory=True)
metadata.create_all(conn.engine)
buffer = StringIO()
# with open("test_db.sql","w") as f:
with redirect_stdout(buffer):
	result = conn.execute("SELECT sql FROM sqlite_master WHERE type='table';") #pyright: ignore [reportUnknownMemberType]
	result = [cast(str,r[0]) for r in cast(Iterable[Row],result.fetchall())]
	result.append("")
	print(";\n".join(result))
	result = conn.execute("SELECT sql FROM sqlite_master WHERE type='index';") #pyright: ignore [reportUnknownMemberType]
	result = [cast(str,r[0]) for r in cast(Iterable[Row],result.fetchall())]
	result.append("")
	print(";\n".join(result))
	conn.connection.connection.set_trace_callback(print) #pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
	populate_artists(conn)
	populate_albums(conn)
	populate_songs(conn)
	populate_songs_artists(conn)
	populate_stations_songs(conn)
	populate_stations(conn)
	populate_users(
		conn,
		mock_ordered_date_list,
		primary_user(),
		mock_password()
	)
	populate_user_roles(conn, mock_ordered_date_list, primary_user())
	populate_station_permissions(conn, mock_ordered_date_list)
	populate_path_permissions(conn, mock_ordered_date_list)
	populate_user_actions_history(conn, mock_ordered_date_list)
	populate_station_queue(conn)
conn.close()
contents = buffer.getvalue()
contents = re.sub(r"(INSERT .+)\n", lambda m: f"{m.group(1)};\n", contents)
contents = re.sub(r"(BEGIN) *\n", lambda m: f"{m.group(1)};\n", contents)
contents = re.sub(r"(COMMIT)\n", lambda m: f"{m.group(1)};\n", contents)
with open("test_db.sql","w") as f:
	f.write(contents)
