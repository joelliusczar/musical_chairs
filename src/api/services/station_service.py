from sqlalchemy import select, func
from .tables import stations, stations_tags, songs_tags


def get_station_list(conn):
  query = select(stations.c.stationPK, stations.c.name) \
    .select_from(stations) \
    .join(stations_tags, stations.c.stationPK == stations_tags.c.stationFK) \
    .join(songs_tags, songs_tags.c.tagFK == stations_tags.c.tagFK) \
    .group_by(stations.c.stationPK, stations.c.name) \
    .having(func.count(songs_tags.c.tagFK) > 0)
  records = conn.execute(query)
  for row in records:
    yield { 'name': row["name"]}

