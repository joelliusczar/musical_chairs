from musical_chairs_libs.config_loader import get_http_config, get_config
from musical_chairs_libs.queue_manager import \
get_queue_for_station, \
get_history_for_station, \
get_station_list
import cherrypy
import sqlite3

class MusicalChairsApi:

    def __init__(self):
        self.config = get_config()

    @cherrypy.expose
    def index(self):
        return 'Hello World'

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def queue(self, stationName, limit = 50, pageNumber = 1):
        if not stationName:
            return []
        dbName = self.config['dbName']
        conn = sqlite3.connect(dbName)
        searchBase = self.config['searchBase']
        queue = list(get_queue_for_station(conn, searchBase, stationName))
        conn.close()
        return queue

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def history(self, stationName, limit = 50, pageNumber = 1):
        if not stationName:
            return []
        dbName = self.config['dbName']
        conn = sqlite3.connect(dbName)
        searchBase = self.config['searchBase']
        history = list(get_history_for_station(conn, searchBase, 
                        stationName))
        conn.close()
        return history

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def stations(self):
        dbName = self.config['dbName']
        conn = sqlite3.connect(dbName)
        stations = list(get_station_list)
        conn.close()
        return stations

if __name__ == '__main__':
    config = get_http_config()
    print(config)
    app = MusicalChairsApi()
    cherrypy.quickstart(app, config=config)