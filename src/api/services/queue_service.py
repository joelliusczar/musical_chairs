from sqlalchemy import create_engine, select, func
from .tables import songs, station_queue, stations
from .history_service import get_history_for_station
from .sql_functions import song_name, album_name, artist_name



def get_now_playing_and_queue(conn, stationName):
    queue = list(get_queue_for_station(conn, stationName))
    try:
        playing = next(get_history_for_station(conn, stationName, 1))
        return {'nowPlaying':playing, 'items': queue}
    except:
        return {'nowPlaying':'', 'items': queue}

