#pyright: reportPrivateUsage=false
import pytest
from musical_chairs_libs.services import TemplateService
from .constant_fixtures_for_test import *
from .common_fixtures import\
	fixture_template_service as fixture_template_service,\
	fixture_clean_station_folders as fixture_clean_station_folders



def test_extract_source_password(fixture_template_service: TemplateService):
	templateService = fixture_template_service
	sourcePassword = templateService.__extract_icecast_source_password__()
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

