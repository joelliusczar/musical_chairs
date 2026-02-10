import pytest
import os
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
)
from pathlib import Path

@pytest.fixture(autouse=True)
def fixture_clean_event_logs():
	path = Path(ConfigAcessors.event_log_dir())
	path.mkdir(parents=True, exist_ok=True)
	path = Path(ConfigAcessors.visit_log_dir())
	path.mkdir(parents=True, exist_ok=True)
	yield
	for file in os.scandir(ConfigAcessors.event_log_dir()):
		os.remove(file.path)
	for file in os.scandir(ConfigAcessors.visit_log_dir()):
		os.remove(file.path)