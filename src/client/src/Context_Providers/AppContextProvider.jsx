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
} from "../Components/Shared/waitingReducer";
import PropTypes from "prop-types";
import { fetchAlbumList, fetchArtistList } from "../API_Calls/songInfoCalls";
import { formatError } from "../Helpers/error_formatter";
import { fetchTags } from "../API_Calls/tagCalls";
import { CallStatus } from "../constants";

const AppContext = createContext();

const sortedListReducerPaths = {
	[waitingTypes.done]: (state, payload) => {
		const items = payload && payload.items ? payload.items
			.sort((a,b) => a.name > b.name ? 1 : a.name < b.name ? -1 : 0)
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
			.sort((a,b) => a.name > b.name ? 1 : a.name < b.name ? -1 : 0);
		return {
			...state,
			data: {
				items: items,
			},
		};
	},
};

export const AppContextProvider = (props) => {
	const { children } = props;
	const [albumsState, albumsDispatch] = useReducer(
		waitingReducer(sortedListReducerPaths),
		{...listDataInitialState}
	);

	const [tagsState, tagsDispatch] = useReducer(
		waitingReducer(sortedListReducerPaths),
		{...listDataInitialState}
	);

	const [artistState, artistDispatch] = useReducer(
		waitingReducer(sortedListReducerPaths),
		{...listDataInitialState}
	);

	useEffect(() => {
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
	},[albumsDispatch]);

	useEffect(() => {
		const fetch = async () => {
			try {
				tagsDispatch(dispatches.started());
				const data = await fetchTags();
				tagsDispatch(dispatches.done(data));
			}
			catch(err) {
				tagsDispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
	}, [tagsDispatch]);

	useEffect(() => {
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
	}, [artistDispatch]);

	const contextValue = useMemo(() => ({
		albumsState,
		albumsDispatch,
		tagsState,
		tagsDispatch,
		artistState,
		artistDispatch,
	}),[
		albumsState,
		tagsState,
		albumsState,
		albumsDispatch,
		artistState,
		tagsDispatch,
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

export const emptyValue = { id: 0, name: "" };

export const useAlbumData = () => {
	const {
		albumsState: { data: { items }, error, callStatus },
		albumsDispatch: dispatch,
	} = useContext(AppContext);

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

	const add = useCallback(
		(item) => dispatch(dispatches.add(item)),
		[dispatch]
	);

	return {
		items,
		error,
		callStatus,
		add,
		idMapper,
	};
};

export const useTagData = () => {
	const {
		tagsState: { data: { items }, error, callStatus },
		tagsDispatch: dispatch,
	} = useContext(AppContext);

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

	const add = useCallback(
		(item) => dispatch(dispatches.add(item)),
		[dispatch]
	);

	return {
		items,
		error,
		callStatus,
		add,
		idMapper,
	};
};

export const useArtistData = () => {
	const {
		artistState: { data: { items }, error, callStatus },
		artistDispatch: dispatch,
	} = useContext(AppContext);

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

	const add = useCallback(
		(item) => dispatch(dispatches.add(item)),
		[dispatch]
	);

	return {
		items,
		error,
		callStatus,
		add,
		idMapper,
	};
};