import yaml
import os
import sqlite3
from queue_manager import get_next_queued 

if __name__ == '__main__':

    configPath = ''
    if 'radio_config' in os.environ:
        configPath = os.environ['radio_config']
    else:
        configPath = 'src/configs/config.yml'

    config = None

    with open(configPath,'r') as stream:
        config =  yaml.safe_load(stream)

    searchBase = config['searchBase']
    dbName = config['dbName']

    conn = sqlite3.connect(dbName)
    print(get_next_queued(conn, 'movies'))
    conn.close()
