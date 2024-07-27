import React,
{
	createContext,
	useContext,
} from "react";
import { Dictionary } from "../../Types/generic_types";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import {
	KeyedDataActionPayload,
} from "../../Reducers/keyedDataWaitingReducer";

type TreeCacheContextType<T> = {
	state: Dictionary<RequiredDataStore<T | null>>,
	dispatch: React.Dispatch<KeyedDataActionPayload<T>>,
	treeData: Dictionary<T>,
	updateTree: (nodes: Dictionary<T>) => void,
	setExpandedNodes: React.Dispatch<
		React.SetStateAction<string[]>
	>,
	expandedNodes: string[],
};

export const TreeCacheContext = createContext({
	state: {},
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	dispatch: ((any: any) => any),
	treeData: {},
	// eslint-disable-next-line max-len
	// eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars
	updateTree: (_: Dictionary<any>) => {},
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	setExpandedNodes: ((any: any) => any),
	expandedNodes: [] as string[],
});


export const useTree = <T,>() => {
	const cacheContext = useContext<TreeCacheContextType<T>>(TreeCacheContext);
	return cacheContext;
};
