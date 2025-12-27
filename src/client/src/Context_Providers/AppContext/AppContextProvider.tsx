import React, {
	useMemo,
	useEffect,
} from "react";
import {
	dataDispatches as dispatches,
	useDataWaitingReducer,
} from "../../Reducers/dataWaitingReducer";
import PropTypes from "prop-types";
import { getList as fetchArtistList } from "../../API_Calls/artistCalls";
import { Calls as AlbumCalls } from "../../API_Calls/albumCalls";
import {
	Calls as PlaylistCalls,
} from "../../API_Calls/playlistCalls";
import { formatError } from "../../Helpers/error_formatter";
import { 
	Calls as StationCalls,
} from "../../API_Calls/stationCalls";
import { useCurrentUser } from "../AuthContext/AuthContext";
import {
	initialAlbumState,
	initialAlbumsSongsCountsState,
	initialArtistState,
	initialStationState,
	initialPlaylistsState,
	AppContext,
} from "./AppContext";



export const AppContextProvider = (props: { children: JSX.Element }) => {
	const { children } = props;
	const { access_token } = useCurrentUser();
	const loggedIn = !!access_token;

	const [albumsState, albumsDispatch] = useDataWaitingReducer(
		initialAlbumState
	);

	const [albumsSongsCountsState, albumsSongsCountsDispatch] 
	= useDataWaitingReducer(
		initialAlbumsSongsCountsState
	);

	const [stationsState, stationsDispatch] = useDataWaitingReducer(
		initialStationState
	);

	const [artistState, artistDispatch] = useDataWaitingReducer(
		initialArtistState
	);

	const [playlistsState, playlistsDispatch] = useDataWaitingReducer(
		initialPlaylistsState
	);

	useEffect(() => {
		if (!loggedIn) return;
		const requestObj = AlbumCalls.getList({});
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
		if (!loggedIn) return;
		const requestObj = AlbumCalls.songCounts();
		const fetch = async () => {
			try {
				albumsSongsCountsDispatch(dispatches.started());
				const data = await requestObj.call();
				albumsSongsCountsDispatch(dispatches.done(data));
			}
			catch(err) {
				albumsSongsCountsDispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
		return () => requestObj.abortController.abort();
	},[albumsSongsCountsDispatch, loggedIn]);

	useEffect(() => {
		const requestObj = StationCalls.getList();
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

	useEffect(() => {
		if (!loggedIn) return;
		const requestObj = PlaylistCalls.getList({});
		const fetch = async () => {
			try {
				playlistsDispatch(dispatches.started());
				const data = await requestObj.call();
				playlistsDispatch(dispatches.done(data));
			}
			catch(err) {
				playlistsDispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
		return () => requestObj.abortController.abort();
	}, [playlistsDispatch, loggedIn]);

	const contextValue = useMemo(() => ({
		albumsState,
		albumsDispatch,
		albumsSongsCountsState,
		albumsSongsCountsDispatch,
		stationsState,
		stationsDispatch,
		artistState,
		artistDispatch,
		playlistsState,
		playlistsDispatch,
	}),[
		albumsState,
		albumsDispatch,
		albumsSongsCountsState,
		albumsSongsCountsDispatch,
		artistState,
		artistDispatch,
		stationsState,
		stationsDispatch,
		playlistsState,
		playlistsDispatch,
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



