import webClient from "./api";
import { buildArrayQueryStrFromObj } from "../Helpers/url_helpers";
import { OwnerParam, KeyType, IdType } from "../Types/generic_types";
import {
	RequiredStationParams,
	StationCreationInfo,
	StationInfo,
	StationTableData,
	StationRuleAddition,
	StationRuleDeletion,
} from "../Types/station_types";
import {
	CurrentPlayingInfo,
	SongListDisplayItem,
} from "../Types/song_info_types";
import { Flags, StringObject } from "../Types/generic_types";
import { ListData, TableData } from "../Types/pageable_types";
import {
	User,
	ActionRule,
} from "../Types/user_types";

export const fetchStations = async (params?: OwnerParam) => {
	const response = await webClient.get<ListData<StationInfo>>(
		"stations/list",
		{
			params: {
				ownerKey: params?.ownerKey || undefined,
			},
		});
	return response.data;
};

export const fetchStationForEdit = async (
	{ ownerKey, stationKey }: { ownerKey: KeyType, stationKey: KeyType}
) => {
	const response = await webClient.get<StationInfo>(
		`stations/${ownerKey}/${stationKey}/`
	);
	return response.data;
};

export const checkValues = async (
	{ id, values }: { id: IdType, values: StringObject }
) => {
	const response = await webClient.get<Flags<StringObject>>("stations/check/", {
		params: {
			id,
			...values,
		},
	});
	return response.data;
};

export const saveStation = async (
	{ values, id}: { values: StationCreationInfo, id?: IdType | null }
) => {
	if(id) {
		const response = await webClient.put<StationInfo>(
			`/stations/${id}`,
			values
		);
		return response.data;
	}
	else {
		const response = await webClient.post<StationInfo>("stations", values);
		return response.data;
	}
};

export const fetchSongCatalogue = async ({
	stationKey,
	ownerKey,
	...params
}: RequiredStationParams) => {
	const url = `stations/${ownerKey}/${stationKey}/catalogue/`;
	const response = await webClient.get<
		StationTableData<SongListDisplayItem>
	>(url, { params: params });
	return response.data;
};

export const fetchQueue = async (
	{ stationKey, ownerKey, ...params }: RequiredStationParams
) => {
	const url = `stations/${ownerKey}/${stationKey}/queue/`;
	const response = await webClient.get<CurrentPlayingInfo>(url, {
		params: params,
	});
	return response.data;
};

export const fetchHistory = async (
	{ stationKey, ownerKey, ...params }: RequiredStationParams
) => {
	const url = `stations/${ownerKey}/${stationKey}/history/`;
	const response = await webClient.get<
		StationTableData<SongListDisplayItem>
	>(url, { params: params });
	return response.data;
};

export const sendSongRequest = async (
	{ stationKey, songId}: {stationKey: KeyType, songId: IdType}
) => {
	const response = await webClient
		.post<void>(`stations/${stationKey}/request/${songId}`);
	return response.data;
};

export const removeSongFromQueue = async (
	params: RequiredStationParams & { songId: IdType, queuedTimestamp: number }
) => {
	const {
		ownerKey,
		stationKey,
		songId,
		queuedTimestamp,
	} = params;
	const response = await webClient.delete<CurrentPlayingInfo>(
		`stations/${ownerKey}/${stationKey}/request`, {
			params: {
				id: songId,
				queuedTimestamp,
			},
		});
	return response.data;
};

export const enableStations = async (
	{ ids }: { ids: IdType[] | IdType }
) => {
	const queryStr = buildArrayQueryStrFromObj({"stationIds": ids});
	const response = await webClient
		.put<StationInfo[]>(`stations/enable/${queryStr}`);
	return response.data;
};

export const disableStations = async (
	{ ids=[] }: { ids?: number[], includeAll?: boolean }
) => {
	const queryStr = buildArrayQueryStrFromObj({"stationIds": ids});
	const response = await webClient
		.put<void>(`stations/disable/${queryStr}`);
	return response.data;
};

export const fetchStationUsers = async ({
	stationKey,
	ownerKey,
	...params
}: RequiredStationParams) => {
	const url = `stations/${ownerKey}/${stationKey}/user_list`;
	const response = await webClient.get<TableData<User>>(url, {
		params: params,
	});
	return response.data;
};

export const addStationUserRule = async ({
	ownerKey,
	stationKey,
	subjectUserKey,
	rule,
}: StationRuleAddition ) => {
	const url = `stations/${ownerKey}/${stationKey}/user_role`;
	const response = await webClient.post<ActionRule>(url, rule, {
		params: { subjectUserKey },
	});
	return response.data;
};

export const removeStationUserRule = async ({
	ownerKey,
	stationKey,
	subjectUserKey,
	ruleName,
}: StationRuleDeletion) => {
	const url = `stations/${ownerKey}/${stationKey}/user_role`;
	const response = await webClient.delete(url, {
		params: { subjectUserKey, ruleName },
	});
	return response.data;
};