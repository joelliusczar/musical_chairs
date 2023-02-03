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
	queue: "/queue/",
	history: "/history/",
	stations: "/stations/list/",
	stationsEdit: "/stations/edit/",
	songEdit: "/songs/edit/",
	songCatalogue: "/song-catalogue/",
	songTree: "/song-info/tree/",
	accountsNew: "/accounts/new",
	accountsEdit: "/accounts/edit",
	accountsLogin: "/accounts/login",
	accountsRoles: "/accounts/roles/",
	accountsList: "/accounts/list",
	notFound: "/not-found",
};

export const UserRoleDef = {
	"ADMIN": "admin",
	"SONG_EDIT": "song:edit",
	"SONG_DOWNLOAD": "song:download",
	"SONG_TREE_LIST": "songtree:list",
	"STATION_EDIT": "station:edit",
	"STATION_DELETE": "station:delete",
	"STATION_REQUEST": "station:request",
	"STATION_FLIP": "station:flip",
	"STATION_SKIP": "station:skip",
	"USER_LIST": "user:list",
	"USER_EDIT": "user:edit",
};
