import { useMemo } from "react";

export const nameSortFn = (a,b) =>
	a.name > b.name ? 1 : a.name < b.name ? -1 : 0;

export const keyedSortFn = (key) => (a,b) =>
	a[key] > b[key] ? 1 : a[key] < b[key] ? -1 : 0;


export const useCombinedContextAndFormItems = (contextItems, fetchedItems) => {
	const combined = useMemo(() => {
		const missing = fetchedItems
			.filter(i => contextItems.every(c => c.id !== i.id) || !contextItems);
		return [...contextItems, ...missing].sort(nameSortFn);
	},[contextItems, fetchedItems]);

	return combined;
};