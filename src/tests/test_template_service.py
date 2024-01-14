#pyright: reportPrivateUsage=false
import pytest
from musical_chairs_libs.services import (
	TemplateService,
	EnvManager,
	ProcessService
)
from .constant_fixtures_for_test import *
from .common_fixtures import(
	fixture_template_service as fixture_template_service,
	fixture_clean_station_folders as fixture_clean_station_folders,
	ices_config_monkey_patch as ices_config_monkey_patch
)


@pytest.mark.usefixtures("ices_config_monkey_patch")
def test_extract_source_password():

	sourcePassword = EnvManager.read_config_value(
		ProcessService.get_icecast_conf_location(),
		"source-password"
	)
	assert sourcePassword == "hackmeSource"

@pytest.mark.usefixtures("fixture_clean_station_folders")
def test_create_station_files(fixture_template_service: TemplateService):
	templateService = fixture_template_service
	templateService.create_station_files(
		3,
		"testSation",
		"A station to be tested",
		"testUser_foxtrot"
	)

