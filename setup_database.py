from musical_chairs_libs.services import (
	DbRootConnectionService,
	DbOwnerConnectionService
)
dbName="test_musical_chairs_db"
with DbRootConnectionService() as rootConnService:
	rootConnService.create_db(dbName)
	rootConnService.create_owner()
	rootConnService.create_app_users()
	rootConnService.grant_owner_roles(dbName)

with DbOwnerConnectionService(dbName, echo=False) as ownerConnService:
	ownerConnService.create_tables()
	ownerConnService.add_path_permission_index()
	ownerConnService.grant_api_roles()
	ownerConnService.grant_radio_roles()
	ownerConnService.add_next_directory_level_func()
	ownerConnService.add_normalize_opening_slash()