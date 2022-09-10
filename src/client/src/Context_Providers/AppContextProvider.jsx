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
import { fetchAlbumList } from "../API_Calls/songInfoCalls";
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

	const [tagState, tagsDispatch] = useReducer(
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

	const addTag = useCallback(
		(tag) => tagsDispatch(dispatches.add(tag)),
		[tagsDispatch]
	);

	const addAlbum = useCallback(
		(album) => albumsDispatch(dispatches.add(album)),
		[albumsDispatch]
	);

	const contextValue = useMemo(() => ({
		albumsState,
		addAlbum,
		tagsState: tagState,
		addTag,
	}),[albumsState, tagState, addTag, addAlbum]);

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

export const useAlbumData = () => {
	const { albumsState, addAlbum } = useContext(AppContext);
	return {
		items: albumsState.data.items,
		callStatus: albumsState.callStatus,
		add: addAlbum,
	};
};

export const useTagData = () => {
	const { tagsState, addTag } = useContext(AppContext);
	console.log(tagsState);
	return {
		items: tagsState.data.items,
		error: tagsState.error,
		callStatus: tagsState.callStatus,
		add: addTag,
	};
};