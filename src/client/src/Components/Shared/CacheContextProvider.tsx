import React,
{
	createContext,
	useState,
	useCallback,
	useMemo,
	useContext,
	ComponentType,
} from "react";
import { KeyType } from "../../Types/generic_types";

const defaultKey = "__mc_cache_default__";


type CacheContextType<T> = {
	[key: KeyType]: {
		getCacheValue: (key: KeyType, defaultValue?: T | null) => T | null,
		setCacheValue: (key: KeyType, value: T) => void
	}
};

type CacheContextProviderProps = {
	children?: JSX.Element | JSX.Element[]
	key?: KeyType
};

const CacheContext = createContext({});

export const CacheContextProvider = <T,>(props: CacheContextProviderProps) => {
	const { children, key } = props;
	const [cache, setCache] = useState<{ [key: KeyType]: T}>({});
	const cacheKey = key || defaultKey;

	const setCacheValue = useCallback((key: KeyType, value: T) => {
		setCache(m => ({...m, [key]: value}));
	},[setCache]);

	const getCacheValue = useCallback((key: KeyType, defaultValue = null) => {
		return key in cache ? cache[key] : defaultValue;
	},[cache]);

	const existingCaches = useContext<CacheContextType<T>>(CacheContext);


	const contextValue = useMemo(() => ({
		...existingCaches,
		[cacheKey]: { getCacheValue, setCacheValue},
	}),[existingCaches, cacheKey, getCacheValue, setCacheValue]);

	return (
		<CacheContext.Provider value={contextValue}>
			{children}
		</CacheContext.Provider>
	);

};


export const useCache = <T,>(key?: KeyType) => {
	const existingCaches = useContext<CacheContextType<T>>(CacheContext);
	const cacheKey = key || defaultKey;
	return existingCaches[cacheKey];
};

export const withCacheProvider =
	<WrappedPropsType,CachedPropTypes>(key?: KeyType) => {
		const componentReceiver = (
			WrappedComponent: ComponentType<WrappedPropsType>
		) => {
			const wrappingFn = (props: WrappedPropsType) => {
				return (
					<CacheContextProvider<CachedPropTypes> key={key}>
						<WrappedComponent {...props} cacheKey={key} />
					</CacheContextProvider>
				);
			};
			return wrappingFn;
		};
		return componentReceiver;
	};