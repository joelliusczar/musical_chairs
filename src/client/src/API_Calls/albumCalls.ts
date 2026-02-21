import { defaultWebClient as webClient } from "./api";
import {
	IdValue,
	Token,
} from "../Types/generic_types";
import {
	AlbumInfo,
	AlbumCreationInfo,
	SongsAlbumInfo,
} from "../Types/song_info_types";
import { PageableParams, ListData } from "../Types/pageable_types";
import {
	PageableListDataShape,
} from "../Types/reducerTypes";

export const Calls = {
	get: ({ id }: { id: Token }) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient.get<SongsAlbumInfo>(
					`/albums/${id}`,
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
	getPage: (params: PageableParams & { artist?: string }) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {
				const response = await webClient.get<PageableListDataShape<AlbumInfo>>(
					"albums/page",
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
				const response = await webClient.get<ListData<AlbumInfo>>(
					"albums/list",
					{
						params: params,
						signal: abortController.signal,
					});
				return response.data;
			},
		};
	},
	add: ({ data }: { data: AlbumCreationInfo}) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {

				const response = await webClient.post<AlbumInfo>(
					"/albums",
					data,
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
	update: (
		{ id, data }: { id: Token, data: AlbumCreationInfo }
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {

				const response = await webClient.put<AlbumInfo>(
					`/albums/${id}`,
					data,
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
	remove: ({ id }: { id: Token }) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {

				const response = await webClient.delete(
					`/albums/${id}`,
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
	songCounts: () => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {

				const response = await webClient.get(
					"/albums/song-counts",
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
};


