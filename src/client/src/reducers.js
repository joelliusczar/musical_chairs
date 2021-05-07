import queueReducer from "./Components/Queue/queue_state";
import stationsReducer from "./shared_api/stations_state";
import historyReducer from "./Components/History/history_state";
import { configureStore } from "@reduxjs/toolkit";
import logger from "redux-logger";


const reducer = {
  queue: queueReducer,
  stations: stationsReducer,
  history: historyReducer,
};


export default configureStore({reducer,
  middleware: (getDefault) => getDefault().concat(logger),
  devTools: process.env.NODE_ENV !== "production",
});