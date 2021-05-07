from sqlalchemy import create_engine
from queue_service import get_queue_for_station
from musical_chairs_libs.config_loader import get_config

config = get_config()

engine = create_engine(f"sqlite+pysqlite:///{config['dbName']}")


conn = engine.connect()

q = list(get_queue_for_station(conn, "base", "thinking"))
print(q)