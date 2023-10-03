import sys
import os

def test_show_path():
	print(os.environ['PYTHONPATH'])
	print(sys.path)

def test_print_schema():
	from musical_chairs_libs.services import EnvManager
	EnvManager.print_expected_schema()

def test_show_db_setup_pass():
	from musical_chairs_libs.services import EnvManager
	dbSetupPass = EnvManager.db_setup_pass
	dbOwnerPass = EnvManager.db_pass_owner
	dbApiPass = EnvManager.db_pass_api
	dbRadioPass = EnvManager.db_pass_radio
	assert dbSetupPass
	assert dbOwnerPass
	assert dbApiPass
	assert dbRadioPass