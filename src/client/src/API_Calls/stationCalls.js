import webClient from "./api";
import { buildArrayQueryStrFromObj } from "../Helpers/url_helpers";


export const fetchStations = async (params) => {
	const response = await webClient.get("stations/list", {
		params: {
			ownerKey: params?.ownerKey || undefined,
		},
	});
	return response.data;
};

export const fetchStationForEdit = async ({ ownerKey, stationKey }) => {
	const response = await webClient.get(`stations/${ownerKey}/${stationKey}/`);
	return response.data;
};

export const checkValues = async ({ values }) => {
	const response = await webClient.get("stations/check/", {
		params: values,
	});
	return response.data;
};

export const saveStation = async ({ values, id}) => {
	if(id) {
		const response = await webClient.put(`/stations/${id}`, values);
		return response.data;
	}
	else {
		const response = await webClient.post("stations", values);
		return response.data;
	}
};

export const fetchSongCatalogue = async ({
	stationKey,
	params,
	ownerKey,
}) => {
	const url = `stations/${ownerKey}/${stationKey}/catalogue/`;
	const response = await webClient.get(url, {
		params: params,
	});
	return response.data;
};

export const fetchQueue = async ({ stationKey, params, ownerKey }) => {
	const url = `stations/${ownerKey}/${stationKey}/queue/`;
	const response = await webClient.get(url, {
		params: params,
	});
	return response.data;
};

export const fetchHistory = async ({ stationKey, params, ownerKey }) => {
	const url = `stations/${ownerKey}/${stationKey}/history/`;
	const response = await webClient.get(url, {
		params: params,
	});
	return response.data;
};

export const sendSongRequest = async ({ station, songId}) => {
	const response = await webClient
		.post(`stations/${station}/request/${songId}`);
	return response.data;
};

export const removeSongFromQueue = async (params) => {
	const { stationName, songId, queuedTimestamp } = params;
	const response = await webClient
		.delete(`stations/${stationName}/request/`, {
			params: {
				id: songId,
				queuedTimestamp,
			},
		});
	return response.data;
};

export const enableStations = async ({ ids }) => {
	const queryStr = buildArrayQueryStrFromObj({"id": ids});
	const response = await webClient
		.put(`stations/enable/${queryStr}`);
	return response.data;
};

export const disableStations = async ({ ids, names }) => {
	const queryStr = buildArrayQueryStrFromObj({"id": ids, "name": names});
	const response = await webClient
		.put(`stations/disable/${queryStr}`);
	return response.data;
};

export const fetchStationUsers = async ({
	stationKey,
	params,
	ownerKey,
}) => {
	const url = `stations/${ownerKey}/${stationKey}/user_list/`;
	const response = await webClient.get(url, {
		params: params,
	});
	return response.data;
};

export const addStationUserRule = async ({
	ownerKey,
	stationKey,
	params,
	rule,
}) => {
	const url = `stations/${ownerKey}/${stationKey}/user_role/`;
	const response = await webClient.post(url, rule, {
		params: params,
	});
	return response.data;
};

export const removeStationUserRule = async ({
	ownerKey,
	stationKey,
	params,
}) => {
	const url = `stations/${ownerKey}/${stationKey}/user_role/`;
	const response = await webClient.delete(url, {
		params: params,
	});
	return response.data;
};