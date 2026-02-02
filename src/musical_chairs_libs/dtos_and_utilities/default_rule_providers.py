from typing import Collection, Iterator
from .action_rule_dtos import ActionRule
from .user_role_def import RulePriorityLevel, UserRoleDef
from .constants import UserRoleSphere


path_owner_rules = [
	UserRoleDef.PATH_DELETE,
	UserRoleDef.PATH_DOWNLOAD,
	UserRoleDef.PATH_EDIT,
	UserRoleDef.PATH_LIST,
	UserRoleDef.PATH_VIEW,
	UserRoleDef.PATH_MOVE,
	UserRoleDef.PATH_USER_LIST,
	UserRoleDef.PATH_USER_ASSIGN,
	UserRoleDef.PATH_UPLOAD,
]

def get_path_owner_roles(
	ownerDir: str | None,
	scopes: Collection[str] | None=None
) -> Iterator[ActionRule]:
		if not ownerDir:
			return
		for rule in path_owner_rules:
			if not scopes or rule.value in scopes:
				if rule == UserRoleDef.PATH_DOWNLOAD:
					yield ActionRule(
						name=rule.value,
						priority=RulePriorityLevel.USER.value,
						sphere=UserRoleSphere.Path.value,
						keypath=ownerDir,
						span=60,
						quota=12
					)
					continue
				yield ActionRule(
						name=rule.value,
						priority=RulePriorityLevel.OWNER.value,
						sphere=UserRoleSphere.Path.value,
						keypath=ownerDir,
					)

#create left out on purpose
playlist_owner_rules = [
	UserRoleDef.PLAYLIST_VIEW,
	UserRoleDef.PLAYLIST_EDIT,
	UserRoleDef.PLAYLIST_DELETE,
	UserRoleDef.PLAYLIST_ASSIGN,
	UserRoleDef.PLAYLIST_USER_ASSIGN,
	UserRoleDef.PLAYLIST_USER_LIST,
]

def get_playlist_owner_roles(
	scopes: Collection[str] | None=None
) -> Iterator[ActionRule]:
	for rule in playlist_owner_rules:
		if not scopes or rule.value in scopes:
			yield ActionRule(
				name=rule.value,
				priority=RulePriorityLevel.OWNER.value,
				sphere=UserRoleSphere.Playlist.value
			)


#STATION_CREATE, STATION_FLIP, STATION_REQUEST, STATION_SKIP
	# left out of here on purpose
	# for STATION_FLIP, STATION_REQUEST, STATION_SKIP, we should have
	#explicit rules with defined limts
station_owner_rules = [
	UserRoleDef.STATION_ASSIGN,
	UserRoleDef.STATION_DELETE,
	UserRoleDef.STATION_EDIT,
	UserRoleDef.STATION_VIEW,
	UserRoleDef.STATION_USER_ASSIGN,
	UserRoleDef.STATION_USER_LIST
]

def get_station_owner_rules(
	scopes: Collection[str] | None=None
) -> Iterator[ActionRule]:
	for rule in station_owner_rules:
		if not scopes or rule.value in scopes:
			yield ActionRule(
				name=rule.value,
				priority=RulePriorityLevel.OWNER.value,
				sphere=UserRoleSphere.Station.value
			)



album_owner_rules = [
	UserRoleDef.ALBUM_EDIT,
]

def get_album_owner_roles(
	scopes: Collection[str] | None=None
) -> Iterator[ActionRule]:
	for rule in album_owner_rules:
		if not scopes or rule.value in scopes:
			yield ActionRule(
				name=rule.value,
				priority=RulePriorityLevel.OWNER.value,
				sphere=UserRoleSphere.Album.value
			)

artist_owner_rules = [
	UserRoleDef.ARTIST_EDIT,
]

def get_artist_owner_roles(
	scopes: Collection[str] | None=None
) -> Iterator[ActionRule]:
	for rule in artist_owner_rules:
		if not scopes or rule.value in scopes:
			yield ActionRule(
				name=rule.value,
				priority=RulePriorityLevel.OWNER.value,
				sphere=UserRoleSphere.Artist.value
			)

starting_user_roles = [
	UserRoleDef.PLAYLIST_CREATE,
	UserRoleDef.STATION_CREATE,
	UserRoleDef.ARTIST_CREATE,
	UserRoleDef.ALBUM_CREATE,
]

def get_starting_site_roles(
	scopes: Collection[str] | None=None
) -> Iterator[ActionRule]:
	for rule in starting_user_roles:
		if not scopes or rule.value in scopes:
			yield ActionRule(
				name=rule.value,
				priority=RulePriorityLevel.USER.value,
				span=60,
				quota=1
			)