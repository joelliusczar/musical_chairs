import { defaultWebClient as webClient } from "./api";
import { buildArrayQueryStr } from "../Helpers/request_helpers";
import {
	AlbumInfo,
	ArtistInfo,
	SongTreeNodeInfo,
	SongInfoApiSavura,
	SongInfoForm,
	AlbumCreationInfo,
	UploadInfo,
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


export const fetchSongForEdit = ({ id }: { id: IdValue}) => {
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
};

export const fetchSongsForMultiEdit = ({ ids }: { ids: IdValue[]}) => {
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
};

export const saveSongEdits = (
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
};

export const saveSongsEditsMulti = (
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
};

export const fetchArtistList = ({ params }: { params?: object}) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.get<ListData<ArtistInfo>>(
				"/song-info/artists/list",
				{
					params: params,
					signal: abortController.signal,
				});
			return response.data;
		},
	};
};


export const fetchAlbumList = ({ params }: { params?: object}) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.get<ListData<AlbumInfo>>(
				"/song-info/albums/list",
				{
					params: params,
					signal: abortController.signal,
				});
			return response.data;
		},
	};
};

export const saveArtist = ({ name }: { name: string }) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.post<ArtistInfo>(
				"/song-info/artists",
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
};

export const saveAlbum = ({ data }: { data: AlbumCreationInfo}) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {

			const response = await webClient.post<AlbumInfo>(
				"/song-info/albums",
				data,
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};

export const fetchSongsLs = ({ prefix }: { prefix: string }) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.get<ListData<SongTreeNodeInfo>>(
				"song-info/songs/ls",
				{
					params: {
						prefix,
					},
					signal: abortController.signal,
				}
			);
			return response.data;
		},
	};
};


export const fetchSongLsParents = ({ prefix }: { prefix: string }) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient
				.get<Dictionary<ListData<SongTreeNodeInfo>>>(
					"song-info/songs/ls_parents",
					{
						params: {
							prefix,
						},
						signal: abortController.signal,
					}
				);
			return response.data;
		},
	};
};


export const fetchPathUsers = (
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
};

export const addPathUserRule = (
	{ rule, ...params }: SubjectUserRoleAddition & { prefix: string | null }
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
};

export const removePathUserRule = (
	{ ...params }: SubjectUserRoleDeletion & { prefix: string | null }
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
};

export const saveDirectory = (
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
};

export const checkValues = (
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
};

export const checkSuffixes = ({
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
};

export const uploadSong = (
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
};

export const songDownloadUrl = ({ id }:{ id: IdValue}) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.get<string>(
				`/song-info/songs/download/${id}`,
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};