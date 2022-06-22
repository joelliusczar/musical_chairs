import queueReducer from "./Components/Queue/queue_slice";
import historyReducer from "./Components/History/history_slice";
import songCatalogueReducer 
	from "./Components/Song_Catalogue/song_catalogue_slice";
import accountsReducer from "./Components/Accounts/accounts_slice";
import { configureStore } from "@reduxjs/toolkit";
import logger from "redux-logger";


const reducer = {
	queue: queueReducer,
	history: historyReducer,
	songCatalogue: songCatalogueReducer,
	accounts: accountsReducer,
};


export default configureStore({reducer,
	middleware: (getDefault) => getDefault()
		.concat(logger),
	devTools: process.env.NODE_ENV !== "production",
});