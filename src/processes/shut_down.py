from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.station_proc_manager import end_all_stations
from sqlalchemy import create_engine

if __name__ == '__main__':
    config = get_config()
    dbName = config['dbName']
    engine = create_engine(f"sqlite+pysqlite:///{dbName}")
    conn = engine.connect()
    end_all_stations(conn)
    conn.close()