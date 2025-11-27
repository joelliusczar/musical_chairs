import webClient from "./api";
import { buildArrayQueryStrFromObj } from "../Helpers/request_helpers";
import { OwnerParam, KeyValue, IdValue } from "../Types/generic_types";
import {
	RequiredStationParams,
	StationCreationInfo,
	StationInfo,
	StationTableData,
	StationRuleAddition,
	StationRuleDeletion,
	RequiredStationParamsOnly,
} from "../Types/station_types";
import {
	CurrentPlayingInfo,
	SongListDisplayItem,
	CollectionQueuedItem,
} from "../Types/song_info_types";
import { Flags, StringObject } from "../Types/generic_types";
import { ListData, TableData } from "../Types/pageable_types";
import {
	User,
	ActionRule,
} from "../Types/user_types";

export const fetchStations = (params?: OwnerParam) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.get<ListData<StationInfo>>(
				"stations/list",
				{
					params: {
						ownerkey: params?.ownerkey || undefined,
					},
				});
			return response.data;
		},
	};
};

export const getRecordCaller = (
	{ ownerkey, stationkey }: { ownerkey: KeyValue, stationkey: KeyValue}
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {

			const response = await webClient.get<StationInfo>(
				`stations/${ownerkey}/${stationkey}`,
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};

export const checkValuesCaller = (
	{ id, values }: { id: IdValue, values: StringObject }
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {

			const response = await webClient.get<Flags<StringObject>>(
				"stations/check/", {
					params: {
						id,
						...values,
					},
					signal: abortController.signal,
				}
			);
			return response.data;
		},
	};
};

export const saveCaller = (
	{ values, id }: { values: StationCreationInfo, id?: IdValue | null }
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			if(id) {
				const response = await webClient.put<StationInfo>(
					`/stations/${id}`,
					values,
					{ signal: abortController.signal }
				);
				return response.data;
			}
			else {
				const response = await webClient.post<StationInfo>("stations", values);
				return response.data;
			}
		},
	};
};

export const fetchSongCatalogue = ({
	stationkey,
	ownerkey,
	...params
}: RequiredStationParams) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const url = `stations/${ownerkey}/${stationkey}/catalogue/`;
			const response = await webClient.get<
				StationTableData<SongListDisplayItem>
			>(
				url,
				{ params: params, signal: abortController.signal }
			);
			return response.data;
		},
	};
};


export const fetchCollectionCatalogueCaller = ({
	stationkey,
	ownerkey,
	...params
}: RequiredStationParams) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const url = `stations/${ownerkey}/${stationkey}/collection_catalogue/`;
			const response = await webClient.get<
				StationTableData<CollectionQueuedItem>
			>(
				url,
				{ params: params, signal: abortController.signal }
			);
			return response.data;
		},
	};
};

export const fetchQueue = (
	{ stationkey, ownerkey, ...params }: RequiredStationParams
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const url = `stations/${ownerkey}/${stationkey}/queue/`;
			const response = await webClient.get<CurrentPlayingInfo>(
				url, {
					params: params,
					signal: abortController.signal,
				}
			);
			return response.data;
		},
	};
};

export const fetchHistory = (
	{ stationkey, ownerkey, ...params }: RequiredStationParams
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const url = `stations/${ownerkey}/${stationkey}/history/`;
			const response = await webClient.get<
				StationTableData<SongListDisplayItem>
			>(url, { params: params, signal: abortController.signal });
			return response.data;
		},
	};
};

export const sendSongRequestCaller = (
	{ stationkey, ownerkey, songid}: RequiredStationParamsOnly & {songid: IdValue}
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient
				.post<void>(
					`stations/${ownerkey}/${stationkey}/request/${songid}`,
					null,
					{ signal: abortController.signal }
				);
			return response.data;
		},
	};
};

export const sendCollectionRequestCaller = (
	{ 
		stationkey,
		ownerkey,
		collectionId,
		typeId,
	}: RequiredStationParamsOnly & {collectionId: IdValue, typeId: IdValue }
) => {
	const abortController = new AbortController();
	const stationKeySegment = `${ownerkey}/${stationkey}`;
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient
				.post<void>(
					`stations/${stationKeySegment}/request/${typeId}/${collectionId}`,
					null,
					{ signal: abortController.signal }
				);
			return response.data;
		},
	};
};

export const removeSongFromQueue = (
	params: RequiredStationParams & { songid: IdValue, queuedtimestamp: number }
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const {
				ownerkey,
				stationkey,
				songid,
				queuedtimestamp,
			} = params;
			const response = await webClient.delete<CurrentPlayingInfo>(
				`stations/${ownerkey}/${stationkey}/request`, {
					params: {
						id: songid,
						queuedtimestamp,
					},
					signal: abortController.signal,
				});
			return response.data;
		},
	};
};

export const enableStationsCaller = (
	{ ids }: { ids: IdValue[] | IdValue }
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const queryStr = buildArrayQueryStrFromObj({"stationids": ids});
			const response = await webClient
				.put<StationInfo[]>(
					`stations/enable/${queryStr}`,
					null,
					{ signal: abortController.signal }
				);
			return response.data;
		},
	};
};

export const disableStations = (
	{ ids=[] }: { ids?: number[], includeAll?: boolean }
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const queryStr = buildArrayQueryStrFromObj({"stationids": ids});
			const response = await webClient
				.put<void>(
					`stations/disable/${queryStr}`,
					null,
					{ signal: abortController.signal }
				);
			return response.data;
		},
	};
};

export const fetchStationUsers = ({
	stationkey,
	ownerkey,
	...params
}: RequiredStationParams) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const url = `stations/${ownerkey}/${stationkey}/user_list`;
			const response = await webClient.get<TableData<User>>(url, {
				params: params,
				signal: abortController.signal,
			});
			return response.data;
		},
	};
};

export const addStationUserRule = ({
	ownerkey,
	stationkey,
	subjectuserkey,
	rule,
}: StationRuleAddition ) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const url = `stations/${ownerkey}/${stationkey}/user_role`;
			const response = await webClient.post<ActionRule>(url, rule, {
				params: { subjectuserkey },
				signal: abortController.signal,
			});
			return response.data;
		},
	};
};

export const removeStationUserRule = ({
	ownerkey,
	stationkey,
	subjectuserkey,
	rulename,
}: StationRuleDeletion) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const url = `stations/${ownerkey}/${stationkey}/user_role`;
			const response = await webClient.delete(url, {
				params: { subjectuserkey, rulename },
				signal: abortController.signal,
			});
			return response.data;
		},
	};
};

export const removeRecordCaller = ({ id }: { id: IdValue }) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {

			const response = await webClient.delete(
				`/stations/${id}`,
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};

export const copyRecordCaller = (
	{ values, id }: { values: StationCreationInfo, id: IdValue }
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {

			const response = await webClient.post(
				`/stations/copy/${id}`,
				values,
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};