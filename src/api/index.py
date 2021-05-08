from musical_chairs_libs.config_loader import get_http_config, get_config
from controllers.stations_controller import StationController
import cherrypy



class MusicalChairsApi:

  def __init__(self, config):
    self.config = config

  @cherrypy.expose
  def index(self):
    return 'Hello World'


if __name__ == '__main__':
  webConfig = get_http_config()
  webConfig["global"]["tools.response_headers.on"] = True
  webConfig["global"]["tools.response_headers.headers"] = \
    [("Access-Control-Allow-Origin","*")]
  webConfig["global"]["tools.sessions.on"] = True
  appConfig = get_config()
  app = MusicalChairsApi(appConfig)

  stations = StationController(appConfig)
  cherrypy.tree.mount(stations, "/stations",webConfig)
  cherrypy.quickstart(app, "/", webConfig)