import cherrypy
from musical_chairs_libs.station_service import StationService
from controller_decorators import check_access
from musical_chairs_libs.history_service import HistoryService
from musical_chairs_libs.queue_service import QueueService


class StationController:

  def __init__(self, stationService: StationService, 
  historyService: HistoryService,
  queueService: QueueService):
    self.station_service = stationService
    self.history_service = historyService
    self.queue_service = queueService

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
  def index(self):
    stations = list(self.station_service.get_station_list())
    return { "items": stations }

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def history(self, stationName = "", limit = 50, pageNumber = 0, conn = None):
    if not stationName:
      return []
    history = list(self.history_service.get_history_for_station(stationName))
    return {"items": history }

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def queue(self, stationName = "", limit = 50, pageNumber = 1, conn = None):
    if not stationName:
      return []
    queue = self.queue_service.get_now_playing_and_queue(stationName)
    return queue

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def song_catalogue(self, stationName, conn):
    if not stationName:
      return []
    songs = list(self.station_service.get_station_song_catalogue(stationName))
    return { "items": songs}

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @check_access
  def request(self, stationName, songPK, conn):
    r = cherrypy.request
    resultCount = self.queue_service.add_song_to_queue(stationName, songPK)
    return resultCount