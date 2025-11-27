import sys
import os
import pytest

@pytest.mark.skip()
def test_show_path():
	print(os.environ['PYTHONPATH'])
	print(sys.path)


def test_show_db_setup_pass():
	from musical_chairs_libs.dtos_and_utilities import ConfigAcessors
	dbSetupPass = ConfigAcessors.db_setup_pass()
	dbOwnerPass = ConfigAcessors.db_pass_owner()
	dbApiPass = ConfigAcessors.db_pass_api()
	dbRadioPass = ConfigAcessors.db_pass_radio()
	assert dbSetupPass
	assert dbOwnerPass
	assert dbApiPass
	assert dbRadioPass