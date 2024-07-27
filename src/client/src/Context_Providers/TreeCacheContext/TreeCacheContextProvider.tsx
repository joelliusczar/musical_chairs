import React,
{
	useCallback,
	useMemo,
	useState,
} from "react";
import {
	keyedDataDispatches as dispatches,
	useKeyedDataWaitingReducer,
} from "../../Reducers/keyedDataWaitingReducer";
import { TreeCacheContext } from "./TreeCacheContext";
import { Dictionary } from "../../Types/generic_types";
import { 
	normalizeOpeningSlash,
} from "../../Helpers/string_helpers";




type CacheContextProviderProps = {
	children?: JSX.Element | JSX.Element[]
};


export const CacheContextProvider = <T,>(props: CacheContextProviderProps) => {
	const { children } = props;
	const [state, dispatch] = useKeyedDataWaitingReducer<T>();
	const [expandedNodes, setExpandedNodes] = useState<
			string[]
		>([]); 

	const treeData = useMemo(() => {
		const data: Dictionary<T | null> = {};
		Object.keys(state).forEach((key) => {
			data[key] =  state[key].data;
		});
		return data;
	}, [state]);

	const updateTree = useCallback((nodes: Dictionary<T>) => {
		Object.keys(nodes).forEach(key => {
			dispatch(dispatches.done({
				[normalizeOpeningSlash(key)]: nodes[key],
			}));
		});
	},[dispatch]);

	const contextValue = useMemo(() => ({
		state, 
		dispatch, 
		treeData, 
		updateTree,
		setExpandedNodes,
		expandedNodes,
	}),[
		state,
		dispatch,
		treeData,
		updateTree,
		setExpandedNodes,
		expandedNodes,
	]);

	return (
		<TreeCacheContext.Provider value={contextValue}>
			{children}
		</TreeCacheContext.Provider>
	);

};


