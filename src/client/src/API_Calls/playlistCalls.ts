import { defaultWebClient as webClient } from "./api";
import { PageableParams } from "../Types/pageable_types";
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


export const get = (
	{ ownerkey, playlistkey }: { ownerkey: KeyValue, playlistkey: KeyValue}
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
};

export const getPage = (params: PageableParams) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.get<PageableListDataShape<PlaylistInfo>>(
				"playlists/page",
				{ params: params, signal: abortController.signal }
			);
			return response.data;
		},
	};
};


export const add = ({ data }: { data: PlaylistCreationInfo}) => {
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
};

export const update = (
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
};



export const remove = ({ id }: { id: IdValue }) => {
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
};

export const checkValuesCaller = (
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
};