from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.station_proc_manager import end_all_stations

if __name__ == '__main__':
    config = get_config()
    dbName = config['dbName']
    conn = sqlite3.connect(dbName)
    end_all_stations(conn)
    conn.commit()
    conn.close()