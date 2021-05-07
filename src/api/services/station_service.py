from sqlalchemy import select, func
from .tables import stations, stations_tags, songs_tags, tags
import itertools


def get_station_list(conn):
  query = select(stations.c.stationPK, stations.c.name, \
    tags.c.name, tags.c.tagPK) \
    .select_from(stations) \
    .join(stations_tags, stations.c.stationPK == stations_tags.c.stationFK) \
    .join(songs_tags, songs_tags.c.tagFK == stations_tags.c.tagFK) \
    .join(tags, stations_tags.c.tagFK == tags.c.tagPK) \
    .group_by(stations.c.stationPK, stations.c.name, tags.c.name, tags.c.tagPK) \
    .having(func.count(songs_tags.c.tagFK) > 0)
  records = conn.execute(query)
  partition = lambda r: (r[stations.c.stationPK], r[stations.c.name])
  for key, group in itertools.groupby(records, partition):
    yield { 
      "id": key[0],
      "name": key[1], 
      "tags": list(map(lambda r: { 
        "name": r[tags.c.name],
        "id": r[tags.c.tagPK],
      }, group))
    }

