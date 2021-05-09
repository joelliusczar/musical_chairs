from musical_chairs_libs.config_loader import get_http_config, get_config
from controllers.stations_controller import StationController
import cherrypy
import os



class MusicalChairsApi:

  def __init__(self, config):
    self.config = config

  @cherrypy.expose
  def index(self):
    print(os.getcwd())
    return open("../client/build/index.html")


if __name__ == '__main__':

  dirName = os.path.dirname(os.path.realpath(__file__))
  os.chdir(dirName)
  webConfig = get_http_config()
  webConfig["global"]["tools.response_headers.on"] = True
  webConfig["global"]["tools.response_headers.headers"] = \
    [("Access-Control-Allow-Origin","*")]
  webConfig["global"]["tools.sessions.on"] = True
  appConfig = get_config()
  app = MusicalChairsApi(appConfig)
  print(webConfig)
  stations = StationController(appConfig)
  cherrypy.tree.mount(stations, "/stations",webConfig)
  cherrypy.quickstart(app, "/", webConfig)