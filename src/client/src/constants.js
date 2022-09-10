export const apiAddress = process.env.REACT_APP_API_ADDRESS;
export const apiVersion = process.env.REACT_APP_API_VERSION;

export const CallStatus = {
	loading: "loading",
	done: "done",
	failed: "failed",
	idle: "idle",
};

export const CallType = {
	fetch: "fetch",
	post: "post",
};

export const DomRoutes = {
	queue: "/queue/",
	history: "/history/",
	stations: "/stations/list/",
	stationsEdit: "/stations/edit/",
	songEdit: "/songs/edit/",
	songCatalogue: "/song-catalogue/",
	songTree: "/song-info/tree/",
	accountsNew: "/accounts/new",
	accountsLogin: "/accounts/login",
	accountsRoles: "/accounts/roles/",
	accountsList: "/accounts/list",
	notFound: "/not-found",
};

export const ApiRoutes = {
	queue: (stationName) => `stations/${stationName}/queue/`,
	history: (stationName) =>
		`stations/${stationName}/history/`,
	stations: () => "stations/",
	songRequest: (stationName, songId) =>
		`stations/${stationName}/request/${songId}`,
	songCatalogue: (stationName) =>
		`stations/${stationName}/catalogue/`,
	login: "token",
	check: "accounts/check",
	setupInfo: "accounts/setup-info",
};

export const UserRoleDef = {
	"ADMIN": "admin::",
	"SONG_EDIT": "song:edit:",
	"SONG_REQUEST": "song:request:",
	"STATION_EDIT": "station:edit:",
	"STATION_DELETE": "station:delete:",
	"USER_LIST": "user:list:",
	"USER_EDIT": "user:edit:",
};
