import tracemalloc
from musical_chairs_libs.services import EnvManager
from sqlalchemy import (
	select,
	
)
from musical_chairs_libs.dtos_and_utilities import UserRoleDef
from musical_chairs_libs.tables import (
	q_userActionHistoryFk, q_stationFk, q_songFk, uah_pk,
	uah_queuedTimestamp, uah_action, user_action_history,
  songs
)


conn = EnvManager.get_configured_api_connection("musical_chairs_db")

subquery = select(q_userActionHistoryFk.label("fkBob"))\
	.where(q_stationFk == 3)\
	.where(q_songFk == 3603)

query = select(user_action_history.c)\
.where(uah_action == UserRoleDef.STATION_REQUEST.value)\
.where(uah_pk.in_(subquery))
# .where(uah_queuedTimestamp == 1716127797.993587)\

query = select(songs.c)


tracemalloc.start()
print(tracemalloc.get_traced_memory())
result = conn.execution_options().execute(query)

for row in result:
	pass
# while row := result.fetchone():
#     pass

print([round(v/1024) for v in tracemalloc.get_traced_memory()])

# snapshot = tracemalloc.take_snapshot()
# snapshot.filter_traces([tracemalloc.Filter(True, "sqlalchemy/engine/result")])
# top_stats = snapshot.statistics("lineno")

# for stat in top_stats:
#     print(f"{stat.traceback.format()}\n{round(stat.size /1024)}KiB")
# pass