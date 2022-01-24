import yaml
import os
from sqlalchemy import create_engine


def get_config():
    config_path = os.environ["config_file"]

    config = None

    with open(config_path,"r") as stream:
        config =  yaml.safe_load(stream)
    return config

def get_http_config():
    config_path = os.environ["http_config"]

    with open(config_path,"r") as stream:
        config =  yaml.safe_load(stream)
    return config

def get_configured_db_connection(echo = False):
  config = get_config()
  engine = create_engine(f"sqlite+pysqlite:///{config['dbName']}", echo=echo)
  return engine.connect()