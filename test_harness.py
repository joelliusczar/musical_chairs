import sys
from sqlalchemy import create_engine
from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.queue_manager import get_next_queued
from musical_chairs_libs.station_manager import add_station, assign_tag_to_station




if __name__ == '__main__':
	print(sys.prefix)
	config = get_config()
	searchBase = config["searchBase"]
	dbName = config["dbName"]
	engine = create_engine(f"sqlite+pysqlite:///{config['dbName']}", echo=True)
	conn = engine.connect()
	songInfo = get_next_queued(conn, "VG")

