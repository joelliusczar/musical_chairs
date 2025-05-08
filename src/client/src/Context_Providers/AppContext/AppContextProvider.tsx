import React, {
	useMemo,
	useEffect,
} from "react";
import {
	dataDispatches as dispatches,
	useDataWaitingReducer,
} from "../../Reducers/dataWaitingReducer";
import PropTypes from "prop-types";
import { fetchArtistList } from "../../API_Calls/songInfoCalls";
import { getList as fetchAlbumList } from "../../API_Calls/albumCalls";
import { formatError } from "../../Helpers/error_formatter";
import { fetchStations } from "../../API_Calls/stationCalls";
import { useCurrentUser } from "../AuthContext/AuthContext";
import {
	initialAlbumState,
	initialArtistState,
	initialStationState,
	AppContext,
} from "./AppContext";



export const AppContextProvider = (props: { children: JSX.Element }) => {
	const { children } = props;
	const { access_token } = useCurrentUser();
	const loggedIn = !!access_token;

	const [albumsState, albumsDispatch] = useDataWaitingReducer(
		initialAlbumState
	);

	const [stationsState, stationsDispatch] = useDataWaitingReducer(
		initialStationState
	);

	const [artistState, artistDispatch] = useDataWaitingReducer(
		initialArtistState
	);

	useEffect(() => {
		if (!loggedIn) return;
		const requestObj = fetchAlbumList({});
		const fetch = async () => {
			try {
				albumsDispatch(dispatches.started());
				const data = await requestObj.call();
				albumsDispatch(dispatches.done(data));
			}
			catch(err) {
				albumsDispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
		return () => requestObj.abortController.abort();
	},[albumsDispatch, loggedIn]);

	useEffect(() => {
		const requestObj = fetchStations();
		const fetch = async () => {
			try {
				stationsDispatch(dispatches.started());
				const data = await requestObj.call();
				stationsDispatch(dispatches.done(data));
			}
			catch(err) {
				stationsDispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
		return () => requestObj.abortController.abort();
	}, [stationsDispatch]);

	useEffect(() => {
		if (!loggedIn) return;
		const requestObj = fetchArtistList({});
		const fetch = async () => {
			try {
				artistDispatch(dispatches.started());
				const data = await requestObj.call();
				artistDispatch(dispatches.done(data));
			}
			catch(err) {
				artistDispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
		return () => requestObj.abortController.abort();
	}, [artistDispatch, loggedIn]);

	const contextValue = useMemo(() => ({
		albumsState,
		albumsDispatch,
		stationsState,
		stationsDispatch,
		artistState,
		artistDispatch,
	}),[
		stationsState,
		albumsState,
		albumsDispatch,
		artistState,
		artistDispatch,
		stationsDispatch,
	]);

	return <AppContext.Provider value={contextValue}>
		{children}
	</AppContext.Provider>;
};

AppContextProvider.propTypes = {
	children: PropTypes.oneOfType([
		PropTypes.arrayOf(PropTypes.node),
		PropTypes.node,
	]).isRequired,
};



