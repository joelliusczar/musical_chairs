from sqlalchemy import create_engine
from services.queue_service import get_queue_for_station
from musical_chairs_libs.config_loader import get_config
from services.station_service import get_station_list

config = get_config()

engine = create_engine(f"sqlite+pysqlite:///{config['dbName']}")


conn = engine.connect()

siter = get_station_list(conn)

print(list(siter)[2])
# for s in siter:
#   print(s)