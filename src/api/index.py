from musical_chairs_libs.config_loader import get_http_config, get_config
from services.station_service import get_station_list, \
  get_station_song_catalogue
from services.history_service import get_history_for_station
from services.queue_service import get_now_playing_and_queue
from controller_helper import provide_db_conn
import cherrypy



class MusicalChairsApi:

  def __init__(self, config):
    self.config = config

  @cherrypy.expose
  def index(self):
    return 'Hello World'


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
  def history(self, conn, stationName = "", limit = 50, pageNumber = 1):
    if not stationName:
      return []
    searchBase = self.config['searchBase']
    history = list(get_history_for_station(conn, searchBase, 
      stationName))
    return history

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @provide_db_conn
  def stations(self, conn):
    stations = list(get_station_list(conn))
    return stations

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @provide_db_conn
  def song_catalogue(self, conn, stationName):
    if not stationName:
      return []
    searchBase = self.config['searchBase']
    songs = list(get_station_song_catalogue(conn, searchBase, stationName))
    return songs

if __name__ == '__main__':
  config = get_http_config()
  config['global']['tools.response_headers.on'] = True
  config['global']['tools.response_headers.headers'] = [('Access-Control-Allow-Origin','*')]
  app = MusicalChairsApi(get_config())
  cherrypy.quickstart(app, config=config)