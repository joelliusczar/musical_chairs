from musical_chairs_libs.config_loader import get_http_config, get_config
from sqlalchemy import create_engine
from services.station_service import get_station_list
from services.history_service import get_history_for_station
from services.queue_service import get_now_playing_and_queue
import cherrypy



class MusicalChairsApi:

    def __init__(self):
        self.config = get_config()

    @cherrypy.expose
    def index(self):
        return 'Hello World'

    def provide_db_conn(func):
        def wrap(*args, **kwargs):
            self = args[0]
            dbName = self.config['dbName']
            engine = create_engine(f"sqlite+pysqlite:///{self.config['dbName']}")
            conn = engine.connect()
            nargs = (args[0], conn, *args[1:])
            result = func(*nargs, **kwargs)
            conn.close()
            return result
        return wrap

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

if __name__ == '__main__':
    config = get_http_config()
    config['global']['tools.response_headers.on'] = True
    config['global']['tools.response_headers.headers'] = [('Access-Control-Allow-Origin','*')]
    app = MusicalChairsApi()
    cherrypy.quickstart(app, config=config)