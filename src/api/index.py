import cherrypy
import os
from musical_chairs_libs.config_loader import ConfigLoader
from controllers.stations_controller import StationController
from musical_chairs_libs.station_service import StationService


class MusicalChairsApi:


  @cherrypy.expose
  def default(self, *args, **kwargs):
    print("hit index")
    print(os.getcwd())
    return open("../client/build/index.html")

if __name__ == '__main__':

  dirName = os.path.dirname(os.path.realpath(__file__))
  os.chdir(dirName)
  configLoader = ConfigLoader()
  webConfig = configLoader.get_http_config()
  webConfig["global"]["tools.response_headers.on"] = True
  webConfig["global"]["tools.response_headers.headers"] = \
    [("Access-Control-Allow-Origin","*")]
  webConfig["global"]["tools.sessions.on"] = True
  appConfig = configLoader.config
  app = MusicalChairsApi(appConfig)
  print(webConfig)
  conn = configLoader.get_configured_db_connection()
  stationService = StationService(conn)
  stations = StationController(stationService)
  cherrypy.tree.mount(stations, "/api/stations",webConfig)
  cherrypy.quickstart(app, "/", webConfig)