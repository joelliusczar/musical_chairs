import { useMemo } from "react";
import {
	Named,
	NamedIdItem,
	Keyed,
	SortCallback,
	SortCallbackFactory
} from "../Types/generic_types";

export const nameSortFn: SortCallback<Named> = (a: Named,b: Named): number =>
	a.name > b.name ? 1 : a.name < b.name ? -1 : 0;


export const keyedSortFn: SortCallbackFactory =
	(key: string) => ((a: Keyed,b: Keyed) =>
		a[key] > b[key] ? 1 : a[key] < b[key] ? -1 : 0) as (a:{}, b:{}) => number;


export const useCombinedContextAndFormItems = <T extends NamedIdItem>(
	contextItems: T[],
	fetchedItems: T[]
): T[] => {
	const combined = useMemo(() => {
		const missing = fetchedItems
			.filter(i => contextItems.every(c => c.id !== i.id) || !contextItems);
		return [...contextItems, ...missing].sort(nameSortFn);
	},[contextItems, fetchedItems]);

	return combined;
};