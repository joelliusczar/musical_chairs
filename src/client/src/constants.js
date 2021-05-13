export const apiAddress = process.env.REACT_APP_API_ADDRESS;

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
  queue: (stationName) => `api/stations/${stationName}/queue/`,
  history: (stationName) => `api/stations/${stationName}/history/`,
  stations: () => "api/stations/",
  songRequest: (stationName, songId) => 
    `api/stations/${stationName}/request/${songId}`,
  songCatalogue: (stationName) => `api/stations/${stationName}/song-catalogue/`,
};