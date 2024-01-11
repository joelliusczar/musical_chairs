import { apiAddress, baseAddress } from "../constants";
import { StationInfo } from "../Types/station_types";
import { IdValue } from "../Types/generic_types";

export const buildArrayQueryStr = (key: string, arr: number[] | string[]) => {
	const queryObj = new URLSearchParams();
	for (const item of arr) {
		queryObj.append(key, item as string);
	}
	return `?${queryObj.toString()}`;
};

export const buildArrayQueryStrFromObj = (
	obj: {[key: string]: number | string | (number | string)[]}
): string => {
	const queryObj = new URLSearchParams();
	for (const key of Object.keys(obj)) {
		const value = obj[key];
		if (Array.isArray(value)) {
			for (const item of value) {
				queryObj.append(key, item as string);
			}
			continue;
		}
		if (typeof value === "string" || typeof value === "number") {
			queryObj.append(key, value as string);
		}
	}
	return `?${queryObj.toString()}`;
};

export const getListenAddress = (station: StationInfo) => {
	const stationName = `${station.owner?.username || ""}_${station.name}`;
	return `${baseAddress}/listen/stream/${stationName}`;
};

export const getDownloadAddress = (songId: IdValue) => {
	return `${apiAddress}/song-info/songs/download/${songId}`;
};