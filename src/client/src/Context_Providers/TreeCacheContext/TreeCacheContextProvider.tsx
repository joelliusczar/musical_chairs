import React,
{
	useMemo,
} from "react";
import {
	useKeyedDataWaitingReducer,
} from "../../Reducers/keyedDataWaitingReducer";
import { TreeCacheContext } from "./TreeCacheContext";
import { Dictionary } from "../../Types/generic_types";



type CacheContextProviderProps = {
	children?: JSX.Element | JSX.Element[]
};


export const CacheContextProvider = <T,>(props: CacheContextProviderProps) => {
	const { children } = props;
	const [state, dispatch] = useKeyedDataWaitingReducer<T>();

	const treeData = useMemo(() => {
		const data: Dictionary<T | null> = {};
		Object.keys(state).forEach((key) => {
			data[key] =  state[key].data;
		});
		return data;
	}, [state]);

	const contextValue = useMemo(() => ({
		state, dispatch, treeData,
	}),[
		state,
		dispatch,
		treeData,
	]);

	return (
		<TreeCacheContext.Provider value={contextValue}>
			{children}
		</TreeCacheContext.Provider>
	);

};


