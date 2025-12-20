import { defaultWebClient as webClient } from "./api";
import { PageableParams, ListData } from "../Types/pageable_types";
import {
	PageableListDataShape,
} from "../Types/reducerTypes";
import {
	IdValue,
	StringObject,
	Flags,
	KeyValue,
} from "../Types/generic_types";
import {
	PlaylistInfo,
	PlaylistCreationInfo,
	PlaylistsSongsInfo,
} from "../Types/playlist_types";
import { buildArrayQueryStrFromObj } from "../Helpers/request_helpers";



export const Calls = {
	get: (
		{ ownerkey, playlistkey }: { ownerkey: KeyValue, playlistkey: KeyValue }
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {

				const response = await webClient.get<PlaylistsSongsInfo>(
					`playlists/${ownerkey}/${playlistkey}`,
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
	getPage: (params: PageableParams) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient
					.get<PageableListDataShape<PlaylistInfo>>(
						"playlists/page",
						{ params: params, signal: abortController.signal }
					);
				return response.data;
			},
		};
	},
	getList: ({ params }: { params?: object}) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient.get<ListData<PlaylistInfo>>(
					"playlists/list",
					{
						params: params,
						signal: abortController.signal,
					});
				return response.data;
			},
		};
	},
	add: ({ data }: { data: PlaylistCreationInfo}) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {

				const response = await webClient.post<PlaylistInfo>(
					"/playlists",
					data,
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
	update: (
		{ id, data }: { id: IdValue, data: PlaylistCreationInfo }
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {

				const response = await webClient.put<PlaylistInfo>(
					`/playlists/${id}`,
					data,
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
	remove: ({ id }: { id: IdValue }) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {

				const response = await webClient.delete(
					`/playlists/${id}`,
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
					"playlists/check/", {
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
	removeSongs: (
		{ ids, playlistid }:
		{ ids: IdValue[], playlistid: KeyValue  }
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const queryStr = buildArrayQueryStrFromObj({"songids": ids});
				const response = await webClient.delete(
					`playlists/${playlistid}/songs/${queryStr}`, {
						signal: abortController.signal,
					}
				);
				return response.data;
			},
		};
	},
	moveSong: ({ playlistid, songid, order }: { 
		playlistid: IdValue,
		songid: IdValue,
		order: number
	}) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient.post(
					`playlists/${playlistid}/move/${songid}/to/${order}`,
					null,
					{
						signal: abortController.signal,
					}
				);
				return response.data;
			},
		};
	},
};

