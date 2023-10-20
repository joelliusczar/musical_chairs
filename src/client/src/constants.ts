import { OwnedStationParams } from "./Types/station_types";
import { OwnerParams, SubjectUserParams } from "./Types/user_types";
import { StringObject } from "./Types/generic_types";


//these vars need to be prefixed VITE
export const baseAddress = import.meta.env.VITE_BASE_ADDRESS;
export const apiVersion = import.meta.env.VITE_API_VERSION;
export const apiAddress = import.meta.env.DEV ?
	baseAddress : `${baseAddress}/api/${apiVersion}`;




export const CallStatus = {
	loading: "loading",
	done: "done",
	failed: "failed",
	idle: "idle",
};

export const DomRoutes = {
	queue: ({ stationkey, ownerkey }: OwnedStationParams) =>
		`/stations/queue/${ownerkey}/${stationkey ? `${stationkey}/` : ""}`,
	history: ({ stationkey, ownerkey }: OwnedStationParams) =>
		`/stations/history/${ownerkey}/${stationkey ? `${stationkey}/` : ""}`,
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

export const UserRoleDomain: StringObject = {
	SITE: "site",
	STATION: "station",
	PATH: "path",
};

export const UserRoleDef: StringObject = {
	ADMIN: "admin",
	SITE_USER_ASSIGN: `${UserRoleDomain.SITE}:userassign`,
	SITE_USER_LIST: `${UserRoleDomain.SITE}:userlist`,
	SITE_PLACEHOLDER: `${UserRoleDomain.SITE}:placeholder`,
	SONG_EDIT: "song:edit",
	SONG_DOWNLOAD: "song:download",
	SONG_TREE_LIST: "songtree:list",
	STATION_VIEW: `${UserRoleDomain.STATION}:view`,
	STATION_CREATE: `${UserRoleDomain.STATION}:create`,
	STATION_EDIT: `${UserRoleDomain.STATION}:edit`,
	STATION_DELETE: `${UserRoleDomain.STATION}:delete`,
	STATION_REQUEST: `${UserRoleDomain.STATION}:request`,
	STATION_FLIP: `${UserRoleDomain.STATION}:flip`,
	STATION_SKIP: `${UserRoleDomain.STATION}:skip`,
	STATION_ASSIGN: `${UserRoleDomain.STATION}:assign`,
	STATION_USER_ASSIGN: `${UserRoleDomain.STATION}:userassign`,
	USER_LIST: "user:list",
	USER_EDIT: "user:edit",
	USER_IMPERSONATE: "user:impersonate",
	PATH_LIST: `${UserRoleDomain.PATH}:list`,
	PATH_EDIT: `${UserRoleDomain.PATH}:edit`,
	PATH_VIEW: `${UserRoleDomain.PATH}:view`,
	PATH_USER_ASSIGN: `${UserRoleDomain.PATH}:userassign`,
	PATH_USER_LIST: `${UserRoleDomain.PATH}:userlist`,
	PATH_DOWNLOAD: `${UserRoleDomain.PATH}:download`,
	PATH_UPLOAD: `${UserRoleDomain.PATH}:upload`,
};

export const MinItemSecurityLevel = {
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