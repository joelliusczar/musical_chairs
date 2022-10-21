import pytest
from musical_chairs_libs.services import TagService
from musical_chairs_libs.errors import AlreadyUsedError
from .mocks.db_population import get_starting_tags
from .common_fixtures import \
	fixture_tag_service as fixture_tag_service
from .common_fixtures import *


def test_save_tag(fixture_tag_service: TagService):
	tagService = fixture_tag_service
	result = tagService.save_tag("brandNewTag")
	assert result.id == len(get_starting_tags()) + 1
	fetched = list(tagService.get_tags(tagIds=[result.id]))
	assert len(fetched) == 1
	with pytest.raises(AlreadyUsedError):
		tagService.save_tag("mike_tag")
	with pytest.raises(AlreadyUsedError):
		tagService.save_tag("mike_tag", 6)