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
	stations: "/stations/",
	songCatalogue: "/song-catalogue/",
	accountsEdit: "/accounts/edit",
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
	"SONG_ADD": "song:add:",
	"SONG_REQUEST": "song:request:",
	"USER_LIST": "user:list:",
};