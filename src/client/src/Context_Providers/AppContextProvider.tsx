import React, {
	createContext,
	useMemo,
	useEffect,
	useContext,
	useCallback,
} from "react";
import {
	dispatches,
	useWaitingReducer,
} from "../Reducers/waitingReducer";
import PropTypes from "prop-types";
import { fetchAlbumList, fetchArtistList } from "../API_Calls/songInfoCalls";
import { formatError } from "../Helpers/error_formatter";
import { fetchStations } from "../API_Calls/stationCalls";
import { useCurrentUser } from "./AuthContext";
import { CallStatus } from "../constants";
import {
	ListDataShape,
	DataOrUpdater,
	ListStoreShape,
	KeyAndDataOrUpdater,
	ActionPayload,
	WaitingTypes,
} from "../Reducers/types/reducerTypes";
import { RequiredDataStore } from "../Reducers/reducerStores";
import {
	IdItem,
	IdType,
	SingleOrList,
	NamedIdItem,
} from "../Types/generic_types";
import { StationInfo } from "../Types/station_types";
import { AlbumInfo, ArtistInfo } from "../Types/song_info_types";
import { nameSortFn } from "../Helpers/array_helpers";

export const constructSortedListReducerPaths =
	<DataShape extends NamedIdItem>() => {
		return {
			[WaitingTypes.done]: (
				state: ListStoreShape<DataShape>,
				payload?: ListDataShape<DataShape>
			) => {
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
			[WaitingTypes.add]: (
				state: ListStoreShape<DataShape>,
				payload: DataShape
			) => {
				const items = [...state.data.items, payload]
					.sort(nameSortFn);
				return {
					...state,
					data: {
						items: items,
					},
				};
			},
			[WaitingTypes.updateItem]:(
				state: ListStoreShape<DataShape>,
				payload: KeyAndDataOrUpdater<DataShape>
			) => {
				const { key, dataOrUpdater } = payload;
				const items = [...state.data.items];
				const idx = items.findIndex(x => x.id === (+key * 1));
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
					return state;
				}
			},
		};

	};



const initialAlbumState =
	new RequiredDataStore<ListDataShape<AlbumInfo>>({ items: []});
const initialStationState =
	new RequiredDataStore<ListDataShape<StationInfo>>({ items: []});
const initialArtistState =
	new RequiredDataStore<ListDataShape<ArtistInfo>>({ items: []});

type AppContextType = {
	albumsState: RequiredDataStore<ListDataShape<AlbumInfo>>,
	albumsDispatch: React.Dispatch<
		ActionPayload<ListDataShape<AlbumInfo>, AlbumInfo>
	>,
	stationsState: RequiredDataStore<ListDataShape<StationInfo>>,
	stationsDispatch: React.Dispatch<
		ActionPayload<ListDataShape<StationInfo>, StationInfo>
	>,
	artistState: RequiredDataStore<ListDataShape<ArtistInfo>>,
	artistDispatch: React.Dispatch<
		ActionPayload<ListDataShape<ArtistInfo>, ArtistInfo>
	>,
};

const AppContext = createContext<AppContextType>({
	albumsState: initialAlbumState,
	albumsDispatch: ({ }) => {},
	stationsState: initialStationState,
	stationsDispatch: ({ }) => {},
	artistState: initialArtistState,
	artistDispatch: ({ }) => {},
});




export const AppContextProvider = (props: { children: JSX.Element }) => {
	const { children } = props;
	const { username } = useCurrentUser();

	const [albumsState, albumsDispatch] = useWaitingReducer(
		initialAlbumState,
		{ reducerMods: constructSortedListReducerPaths()}
	);

	const [stationsState, stationsDispatch] = useWaitingReducer(
		initialStationState,
		{ reducerMods: constructSortedListReducerPaths()}
	);

	const [artistState, artistDispatch] = useWaitingReducer(
		initialArtistState,
		{ reducerMods: constructSortedListReducerPaths()}
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
		const fetch = async () => {
			try {
				stationsDispatch(dispatches.started());
				const data = await fetchStations();
				stationsDispatch(dispatches.done(data));
			}
			catch(err) {
				stationsDispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
	}, [stationsDispatch]);

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

export const useIdMapper = <T extends IdItem>(items: T[]) => {
	const idMapper =
		<InT extends T | T[] | null,>(value: InT): SingleOrList<T, InT> => {
			if(!value) return null as SingleOrList<T, InT>;
			if(Array.isArray(value)) {
				return value.map((item) =>
					items.find(x => x.id === item.id)
				).filter(x => !!x) as SingleOrList<T, InT>;
			}
			if (typeof(value) === "object") {
				const matches = items.find(x => x.id === value.id) || null;
				if (matches) {
					return matches as SingleOrList<T, InT>;
				}
			}
			return null as SingleOrList<T, InT>;
		};
	return idMapper;
};

export const emptyValue = { id: 0, name: "" };

export const useAlbumData = () => {
	const {
		albumsState: { data: { items }, error, callStatus },
		albumsDispatch: dispatch,
	} = useContext(AppContext);

	const add = useCallback(
		(item: AlbumInfo) => dispatch(dispatches.add(item)),
		[dispatch]
	);

	const update = useCallback(
		(
			key: IdType,
			item: DataOrUpdater<AlbumInfo>
		) => dispatch(dispatches.update(key, item)),
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
		(item: StationInfo) => dispatch(dispatches.add(item)),
		[dispatch]
	);

	const update = useCallback(
		(
			key: IdType,
			item: DataOrUpdater<StationInfo>
		) => dispatch(dispatches.update(key, item)),
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
		(item: ArtistInfo) => dispatch(dispatches.add(item)),
		[dispatch]
	);

	const update = useCallback(
		(
			key: IdType,
			item: DataOrUpdater<ArtistInfo>
		) => dispatch(dispatches.update(key, item)),
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