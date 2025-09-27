import sys
from musical_chairs_libs.services import (
	setup_database
)

def setup_db(dbName: str):
	setup_database(dbName)

if __name__ == "__main__":
	dbName = sys.argv[1]
	setup_db(dbName)