from musical_chairs_libs.tables import get_ddl_scripts
from musical_chairs_libs.services import (
	DbRootConnectionService,
)


def print_schema():
	with DbRootConnectionService() as rootConnService:
		print(get_ddl_scripts(rootConnService.conn))



if __name__ == "__main__":
	print_schema()