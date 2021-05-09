from sqlalchemy import create_engine, select, func, literal
from services.queue_service import get_queue_for_station
from musical_chairs_libs.config_loader import get_config
from services.station_service import get_station_list, \
  get_station_song_catalogue, add_song_to_queue
from tinytag import TinyTag
from services.tables import songs
from services.sql_functions import song_name, album_name, artist_name
import os

# def song_name(path, searchBase):
#   songFullPath = path
#   try:
#     tag = TinyTag.get(songFullPath)
#     return tag.title
#   except:
#     return searchBase


config = get_config()

engine = create_engine(f"sqlite+pysqlite:///{config['dbName']}")


conn = engine.connect()
conn.connection.connection.create_function("song_name", 2, song_name, 
deterministic=True)
conn.connection.connection.create_function("artist_name", 2, artist_name, 
deterministic=True)
conn.connection.connection.create_function("album_name", 2, album_name, 
deterministic=True)

# q = select(songs.c.songPK, func.song_name(songs.c.path, "doink!!")) \
#   .limit(5)

# r = conn.execute(q)
# for row in r:
#   print(row)
# siter = get_station_song_catalogue(conn, "","thinking")

# #print(list(siter)[2])
# for s in siter:
#   print(s)

# q = select(songs.c.songPK, literal("'\");five")).limit(5);
# print(q)
# r = conn.execute(q)
# for row in r:
#   print(row)

# res = add_song_to_queue(conn,"thinking",7)
# print(res)

print(os.getcwd())
print(__file__)
print(os.path.realpath(__file__))
