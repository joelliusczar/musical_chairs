import sys
from musical_chairs_libs.services import (
	DbRootConnectionService,
	setup_database,
)

def setup_db(dbName: str):
	setup_database(dbName)

def teardown_db(dbName: str):
	with DbRootConnectionService() as rootConnService:
		rootConnService.drop_database(dbName, force=True)

if __name__ == "__main__":
	dbName = sys.argv[1]
	if len(sys.argv) > 2 and sys.argv[2].lower() == "clear":
		teardown_db(dbName)
	else:
		setup_db(dbName)