import historyReducer from "./Components/History/history_slice";
import accountsReducer from "./API_Calls/userCalls";
import { configureStore } from "@reduxjs/toolkit";
import logger from "redux-logger";


const reducer = {
	history: historyReducer,
	accounts: accountsReducer,
};


export default configureStore({reducer,
	middleware: (getDefault) => getDefault()
		.concat(logger),
	devTools: process.env.NODE_ENV !== "production",
});