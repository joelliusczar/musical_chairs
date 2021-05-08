from services.station_service import get_station_list, \
  get_station_song_catalogue, add_song_to_queue
from services.queue_service import get_now_playing_and_queue
from controller_decorators import provide_db_conn, check_access
from services.history_service import get_history_for_station
import cherrypy

class StationController:

  def __init__(self, config):
    self.config = config

  def _cp_dispatch(self, vpath):
    if len(vpath) == 2:
      cherrypy.request.params["stationName"] = vpath.pop(0)
    if len(vpath) == 3:
      cherrypy.request.params["stationName"] = vpath.pop(0)
      cherrypy.request.params["songPK"] = vpath.pop()
    print(vpath)
    return self


  @cherrypy.expose
  @cherrypy.tools.json_out()
  @provide_db_conn
  def index(self, conn):
    stations = list(get_station_list(conn))
    return { "items": stations }

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @provide_db_conn
  def history(self, conn, stationName = "", limit = 50, pageNumber = 0):
    if not stationName:
      return []
    searchBase = self.config['searchBase']
    history = list(get_history_for_station(conn, searchBase, 
      stationName))
    return {"items": history }

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @provide_db_conn
  def queue(self, conn, stationName = "", limit = 50, pageNumber = 1):
    if not stationName:
      return []
    searchBase = self.config['searchBase']
    queue = get_now_playing_and_queue(conn, searchBase, stationName)
    return queue

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @provide_db_conn
  def song_catalogue(self, conn, stationName):
    if not stationName:
      return []
    searchBase = self.config['searchBase']
    songs = list(get_station_song_catalogue(conn, searchBase, stationName))
    return { "items": songs}

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @check_access
  @provide_db_conn
  def request(self, conn, stationName, songPK):
    r = cherrypy.request
    resultCount = add_song_to_queue(conn, stationName, songPK)
    return resultCount