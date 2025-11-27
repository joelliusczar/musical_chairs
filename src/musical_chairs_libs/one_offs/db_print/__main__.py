import sys
from musical_chairs_libs.tables import get_ddl_scripts
from musical_chairs_libs.services import (
	DbRootConnectionService,
	get_schema_hash
)


def print_schema():
	with DbRootConnectionService() as rootConnService:
		print(get_ddl_scripts(rootConnService.conn))

def print_schema_hash():
	print(get_schema_hash())

if __name__ == "__main__":
	choice = sys.argv[1] if len(sys.argv) > 1 else ""
	if choice == "--hash":
		print_schema_hash()
	else:
		print_schema()