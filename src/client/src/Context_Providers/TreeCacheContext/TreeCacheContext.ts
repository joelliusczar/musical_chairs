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
	treeData: Dictionary<T>
};

export const TreeCacheContext = createContext({
	state: {},
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	dispatch: ((any: any) => any),
	treeData: {},
});


export const useCache = <T,>() => {
	const cacheContext = useContext<TreeCacheContextType<T>>(TreeCacheContext);
	return cacheContext;
};
