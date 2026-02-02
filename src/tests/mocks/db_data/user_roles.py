from typing import Any
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	RulePriorityLevel,
)
from sqlalchemy.engine import Connection
from ..mock_datetime_provider import MockDatetimeProvider
from musical_chairs_libs.dtos_and_utilities.constants import (
	UserRoleSphere
)
from musical_chairs_libs.tables import (
	userRoles,
)
from sqlalchemy import insert

try:
	from . import user_ids
except:
	import user_ids



def get_user_role_params(
	datetimeProvider: MockDatetimeProvider,
	primaryUser: AccountInfo,
) -> list[dict[Any, Any]]:
	return [
		{
			"userfk": primaryUser.id,
			"role": UserRoleDef.ADMIN.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.bravo_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.charlie_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.delta_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.delta_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.foxtrot_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 15,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.foxtrot_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 120,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.foxtrot_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.golf_user_id,
			"role": UserRoleDef.USER_LIST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.juliet_user_id,
			"role": UserRoleDef.STATION_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.quebec_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":300,
			"quota":15,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.juliet_user_id,
			"role": UserRoleDef.PLAYLIST_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.bravo_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.bravo_user_id,
			"role": UserRoleDef.PLAYLIST_CREATE.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.tango_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.ALBUM_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.hotel_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.hotel_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.hotel_user_id,
			"role": UserRoleDef.ALBUM_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.whiskey_user_id,
			"role": UserRoleDef.STATION_VIEW.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.whiskey_user_id,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.november_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"quota":10,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.lima_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.mike_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.mike_user_id,
			"role": UserRoleDef.ALBUM_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.oscar_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":120,
			"quota":5,
			"priority": RulePriorityLevel.INVITED_USER.value + 1,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.papa_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"quota":20,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.alice_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"quota":20,
			"priority": RulePriorityLevel.SITE.value - 2,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.paul_bear_user_id,
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.quirky_admin_user_id,
			"role": UserRoleDef.ADMIN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.radical_path_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.super_path_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SUPER.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.unruled_station_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.sierra_user_id,
			"role": UserRoleDef.ALBUM_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
	]


def get_station_permission_params(
	datetimeProvider: MockDatetimeProvider
) -> list[dict[Any, Any]]:
	return [
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.kilo_user_id,
			"keypath": "3",
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.mike_user_id,
			"keypath": "3",
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.november_user_id,
			"keypath": "3",
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"quota":5,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.oscar_user_id,
			"keypath": "3",
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":60,
			"quota":5,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.papa_user_id,
			"keypath": "3",
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"quota":25,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.quebec_user_id,
			"keypath": "3",
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"quota":25,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.juliet_user_id,
			"keypath": "9",
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.juliet_user_id,
			"keypath": "5",
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.juliet_user_id,
			"keypath": "9",
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.hotel_user_id,
			"keypath": "9",
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.xray_user_id,
			"keypath": "14",
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.zulu_user_id,
			"keypath": "14",
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.INVITED_USER.value - 5,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.narlon_user_id,
			"keypath": "17",
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.narlon_user_id,
			"keypath": "17",
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.narlon_user_id,
			"keypath": "17",
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":5,
			"quota":300,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.narlon_user_id,
			"keypath": "18",
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.narlon_user_id,
			"keypath": "18",
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":100,
			"quota":300,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.horsetel_user_id,
			"keypath": "17",
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.george_user_id,
			"keypath": "17",
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.george_user_id,
			"keypath": "17",
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":70,
			"quota":10,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.george_user_id,
			"keypath": "17",
			"role": UserRoleDef.STATION_FLIP.value,
			"span":70,
			"quota":10,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.carl_user_id,
			"keypath": "17",
			"role": UserRoleDef.STATION_FLIP.value,
			"span":70,
			"quota":10,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.oomdwell_user_id,
			"keypath": "11",
			"role": UserRoleDef.STATION_USER_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Station.value,
			"userfk": user_ids.unruled_station_user_id,
			"keypath": "20",
			"role": UserRoleDef.STATION_FLIP.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
	]


def get_playlist_permission_params(
	orderedTestDates: MockDatetimeProvider
) -> list[dict[Any, Any]]:
	return [
		{
			"sphere": UserRoleSphere.Playlist.value,
			"userfk": user_ids.juliet_user_id,
			"keypath": "9",
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Playlist.value,
			"userfk": user_ids.juliet_user_id,
			"keypath": "5",
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Playlist.value,
			"userfk": user_ids.hotel_user_id,
			"keypath": "9",
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Playlist.value,
			"userfk": user_ids.xray_user_id,
			"keypath": "14",
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Playlist.value,
			"userfk": user_ids.zulu_user_id,
			"keypath": "14",
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.INVITED_USER.value - 5,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Playlist.value,
			"userfk": user_ids.narlon_user_id,
			"keypath": "17",
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Playlist.value,
			"userfk": user_ids.narlon_user_id,
			"keypath": "17",
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Playlist.value,
			"userfk": user_ids.narlon_user_id,
			"keypath": "18",
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Playlist.value,
			"userfk": user_ids.horsetel_user_id,
			"keypath": "17",
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Playlist.value,
			"userfk": user_ids.george_user_id,
			"keypath": "17",
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Playlist.value,
			"userfk": user_ids.oomdwell_user_id,
			"keypath": "11",
			"role": UserRoleDef.PLAYLIST_USER_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
	]


def get_path_permission_params(
	datetimeProvider: MockDatetimeProvider
)  -> list[dict[Any, Any]]:
	keypathPermissions: list[dict[str, Any]] = [
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.lima_user_id,
			"keypath": "foo/goo/boo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.kilo_user_id,
			"keypath": "foo/goo/shoo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.kilo_user_id,
			"keypath": "foo/goo/moo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.kilo_user_id,
			"keypath": "foo/goo/shoo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.kilo_user_id,
			"keypath": "foo/goo/shoo",
			"role": UserRoleDef.PATH_DOWNLOAD.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.lima_user_id,
			"keypath": "foo/goo/boo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.mike_user_id,
			"keypath": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.mike_user_id,
			"keypath": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.sierra_user_id,
			"keypath": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.sierra_user_id,
			"keypath": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.sierra_user_id,
			"keypath": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.sierra_user_id,
			"keypath": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"quota":0, #blocked
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.foxtrot_user_id,
			"keypath": "/foo/goo/boo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.uniform_user_id,
			"keypath": "/foo/d",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.uniform_user_id,
			"keypath": "/foo/b",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.station_saver_user_id,
			"keypath": "/foo/b",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"sphere": UserRoleSphere.Path.value,
			"userfk": user_ids.station_saver_user_id,
			"keypath": "/foo/b",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		}
	]
	return keypathPermissions


def populate_user_roles(
	conn: Connection,
	datetimeProvider: MockDatetimeProvider,
	primaryUser: AccountInfo,
):
	userRoleParams = get_user_role_params(datetimeProvider, primaryUser)
	stmt = insert(userRoles)
	conn.execute(stmt, userRoleParams) #pyright: ignore [reportUnknownMemberType]

	stationPermissionParams = get_station_permission_params(datetimeProvider)
	stmt = insert(userRoles)
	conn.execute(stmt, stationPermissionParams) #pyright: ignore [reportUnknownMemberType]

	playlistPermissionParams = get_playlist_permission_params(datetimeProvider)
	stmt = insert(userRoles)
	conn.execute(stmt, playlistPermissionParams) #pyright: ignore [reportUnknownMemberType]

	pathPermissionParams = get_path_permission_params(datetimeProvider)
	stmt = insert(userRoles)
	conn.execute(stmt, pathPermissionParams) #pyright: ignore [reportUnknownMemberType]