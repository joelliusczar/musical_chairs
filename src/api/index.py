import cherrypy
import os
from typing import Any, Dict
from musical_chairs_libs.config_loader import ConfigLoader
from controllers.stations_controller import StationController
from musical_chairs_libs.station_service import StationService


class MusicalChairsApi:

	def __init__(self, httpConfig: Dict[str, Any]) -> None:
			self.http_config = httpConfig

	@cherrypy.expose
	def default(self, *args, **kwargs):
		print("hit index")
		print(os.getcwd())
		contentPath = self.http_config["\\"]["tools.staticdir.dir"]
		return open(f"{contentPath}/index.html")

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
	app = MusicalChairsApi(webConfig)
	print(webConfig)
	conn = configLoader.get_configured_db_connection()
	stationService = StationService(conn)
	stations = StationController(stationService)
	cherrypy.tree.mount(stations, "/api/stations", webConfig)
	cherrypy.quickstart(app, "/", webConfig)