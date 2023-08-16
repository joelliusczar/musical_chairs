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
	dispatches,
} from "../Components/Shared/waitingReducer";
import PropTypes from "prop-types";
import { fetchAlbumList, fetchArtistList } from "../API_Calls/songInfoCalls";
import { formatError } from "../Helpers/error_formatter";
import { fetchStations } from "../API_Calls/stationCalls";
import { CallStatus } from "../constants";
import { useCurrentUser } from "./AuthContext";
import { nameSortFn } from "../Helpers/array_helpers";
import {
	ListStore,
	ListDataShape,
	KeyAndDataOrUpdater,
	WaitingTypes,
	DataOrUpdater,
	RequiredDataState
} from "../Types/reducer_types";
import {
	IdItem,
	IdType,
	NamedIdItem,
	SingleOrList
} from "../Types/generic_types";
import { StationInfo } from "../Types/station_types";
import { AlbumInfo, ArtistInfo } from "../Types/song_info_types";

const initialAlbumState =
	new RequiredDataState<ListDataShape<AlbumInfo>>({ items: []});
const initialStationState =
	new RequiredDataState<ListDataShape<StationInfo>>({ items: []});
const initialArtistState =
	new RequiredDataState<ListDataShape<ArtistInfo>>({ items: []});

const AppContext = createContext<{
	albumsState: RequiredDataState<ListDataShape<AlbumInfo>>,
	albumsDispatch: React.Dispatch<{ type: WaitingTypes, payload: any}>,
	stationsState: RequiredDataState<ListDataShape<StationInfo>>,
	stationsDispatch: React.Dispatch<{ type: WaitingTypes, payload: any}>,
	artistState: RequiredDataState<ListDataShape<ArtistInfo>>,
	artistDispatch: React.Dispatch<{ type: WaitingTypes, payload: any}>,
}>({
	albumsState: initialAlbumState,
	albumsDispatch: ({ type: WaitingTypes, payload: any}) => {},
	stationsState: initialStationState,
	stationsDispatch: ({ type: WaitingTypes, payload: any}) => {},
	artistState: initialArtistState,
	artistDispatch: ({ type: WaitingTypes, payload: any}) => {},
});


class SortedListReducerPaths<DataShape extends NamedIdItem> {
	done(state: ListStore<DataShape>, payload: ListDataShape<DataShape>) {
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
	}
	add(state: ListStore<DataShape>, payload: DataShape) {
		const items = [...state.data.items, payload]
			.sort(nameSortFn);
		return {
			...state,
			data: {
				items: items,
			},
		};
	}
	update(
		state: ListStore<DataShape>,
		payload: KeyAndDataOrUpdater<DataShape>
	) {
		const { key, dataOrUpdater } = payload;
		const items = [...state.data.items];
		const idx = items.findIndex(x => x.id === (parseInt(key)));
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
	}
};

export const AppContextProvider = (props: { children: JSX.Element }) => {
	const { children } = props;
	const { username } = useCurrentUser();

	const [albumsState, albumsDispatch] = useReducer(
		waitingReducer(new SortedListReducerPaths<AlbumInfo>()),
		initialAlbumState
	);

	const [stationsState, stationsDispatch] = useReducer(
		waitingReducer(new SortedListReducerPaths<StationInfo>()),
		initialStationState
	);

	const [artistState, artistDispatch] = useReducer(
		waitingReducer(new SortedListReducerPaths<ArtistInfo>()),
		initialArtistState
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