import queueReducer from "./Components/Queue/queue_slice";
import stationsReducer from "./Components/Stations/stations_slice";
import historyReducer from "./Components/History/history_slice";
import { configureStore } from "@reduxjs/toolkit";
import logger from "redux-logger";


const reducer = {
  queue: queueReducer,
  stations: stationsReducer,
  history: historyReducer,
};


export default configureStore({reducer,
  middleware: (getDefault) => getDefault()
    .concat(logger),
  devTools: process.env.NODE_ENV !== "production",
});