import React,
{
	ComponentType,
} from "react";
import { CacheContextProvider } from "./TreeCacheContextProvider";


export const withCacheProvider =
	<WrappedPropsType,CachedPropTypes>() => {
		const componentReceiver = (
			WrappedComponent: ComponentType<WrappedPropsType>
		) => {
			const wrappingFn = (props: WrappedPropsType) => {
				return (
					<CacheContextProvider<CachedPropTypes> >
						<WrappedComponent  key="wtf" {...props} />
					</CacheContextProvider>
				);
			};
			return wrappingFn;
		};
		return componentReceiver;
	};