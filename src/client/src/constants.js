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
};

export const ApiRoutes = {
	queue: (stationName) => `api/${apiVersion}/stations/${stationName}/queue/`,
	history: (stationName) => 
		`api/${apiVersion}/stations/${stationName}/history/`,
	stations: () => `api/${apiVersion}/stations/`,
	songRequest: (stationName, songId) => 
		`api/${apiVersion}/stations/${stationName}/request/${songId}`,
	songCatalogue: (stationName) => 
		`api/${apiVersion}/stations/${stationName}/catalogue/`,
};