import { useMemo } from "react";
import {
	Named,
	NamedIdItem,
	SortCallback,
	SortCallbackFactory,
} from "../Types/generic_types";

export const nameSortFn: SortCallback<Named> = (a: Named,b: Named): number =>
	a.name > b.name ? 1 : a.name < b.name ? -1 : 0;


export const keyedSortFn: SortCallbackFactory =
	<T, K extends keyof T>(key: K) => ((a: T,b: T) =>
		a[key] > b[key] ? 1 : a[key] < b[key] ? -1 : 0);


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

export const notNullPredicate =
	<T>(value: T | null | undefined): value is T => {
		return value !== null && value !== undefined;
	};

export const  squash_sequential_duplicates = <T>(
	compressura: T[],
	pattern: T
) => {
	if (!compressura.length) {
		return [];
	}
	if (compressura.length === 1) {
		return [...compressura];
	}
	let previous = compressura[0];
	const result = [previous];
	for (let idx = 1; idx < compressura.length; idx++) {
		if (compressura[idx] === previous && compressura[idx] == pattern) {
			continue;
		}
		previous = compressura[idx];
		result.push(compressura[idx]);
	}

	return result;
};

export const squash_sequential_duplicate_chars = (
	compressura: string,
	pattern: string
) => {
	const arr = [...compressura];

	return squash_sequential_duplicates(arr, pattern).join("");
};