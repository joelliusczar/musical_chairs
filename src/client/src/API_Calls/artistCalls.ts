import { defaultWebClient as webClient } from "./api";
import {
	IdValue,
	Named,
	Token,
} from "../Types/generic_types";
import {
	ArtistInfo,
	SongsArtistInfo,
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
				const response = await webClient.get<SongsArtistInfo>(
					`/artists/${id}`,
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
				const response = await webClient.get<PageableListDataShape<ArtistInfo>>(
					"artists/page",
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
				const response = await webClient.get<ListData<ArtistInfo>>(
					"/artists/list",
					{
						params: params,
						signal: abortController.signal,
					});
				return response.data;
			},
		};
	},
	add: ({ name }: Named)  => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {

				const response = await webClient.post<ArtistInfo>(
					"/artists",
					null,
					{
						params: {
							name,
						},
						signal: abortController.signal,
					}
				);
				return response.data;
			},
		};
	},
	update: (
		{ id, data }: { id: Token, data: Named }
	) => {
		const abortController = new AbortController();
		return {
			abortController: abortController,
			call: async () => {

				const response = await webClient.put<ArtistInfo>(
					`/artists/${id}`,
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
					`/artists/${id}`,
					{ signal: abortController.signal }
				);
				return response.data;
			},
		};
	},
};
