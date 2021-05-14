
from sqlalchemy import create_engine
from services.sql_functions import song_name, album_name, artist_name
import time
import cherrypy

def provide_db_conn(func):
    def wrap(*args, **kwargs):
        self = args[0]
        dbName = self.config['dbName']
        engine = create_engine(f"sqlite+pysqlite:///{self.config['dbName']}")
        conn = engine.connect()
        conn.connection.connection \
            .create_function("song_name", 2, song_name, \
                deterministic=True)
        conn.connection.connection \
            .create_function("artist_name", 2, artist_name, \
                deterministic=True)
        conn.connection.connection \
            .create_function("album_name", 2, album_name, \
                deterministic=True)
        nargs = (args[0], conn, *args[1:])
        result = func(*nargs, **kwargs)
        conn.close()
        return result
    return wrap

def check_access(func):
  def wrap(*args, **kwargs):
    print(cherrypy.request.header_list)
    if "lastVisited" in cherrypy.session:
      print(cherrypy.session["lastVisited"])
    cherrypy.session["lastVisited"] = time.time()
    result = func(*args, **kwargs)
    return result
  return wrap