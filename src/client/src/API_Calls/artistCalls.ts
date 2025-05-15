import { defaultWebClient as webClient } from "./api";
import {
	IdValue,
} from "../Types/generic_types";
import {
	ArtistInfo,
	AlbumCreationInfo,
	SongsArtistInfo,
} from "../Types/song_info_types";
import { PageableParams, ListData } from "../Types/pageable_types";
import {
	PageableListDataShape,
} from "../Types/reducerTypes";


export const get = ({ id }: { id: IdValue }) => {
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
};

export const getPage = (params: PageableParams) => {
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
};

export const getList = ({ params }: { params?: object}) => {
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
};

export const add = ({ data }: { data: AlbumCreationInfo}) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {

			const response = await webClient.post<ArtistInfo>(
				"/artists",
				data,
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};

export const update = (
	{ id, data }: { id: IdValue, data: AlbumCreationInfo }
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
};


export const remove = ({ id }: { id: IdValue }) => {
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
};