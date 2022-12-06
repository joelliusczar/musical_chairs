import webClient from "./api";
import { buildArrayQueryStrFromObj } from "../Helpers/url_helpers";


export const fetchStations = async () => {
	const response = await webClient.get("stations/list");
	return response.data;
};

export const fetchStationForEdit = async ({ params }) => {
	const response = await webClient.get("stations", {
		params: params,
	});
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
		const response = await webClient.put("stations", values, {
			params: {
				id,
			},
		});
		return response.data;
	}
	else {
		const response = await webClient.post("stations", values);
		return response.data;
	}
};

export const fetchSongCatalogue = async ({ station, params }) => {
	const response = await webClient.get(`stations/${station}/catalogue/`, {
		params: params,
	});
	return response.data;
};

export const fetchQueue = async ({ station, params }) => {
	const response = await webClient.get(`stations/${station}/queue/`, {
		params: params,
	});
	return response.data;
};

export const fetchHistory = async ({ station, params }) => {
	const response = await webClient.get(`stations/${station}/history/`, {
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