import React,
{
	createContext,
	useState,
	useCallback,
	useMemo,
	useContext,
} from "react";
import PropTypes from "prop-types";

const defaultKey = "__mc_cache_default__";
const emptyCache = {};

const CacheContext = createContext();

export const CacheContextProvider = (props) => {
	const { children, key } = props;
	const [cache, setCache] = useState({});
	const cacheKey = key || defaultKey;

	const setCacheValue = useCallback((key, value) => {
		setCache(m => ({...m, [key]: value}));
	},[setCache]);

	const getCacheValue = useCallback((key, defaultValue = null) => {
		return key in cache ? cache[key] : defaultValue;
	},[cache]);

	const existingCaches = useContext(CacheContext) || emptyCache;

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

CacheContextProvider.propTypes = {
	children: PropTypes.oneOfType([
		PropTypes.arrayOf(PropTypes.node),
		PropTypes.node,
	]).isRequired,
	key: PropTypes.string,
};

export const useCache = (key) => {
	const existingCaches = useContext(CacheContext);
	const cacheKey = key || defaultKey;
	return existingCaches[cacheKey];
};

export const withCacheProvider = (key) => {
	const componentReceiver = (WrappedComponent) => {
		const wrappingFn = (props) => {
			return (
				<CacheContextProvider>
					<WrappedComponent {...props} cacheKey={key} />
				</CacheContextProvider>
			);
		};
		return wrappingFn;
	};
	return componentReceiver;
};