import { OwnedStationParams } from "./Types/station_types";
import { OwnerParams, SubjectUserParams } from "./Types/user_types";
import { StringObject, ParamItem } from "./Types/generic_types";
import { OwnedPlaylistParams } from "./Types/playlist_types";


//these vars need to be prefixed VITE
export const baseAddress = import.meta.env.VITE_BASE_ADDRESS;
export const apiVersion = import.meta.env.VITE_API_VERSION;
export const overrideAddress = import.meta.env.VITE_OVERRIDE_ADDRESS;
export const apiAddress = import.meta.env.DEV && ! overrideAddress ?
	baseAddress :
	!! overrideAddress ? overrideAddress : `${baseAddress}/api/${apiVersion}`;
export const API_ROOT = `/api/${apiVersion}`;




export const CallStatus = {
	loading: "loading",
	done: "done",
	failed: "failed",
	idle: "idle",
};

export const DomRoutes = {
	artistPage: () => "/artists/page",
	artist: ({ id }: ParamItem) => `/artists/${id}`,
	albumPage: () => "/albums/page",
	album: ({ id }: ParamItem) => `/albums/${id}`,
	queue: ({ stationkey, ownerkey }: OwnedStationParams) =>
		`/stations/queue/${ownerkey}/${stationkey ? `${stationkey}/` : ""}`,
	history: ({ stationkey, ownerkey }: OwnedStationParams) =>
		`/stations/history/${ownerkey}/${stationkey ? `${stationkey}/` : ""}`,
	playlistEdit: ({ playlistkey, ownerkey }: OwnedPlaylistParams) =>
		`/playlists/edit/${ownerkey}/${playlistkey}`,
	playlistAdd: () => "/playlist/edit/",
	playlistsPageAll: () => "/playlists/page/",
	playlistsPage: (params: OwnerParams) => 
		`/playlists/page/${params?.ownerkey || ""}`,
	stations: (params?: OwnerParams) =>
		`/stations/list/${params?.ownerkey || ""}`,
	stationsEdit: ({ stationkey, ownerkey }: OwnedStationParams) =>
		`/stations/edit/${ownerkey}/${stationkey}`,
	stationsAdd: () => "/stations/edit/",
	stationUsers: ({ stationkey, ownerkey }: OwnedStationParams) =>
		`/stations/users/${ownerkey}/${stationkey}`,
	songEdit: () => "/songs/edit/",
	songCatalogue: ({ stationkey, ownerkey }: OwnedStationParams) => {
		const stationSegment = stationkey ? `${stationkey}/` : "";
		return `/stations/song-catalogue/${ownerkey}/${stationSegment}`;
	},
	collectionCatalogue: ({ stationkey, ownerkey }: OwnedStationParams) => {
		const stationSegment = stationkey ? `${stationkey}/` : "";
		return `/stations/collection-catalogue/${ownerkey}/${stationSegment}`;
	},
	pathUsers: () => "/song-info/users",
	songTree: () => "/song-info/tree/",
	accountsNew: () => "/accounts/new",
	accountsEdit: ({ subjectuserkey }: SubjectUserParams) =>
		`/accounts/edit/${subjectuserkey}`,
	accountsLogin: () => "/accounts/login",
	accountsRoles: ({ subjectuserkey }: SubjectUserParams) =>
		`/users/roles/${subjectuserkey}`,
	accountsList: () => "/accounts/list",
	notFound: () => "/not-found",
};

export const UserRoleSphere: StringObject = {
	SITE: "site",
	STATION: "station",
	PATH: "path",
	PLAYLIST: "playlist",
	ALBUM: "album",
	ARTIST: "artist",
};

export const UserRoleDef: StringObject = {
	ADMIN: "admin",
	SITE_USER_ASSIGN: `${UserRoleSphere.SITE}:userassign`,
	SITE_USER_LIST: `${UserRoleSphere.SITE}:userlist`,
	SITE_PLACEHOLDER: `${UserRoleSphere.SITE}:placeholder`,

	ALBUM_CREATE: `${UserRoleSphere.ALBUM}:create`,
	ALBUM_EDIT:  `${UserRoleSphere.ALBUM}:edit`,

	ARTIST_CREATE: `${UserRoleSphere.ARTIST}:create`,
	ARTIST_EDIT: `${UserRoleSphere.ARTIST}:edit`,
	ARTIST_VIEW_ALL: `${UserRoleSphere.ARTIST}:view_all`,

	STATION_VIEW: `${UserRoleSphere.STATION}:view`,
	STATION_CREATE: `${UserRoleSphere.STATION}:create`,
	STATION_EDIT: `${UserRoleSphere.STATION}:edit`,
	STATION_DELETE: `${UserRoleSphere.STATION}:delete`,
	STATION_REQUEST: `${UserRoleSphere.STATION}:request`,
	STATION_FLIP: `${UserRoleSphere.STATION}:flip`,
	STATION_SKIP: `${UserRoleSphere.STATION}:skip`,
	STATION_ASSIGN: `${UserRoleSphere.STATION}:assign`,
	STATION_USER_ASSIGN: `${UserRoleSphere.STATION}:userassign`,

	USER_LIST: "user:list",
	USER_EDIT: "user:edit",
	USER_IMPERSONATE: "user:impersonate",
	
	PATH_LIST: `${UserRoleSphere.PATH}:list`,
	PATH_EDIT: `${UserRoleSphere.PATH}:edit`,
	PATH_DELETE: `${UserRoleSphere.PATH}:delete`,
	PATH_VIEW: `${UserRoleSphere.PATH}:view`,
	PATH_USER_ASSIGN: `${UserRoleSphere.PATH}:userassign`,
	PATH_USER_LIST: `${UserRoleSphere.PATH}:userlist`,
	PATH_DOWNLOAD: `${UserRoleSphere.PATH}:download`,
	PATH_UPLOAD: `${UserRoleSphere.PATH}:upload`,

	PLAYLIST_ASSIGN: `${UserRoleSphere.PLAYLIST}:assign`,
	PLAYLIST_CREATE: `${UserRoleSphere.PLAYLIST}:create`,
	PLAYLIST_DELETE: `${UserRoleSphere.PLAYLIST}:delete`,
	PLAYLIST_EDIT: `${UserRoleSphere.PLAYLIST}:edit`,
	PLAYLIST_USER_ASSIGN: `${UserRoleSphere.PLAYLIST}:userassign`,
	PLAYLIST_USER_LIST: `${UserRoleSphere.PLAYLIST}:userlist`,
	PLAYLIST_VIEW: `${UserRoleSphere.PLAYLIST}:view`,
};

export const RulePriorityLevel = {
	PUBLIC: 0,
	// SITE permissions should be able to overpower ANY_USER level restrictions
	ANY_USER: 9,
	// ANY_STATION should be able to overpower RULED_USER
	RULED_USER: 19,
	FRIEND_USER: 29, // not used
	// STATION_PATH should be able to overpower INVITED_USER
	INVITED_USER: 39,
	OWENER_USER: 49,
	//only admins should be able to see these items
	LOCKED: 59,
};

export const StationTypes = {
	SONGS_ONLY: 0,
	//Removed
	// ALBUMS_ONLY: 1,
	// PLAYLISTS_ONLY: 2,
	ALBUMS_AND_PLAYLISTS: 3,
};

export const StationRequestTypes = {
	SONG: 0,
	ALBUM: 1,
	PLAYLIST: 2 ,
};