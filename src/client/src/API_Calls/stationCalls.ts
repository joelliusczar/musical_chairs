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
	CatalogueItem,
} from "../Types/song_info_types";
import { Flags, StringObject } from "../Types/generic_types";
import { ListData, TableData } from "../Types/pageable_types";
import {
	RoledUser,
	ActionRule,
} from "../Types/user_types";
import { StationRequestTypes } from "../constants";

export const Calls = {
	getList: (params?: OwnerParam) => {
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
	},
	get: (
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
	},
	checkValues: (
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
	},
	save: (
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
					const response = await webClient.post<StationInfo>(
						"stations",
						values
					);
					return response.data;
				}
			},
		};
	},
	remove: ({ id }: { id: IdValue }) => {
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
	},
	copy: (
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
	},
	getCatalogue: ({
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
					StationTableData<CatalogueItem>
				>(
					url,
					{ params: params, signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
	getQueue: (
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
	},
	getHistory: (
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
	},
	queueRequest: (
		{ stationkey, ownerkey, itemid, requesttypeid = StationRequestTypes.SONG }: 
		RequiredStationParamsOnly & {
			itemid: IdValue,
			requesttypeid?: IdValue,
		}
	) => {
		const abortController = new AbortController();
		const stationKeySegment = `${ownerkey}/${stationkey}`;
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient
					.post<void>(
						`stations/${stationKeySegment}/request/${requesttypeid}/${itemid}`,
						null,
						{ signal: abortController.signal }
					);
				return response.data;
			},
		};
	},
	removeSongFromQueue: (
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
	},
	enableStation: (
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
	},
	disableStations: (
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
	},
	getStationUsers: ({
		stationkey,
		ownerkey,
		...params
	}: RequiredStationParams) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const url = `stations/${ownerkey}/${stationkey}/user_list`;
				const response = await webClient.get<TableData<RoledUser>>(url, {
					params: params,
					signal: abortController.signal,
				});
				return response.data;
			},
		};
	},
	addStationUserRule: ({
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
	},
	removeStationUserRule: ({
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
	},
};

