import { OwnedStationParams } from "./Types/station_types";
import { OwnerParams, SubjectUserParams } from "./Types/user_types";
import { StringObject } from "./Types/generic_types";

export const baseAddress = process.env.reactAppBaseAddress;
export const apiVersion = process.env.reactAppApiVersion;
export const isDev = process.env.NODE_ENV === "development";
export const apiAddress = isDev ?
	baseAddress : `${baseAddress}/api/${apiVersion}`;




export const CallStatus = {
	loading: "loading",
	done: "done",
	failed: "failed",
	idle: "idle",
};

export const DomRoutes = {
	queue: ({ stationKey, ownerKey }: OwnedStationParams) =>
		`/stations/queue/${ownerKey}/${stationKey ? `${stationKey}/` : ""}`,
	history: ({ stationKey, ownerKey }: OwnedStationParams) =>
		`/stations/history/${ownerKey}/${stationKey ? `${stationKey}/` : ""}`,
	stations: (params?: OwnerParams) =>
		`/stations/list/${params?.ownerKey || ""}`,
	stationsEdit: ({ stationKey, ownerKey }: OwnedStationParams) =>
		`/stations/edit/${ownerKey}/${stationKey}`,
	stationsAdd: () => "/stations/edit/",
	stationUsers: ({ stationKey, ownerKey }: OwnedStationParams) =>
		`/stations/users/${ownerKey}/${stationKey}`,
	songEdit: () => "/songs/edit/",
	songCatalogue: ({ stationKey, ownerKey }: OwnedStationParams) => {
		const stationSegment = stationKey ? `${stationKey}/` : "";
		return `/stations/song-catalogue/${ownerKey}/${stationSegment}`;
	},
	pathUsers: () => "/song-info/users",
	songTree: () => "/song-info/tree/",
	accountsNew: () => "/accounts/new",
	accountsEdit: ({ subjectUserKey }: SubjectUserParams) =>
		`/accounts/edit/${subjectUserKey}`,
	accountsLogin: () => "/accounts/login",
	accountsRoles: ({ subjectUserKey }: SubjectUserParams) =>
		`/users/roles/${subjectUserKey}`,
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