import React, {
	useCallback,
	useContext,
	createContext,
} from "react";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import {
	ListDataShape,
} from "../../Types/reducerTypes";
import { StationInfo } from "../../Types/station_types";
import { AlbumInfo, ArtistInfo } from "../../Types/song_info_types";
import {
	IdItem,
	SingleOrList,
	NamedIdItem,
} from "../../Types/generic_types";
import { nameSortFn } from "../../Helpers/array_helpers";
import {
	DataActionPayload as ActionPayload,
	dataDispatches as dispatches,
} from "../../Reducers/dataWaitingReducer";


type AppContextType = {
	albumsState: RequiredDataStore<ListDataShape<AlbumInfo>>,
	albumsDispatch: React.Dispatch<
		ActionPayload<ListDataShape<AlbumInfo>>
	>,
	stationsState: RequiredDataStore<ListDataShape<StationInfo>>,
	stationsDispatch: React.Dispatch<
		ActionPayload<ListDataShape<StationInfo>>
	>,
	artistState: RequiredDataStore<ListDataShape<ArtistInfo>>,
	artistDispatch: React.Dispatch<
		ActionPayload<ListDataShape<ArtistInfo>>
	>,
};

export const initialAlbumState =
	new RequiredDataStore<ListDataShape<AlbumInfo>>({ items: []});
export const initialStationState =
	new RequiredDataStore<ListDataShape<StationInfo>>({ items: []});
export const initialArtistState =
	new RequiredDataStore<ListDataShape<ArtistInfo>>({ items: []});

export const AppContext = createContext<AppContextType>({
	albumsState: initialAlbumState,
	albumsDispatch: ({ }) => {},
	stationsState: initialStationState,
	stationsDispatch: ({ }) => {},
	artistState: initialArtistState,
	artistDispatch: ({ }) => {},
});

const addItemToState = <T extends NamedIdItem>(
	state: RequiredDataStore<ListDataShape<T>>,
	item: T
) => {
	const items = [...state.data.items, item]
		.sort(nameSortFn);
	return {
		...state,
		data: {
			items: items,
		},
	};
};

const updateItemInState = <T extends NamedIdItem>(
	state: RequiredDataStore<ListDataShape<T>>,
	item: T
) => {
	const items = [...state.data.items];
	const idx = items.findIndex(i => i.id === item.id);
	if (idx > -1) {
		items[idx] = item;
		return {
			...state,
			data: {
				items: items,
			},
		};
	}
	console.error("Item was not found in local store.");
	return state;
};

const removeItemInState = <T extends NamedIdItem>(
	state: RequiredDataStore<ListDataShape<T>>,
	item: T
) => {
	const items = [...state.data.items];
	const idx = items.findIndex(i => i.id === item.id);
	if (idx > -1) {
		items.splice(idx, 1);
		return {
			...state,
			data: {
				items: items,
			},
		};
	}
	console.error("Item was not found in local store.");
	return state;
};


export const useAlbumData = () => {
	const {
		albumsState: { data: { items }, error, callStatus },
		albumsDispatch: dispatch,
	} = useContext(AppContext);

	const add = useCallback(
		(item: AlbumInfo) => 
			dispatch(dispatches.update(state => {
				return addItemToState(state, item);
			})),
		[dispatch]
	);

	const update = useCallback((item: AlbumInfo) => 
		dispatch(dispatches.update((state) => {
			return updateItemInState(state, item);
		})),
	[dispatch]
	);

	const remove = useCallback((item: AlbumInfo) => {
		dispatch(dispatches.update((state) => {
			return removeItemInState(state, item);
		}));
	},[dispatch]);

	return {
		items,
		error,
		callStatus,
		add,
		update,
		remove,
	};
};


export const useStationData = () => {
	const {
		stationsState: { data: { items }, error, callStatus },
		stationsDispatch: dispatch,
	} = useContext(AppContext);

	const add = useCallback((item: StationInfo) => 
		dispatch(dispatches.update(state => {
			return addItemToState(state, item);
		})),
	[dispatch]
	);

	const update = useCallback((item: StationInfo) =>
		dispatch(dispatches.update((state) => {
			return updateItemInState(state, item);
		})),
	[dispatch]
	);

	const remove = useCallback((item: StationInfo) => {
		dispatch(dispatches.update((state) => {
			return removeItemInState(state, item);
		}));
	},[dispatch]);

	return {
		items,
		error,
		callStatus,
		add,
		update,
		remove,
	};
};

export const useArtistData = () => {
	const {
		artistState: { data: { items }, error, callStatus },
		artistDispatch: dispatch,
	} = useContext(AppContext);

	const add = useCallback((item: ArtistInfo) => 
		dispatch(dispatches.update(state => {
			return addItemToState(state, item);
		})),
	[dispatch]
	);

	const update = useCallback((item: ArtistInfo) =>
		dispatch(dispatches.update((state) => {
			return updateItemInState(state, item);
		})),
	[dispatch]
	);

	const remove = useCallback((item: ArtistInfo) => {
		dispatch(dispatches.update((state) => {
			return removeItemInState(state, item);
		}));
	},[dispatch]);


	return {
		items,
		error,
		callStatus,
		add,
		update,
		remove,
	};
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