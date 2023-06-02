import React, {
	createContext,
	useMemo,
	useEffect,
	useReducer,
	useContext,
	useCallback,
} from "react";
import {
	waitingReducer,
	listDataInitialState,
	dispatches,
	waitingTypes,
	globalStoreLogger,
} from "../Components/Shared/waitingReducer";
import PropTypes from "prop-types";
import { fetchAlbumList, fetchArtistList } from "../API_Calls/songInfoCalls";
import { formatError } from "../Helpers/error_formatter";
import { fetchStations } from "../API_Calls/stationCalls";
import { CallStatus } from "../constants";
import { useCurrentUser } from "./AuthContext";
import { nameSortFn } from "../Helpers/array_helpers";

const AppContext = createContext();


const sortedListReducerPaths = {
	[waitingTypes.done]: (state, payload) => {
		const items = payload && payload.items ? payload.items
			.sort(nameSortFn)
			: [];
		return {
			...state,
			data: {
				items: items,
			},
			callStatus: CallStatus.done,
		};
	},
	[waitingTypes.add]: (state, payload) => {
		const items = [...state.data.items, payload]
			.sort(nameSortFn);
		return {
			...state,
			data: {
				items: items,
			},
		};
	},
	[waitingTypes.update]: (state, payload) => {
		const { key, dataOrUpdater } = payload;
		const items = [...state.data.items];
		const idx = items.findIndex(x => x.id === (key * 1));
		if (idx > -1) {
			if (typeof dataOrUpdater === "function") {
				items.splice(idx, 1, dataOrUpdater(items[idx]));
			}
			else {
				items.splice(idx, 1, dataOrUpdater);
			}
			const sortedItems = items.sort(nameSortFn);
			return {
				...state,
				data: {
					items: sortedItems,
				},
			};
		}
		else {
			console.error("Item was not found in local store.");
		}
	},
};

export const AppContextProvider = (props) => {
	const { children } = props;
	const { username } = useCurrentUser();

	const [albumsState, albumsDispatch] = useReducer(
		waitingReducer(sortedListReducerPaths),
		{...listDataInitialState}
	);

	const [stationsState, stationsDispatch] = useReducer(
		waitingReducer(sortedListReducerPaths, [(globalStoreLogger("Stations"))]),
		{...listDataInitialState}
	);

	const [artistState, artistDispatch] = useReducer(
		waitingReducer(sortedListReducerPaths),
		{...listDataInitialState}
	);

	useEffect(() => {
		if (!username) return;
		const fetch = async () => {
			try {
				albumsDispatch(dispatches.started());
				const data = await fetchAlbumList({});
				albumsDispatch(dispatches.done(data));
			}
			catch(err) {
				albumsDispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
	},[albumsDispatch, username]);

	useEffect(() => {
		if (!username) return;
		const fetch = async () => {
			try {
				stationsDispatch(dispatches.started());
				const data = await fetchStations({ ownerKey: username });
				stationsDispatch(dispatches.done(data));
			}
			catch(err) {
				stationsDispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
	}, [stationsDispatch, username]);

	useEffect(() => {
		if (!username) return;
		const fetch = async () => {
			try {
				artistDispatch(dispatches.started());
				const data = await fetchArtistList({});
				artistDispatch(dispatches.done(data));
			}
			catch(err) {
				artistDispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
	}, [artistDispatch, username]);

	const contextValue = useMemo(() => ({
		albumsState,
		albumsDispatch,
		stationsState,
		stationsDispatch,
		artistState,
		artistDispatch,
	}),[
		albumsState,
		stationsState,
		albumsState,
		albumsDispatch,
		artistState,
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

export const useIdMapper = (items) => {
	const idMapper = useCallback((value) => {
		if(!value) return value;
		if(Array.isArray(value)) {
			return value.map((item) =>
				items.find(x => x.id === item.id));
		}
		if (typeof(value) === "object") {
			return items.find(x => x.id === value.id) || null;
		}
	},[items]);
	return idMapper;
};

export const emptyValue = { id: 0, name: "" };

export const useAlbumData = () => {
	const {
		albumsState: { data: { items }, error, callStatus },
		albumsDispatch: dispatch,
	} = useContext(AppContext);

	const add = useCallback(
		(item) => dispatch(dispatches.add(item)),
		[dispatch]
	);

	const update = useCallback(
		(key, item) => dispatch(dispatches.update(key, item)),
		[dispatch]
	);

	return {
		items,
		error,
		callStatus,
		add,
		update,
	};
};

export const useStationData = () => {
	const {
		stationsState: { data: { items }, error, callStatus },
		stationsDispatch: dispatch,
	} = useContext(AppContext);

	const add = useCallback(
		(item) => dispatch(dispatches.add(item)),
		[dispatch]
	);

	const update = useCallback(
		(key, item) => dispatch(dispatches.update(key, item)),
		[dispatch]
	);

	return {
		items,
		error,
		callStatus,
		add,
		update,
	};
};

export const useArtistData = () => {
	const {
		artistState: { data: { items }, error, callStatus },
		artistDispatch: dispatch,
	} = useContext(AppContext);

	const add = useCallback(
		(item) => dispatch(dispatches.add(item)),
		[dispatch]
	);

	const update = useCallback(
		(key, item) => dispatch(dispatches.update(key, item)),
		[dispatch]
	);

	return {
		items,
		error,
		callStatus,
		add,
		update,
	};
};