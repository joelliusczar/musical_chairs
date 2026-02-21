from typing import Any, Sequence
from datetime import datetime
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos_and_utilities import EmailableUser
from ..mock_datetime_provider import MockDatetimeProvider
from musical_chairs_libs.tables import (
	users,
)
from sqlalchemy import insert

try:
	from . import user_ids
except:
	import user_ids

users_params: list[dict[str, Any]] = [] # this is needed for weird syntax reasons

def get_user_params(
	datetimeProvider: Sequence[datetime],
	primaryUser: EmailableUser,
	testPassword: bytes
) -> list[dict[Any, Any]]:
	global users_params
	users_params = [
		{
			"pk": primaryUser.id,
			"username": primaryUser.username,
			"displayname": None,
			"hashedpw": testPassword,
			"email": primaryUser.email,
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"dirroot": ""
		},
		{
			"pk": user_ids.bravo_user_id,
			"username": "testUser_bravo",
			"displayname": "Bravo Test User",
			"hashedpw": testPassword,
			"email": "test2@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.charlie_user_id,
			"username": "testUser_charlie",
			"displayname": "charlie the user of tests",
			"hashedpw": None,
			"email": "test3@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.delta_user_id,
			"username": "testUser_delta",
			"displayname": "DELTA USER",
			"hashedpw": testPassword,
			"email": "test4@munchopuncho.com",
			"isdisabled": True,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.echo_user_id, #can't use. No password
			"username": "testUser_echo",
			"displayname": "ECHO, ECHO",
			"hashedpw": None,
			"email": "test5@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.foxtrot_user_id,
			"username": "testUser_foxtrot",
			"displayname": "\uFB00 ozotroz",
			"hashedpw": testPassword,
			"email": "test6@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.golf_user_id,
			"username": "testUser_golf",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test7@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.hotel_user_id,
			"username": "testUser_hotel",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test8@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.india_user_id,
			"username": "testUser_india",
			"displayname": "IndiaDisplay",
			"hashedpw": testPassword,
			"email": "test9@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.juliet_user_id,
			"username": "testUser_juliet",
			"displayname": "julietDisplay",
			"hashedpw": testPassword,
			"email": "test10@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.kilo_user_id,
			"username": "testUser_kilo",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test11@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": "/foo"
		},
		{
			"pk": user_ids.lima_user_id,
			"username": "testUser_lima",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test12@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.mike_user_id,
			"username": "testUser_mike",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test13@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.november_user_id,
			"username": "testUser_november",
			"displayname": "\u006E\u0303ovoper",
			"hashedpw": testPassword,
			"email": "test14@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.oscar_user_id,
			"username": "testUser_oscar",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test15@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.papa_user_id,
			"username": "testUser_papa",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test16@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.quebec_user_id,
			"username": "testUser_quebec",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test17@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.romeo_user_id,
			"username": "testUser_romeo",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test18@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.sierra_user_id,
			"username": "testUser_sierra",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test19@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.tango_user_id,
			"username": "testUser_tango",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test20@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.uniform_user_id,
			"username": "testUser_uniform",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test21@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.victor_user_id,
			"username": "testUser_victor",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test22@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.whiskey_user_id,
			"username": "testUser_whiskey",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test23@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.xray_user_id,
			"username": "testUser_xray",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test24@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.yankee_user_id,
			"username": "testUser_yankee",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test25@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.zulu_user_id,
			"username": "testUser_zulu",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test26@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.alice_user_id,
			"username": "testUser_alice",
			"displayname": "Alice is my name",
			"hashedpw": testPassword,
			"email": "test27@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.bertrand_user_id,
			"username": "bertrand",
			"displayname": "Bertrance",
			"hashedpw": testPassword,
			"email": "test28@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.carl_user_id,
			"username": "carl",
			"displayname": "Carl the Cactus",
			"hashedpw": testPassword,
			"email": "test29@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.dan_user_id,
			"username": "dan",
			"displayname": "Dookie Dan",
			"hashedpw": testPassword,
			"email": "test30@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.felix_user_id,
			"username": "felix",
			"displayname": "Felix the man",
			"hashedpw": testPassword,
			"email": "test31@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.foxman_user_id,
			"username": "foxman",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test32@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.foxtrain_user_id,
			"username": "foxtrain",
			"displayname": "Foxtrain chu",
			"hashedpw": testPassword,
			"email": "test33@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.george_user_id,
			"username": "george",
			"displayname": "George Costanza",
			"hashedpw": testPassword,
			"email": "test35@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.hamburger_user_id,
			"username": "hamburger",
			"displayname": "HamBurger",
			"hashedpw": testPassword,
			"email": "test36@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.horsetel_user_id,
			"username": "horsetel",
			"displayname": "horsetelophone",
			"hashedpw": testPassword,
			"email": "test37@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.ingo_user_id,
			"username": "ingo",
			"displayname": "Ingo      is a bad man",
			"hashedpw": testPassword,
			"email": "test38@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.ned_land_user_id,
			"username": "ned_land",
			"displayname": "Ned Land of the Spear",
			"hashedpw": testPassword,
			"email": "test39@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.narlon_user_id,
			"username": "narlon",
			"displayname": "Narloni",
			"hashedpw": testPassword,
			"email": "test40@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.number_user_id,
			"username": "7",
			"displayname": "seven",
			"hashedpw": testPassword,
			"email": "test41@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.oomdwell_user_id,
			"username": "testUser_oomdwell",
			"displayname": "Oomdwellmit",
			"hashedpw": testPassword,
			"email": "test42@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": user_ids.paul_bear_user_id,
			"username": "paulBear_testUser",
			"displayname": "Paul Bear",
			"hashedpw": testPassword,
			"email": "test43@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": "paulBear_testUser"
		},
		{
			"pk": user_ids.quirky_admin_user_id,
			"username": "quirkyAdmon_testUser",
			"displayname": "Quirky Admin",
			"hashedpw": testPassword,
			"email": "test44@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": "quirkyAdmon_testUser"
		},
		{
			"pk": user_ids.radical_path_user_id,
			"username": "radicalPath_testUser",
			"displayname": "Radical Path",
			"hashedpw": testPassword,
			"email": "test45@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": "radicalPath_testUser"
		},
		{
			"pk": user_ids.station_saver_user_id,
			"username": "stationSaver_testUser",
			"displayname": "Station Saver",
			"hashedpw": testPassword,
			"email": "test46@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": "stationSaver_testUser"
		},
		{
			"pk": user_ids.super_path_user_id,
			"username": "superPath_testUser",
			"displayname": "Super Pathouser",
			"hashedpw": testPassword,
			"email": "test47@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": "superPath_testUser"
		},
		{
			"pk": user_ids.tossed_slash_user_id,
			"username": "tossedSlash_testUser",
			"displayname": "Tossed Slash",
			"hashedpw": testPassword,
			"email": "test48@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": "tossedSlash"
		},
		{
			"pk": user_ids.unruled_station_user_id,
			"username": "unruledStation_testUser",
			"displayname": "Unruled Station User",
			"hashedpw": testPassword,
			"email": "test49@munchopuncho.com",
			"isdisabled": False,
			"creationtimestamp": datetimeProvider[1].timestamp(),
			"dirroot": "unruledStation"
		}
	]
	for user in users_params:
		user["publictoken"] = user_ids.public_tokens[user["pk"]]
		user["hiddentoken"] = user_ids.hidden_tokens[user["pk"]]
	return users_params



def populate_users(
	conn: Connection,
	datetimeProvider: MockDatetimeProvider,
	primaryUser: EmailableUser,
	testPassword: bytes
):
	userParams = get_user_params(datetimeProvider, primaryUser, testPassword)
	stmt = insert(users)
	conn.execute(stmt, userParams)
