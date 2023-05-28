export const baseAddress = process.env.REACT_APP_BASE_ADDRESS;
export const apiVersion = process.env.REACT_APP_API_VERSION;
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
	queue: ({ stationKey, ownerKey }) =>
		`/stations/queue/${ownerKey}/${stationKey ? `${stationKey}/` : ""}`,
	history: ({ stationKey, ownerKey }) =>
		`/stations/history/${ownerKey}/${stationKey ? `${stationKey}/` : ""}`,
	stations: ({ ownerKey }) => `/stations/${ownerKey}/list/`,
	stationsEdit: ({ stationKey, ownerKey }) =>
		`/stations/edit/${ownerKey}/${stationKey}`,
	stationsAdd: () => "/stations/edit/",
	songEdit: () => "/songs/edit/",
	songCatalogue: ({ stationKey, ownerKey }) => {
		const stationSegment = stationKey ? `${stationKey}/` : "";
		return `/stations/song-catalogue/${ownerKey}/${stationSegment}`;
	},
	songTree: () => "/song-info/tree/",
	accountsNew: () => "/accounts/new",
	accountsEdit: ({ userKey }) => `/accounts/edit/${userKey}`,
	accountsLogin: () => "/accounts/login",
	accountsRoles: ({ userKey }) => `/accounts/roles/${userKey}`,
	accountsList: () => "/accounts/list",
	notFound: () => "/not-found",
};

export const UserRoleDomain = {
	SITE: "site",
	STATION: "station",
	PATH: "path",
};

export const UserRoleDef = {
	ADMIN: "admin",
	SONG_EDIT: "song:edit",
	SONG_DOWNLOAD: "song:download",
	SONG_TREE_LIST: "songtree:list",
	STATION_CREATE: `${UserRoleDomain.STATION}:create`,
	STATION_EDIT: `${UserRoleDomain.STATION}:edit`,
	STATION_DELETE: `${UserRoleDomain.STATION}:delete`,
	STATION_REQUEST: `${UserRoleDomain.STATION}:request`,
	STATION_FLIP: `${UserRoleDomain.STATION}:flip`,
	STATION_SKIP: `${UserRoleDomain.STATION}:skip`,
	STATION_ASSIGN: `${UserRoleDomain.STATION}:assign`,
	USER_LIST: "user:list",
	USER_EDIT: "user:edit",
	USER_IMPERSONATE: "user:impersonate",
	PATH_LIST: `${UserRoleDomain.PATH}:list`,
	PATH_EDIT: `${UserRoleDomain.PATH}:edit`,
	PATH_VIEW: `${UserRoleDomain.PATH}:view`,
	PATH_DOWNLOAD: `${UserRoleDomain.PATH}:download`,
};
