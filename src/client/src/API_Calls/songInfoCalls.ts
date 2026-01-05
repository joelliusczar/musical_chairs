import { defaultWebClient as webClient } from "./api";
import { buildArrayQueryStr } from "../Helpers/request_helpers";
import {
	SongTreeNodeInfo,
	SongInfoApiSavura,
	SongInfoForm,
	UploadInfo,
	DirectoryTransfer,
} from "../Types/song_info_types";
import {
	IdValue,
	StringObject,
	Flags,
	Dictionary,
} from "../Types/generic_types";
import { ListData, TableData, PageableParams } from "../Types/pageable_types";
import {
	User,
	SubjectUserRoleAddition,
	SubjectUserRoleDeletion,
	PathsActionRule,
} from "../Types/user_types";
import { getDownloadAddress } from "../Helpers/request_helpers";

export const Calls = {
	get: ({ id }: { id: IdValue}) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient.get<SongInfoApiSavura>(
					`/song-info/songs/${id}`,
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
	getMulti: ({ ids }: { ids: IdValue[]}) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const queryStr = buildArrayQueryStr("itemIds", ids);
				const response = await webClient.get<SongInfoApiSavura>(
					`/song-info/songs/multi/${queryStr}`,
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
	update: (
		{ id, data }: { id: IdValue, data: SongInfoApiSavura}
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient.put<SongInfoForm>(
					`/song-info/songs/${id}`,
					data,
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
	updateMulti: (
		{ ids, data }: { ids: IdValue[], data: SongInfoApiSavura}
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const queryStr = buildArrayQueryStr("itemIds", ids);
				const response = await webClient
					.put<SongInfoForm>(
						`/song-info/songs/multi/${queryStr}`,
						data,
						{ signal: abortController.signal }
					);
				return response.data;
			},
		};
	},
	getTree: ({ nodeId }: { nodeId: string }) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient.get<ListData<SongTreeNodeInfo>>(
					"song-info/songs/ls",
					{
						params: {
							nodeId,
						},
						signal: abortController.signal,
					}
				);
				return response.data;
			},
		};
	},
	getTreeParents: ({ nodeId }: { nodeId: string }) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient
					.get<Dictionary<ListData<SongTreeNodeInfo>>>(
						"song-info/songs/ls_parents",
						{
							params: {
								nodeId,
							},
							signal: abortController.signal,
						}
					);
				return response.data;
			},
		};
	},
	getPathUsers: (
		params: PageableParams & { prefix: string}
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const url = "song-info/path/user_list";
				const response = await webClient.get<TableData<User>>(
					url, {
						params: params,
						signal: abortController.signal,
					});
				return response.data;
			},
		};
	},
	addPathUserRule: (
		{ rule, ...params }: SubjectUserRoleAddition & { nodeId: string | null }
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const url = "song-info/path/user_role";
				const response = await webClient.post<PathsActionRule>(
					url,
					rule, 
					{
						params: params,
						signal: abortController.signal,
					}
				);
				return response.data;
			},
		};
	},
	removePathUserRule: (
		{ ...params }: SubjectUserRoleDeletion & { nodeId: string | null }
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const url = "song-info/path/user_role";
				const response = await webClient.delete<void>(url, {
					params: params,
					signal: abortController.signal,
				});
				return response.data;
			},
		};
	},
	saveDirectory: (
		{ suffix, prefix }: { suffix: string, prefix: string }
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient
					.post<Dictionary<ListData<SongTreeNodeInfo>>>(
						"/song-info/directory",
						null,
						{
							params: {
								prefix,
								suffix,
							},
							signal: abortController.signal,
						}
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
					"/song-info/check/", {
						params: {
							id,
							...values,
						},
						signal: abortController.signal,
					});
				return response.data;
			},
		};
	},
	checkSuffixes: ({
		prefix,
		songSuffixes,
	}: {
		prefix: string,
		songSuffixes: { id?: IdValue, suffix: string }[]
	}) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient.put<Flags<StringObject>>(
					"/song-info/check_multi/", 
					songSuffixes,
					{
						params: {
							prefix: prefix,
						},
						signal: abortController.signal,
					});
				return response.data;
			},
		};
	},
	uploadSong: (
		{ suffix, prefix, files }: UploadInfo
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const formData = new FormData();
				if (files && files.length) {
					formData.append("file", files[0]);
				}
				const response = await webClient.post<SongTreeNodeInfo>(
					"/song-info/upload",
					formData,
					{
						params: {
							prefix,
							suffix,
						},
						signal: abortController.signal,
					}
				);
				return response.data;
			},
		};
	},
	songDownload: ({ id }:{ id: IdValue}) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient.get(
					`/song-info/songs/download/${id}`,
					{ 
						signal: abortController.signal,
						responseType: "arraybuffer",
					}
				);
				return response.data as ArrayBuffer;
			},
		};
	},
	deletePrefix: ({ nodeId }:{ nodeId: string}) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient
					.delete<Dictionary<ListData<SongTreeNodeInfo>>>(
						"/song-info/path/delete_prefix",
						{ 
							params: {
								nodeId,
							},
							signal: abortController.signal,
						}
					);
				return response.data;
			},
		};
	},
	movePath: (transferObj:DirectoryTransfer) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient
					.post<Dictionary<ListData<SongTreeNodeInfo>>>(
						"/song-info/path/move",
						transferObj,
						{ 
							signal: abortController.signal,
						}
					);
				return response.data;
			},
		};
	},
};



export const openSongInTab =  (songId: number) => {
	const url = getDownloadAddress(songId);
	window?.open(url, "_blank")?.focus();
};

