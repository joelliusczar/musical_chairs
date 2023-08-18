import { defaultWebClient as webClient } from "./api";
import { buildArrayQueryStr } from "../Helpers/url_helpers";
import {
	AlbumInfo,
	ArtistInfo,
	SongTreeNodeInfo,
	SongInfoApiSavura,
	SongInfoForm,
	AlbumCreationInfo,
} from "../Types/song_info_types";
import { IdType } from "../Types/generic_types";
import { ListData, TableData, PageableParams } from "../Types/pageable_types";
import {
	User,
	SubjectUserRoleAddition,
	SubjectUserRoleDeletion,
	PathsActionRule
} from "../Types/user_types";


export const fetchSongForEdit = async ({ id }: { id: IdType}) => {
	const response = await webClient.get<SongInfoApiSavura>(
		`/song-info/songs/${id}`
	);
	return response.data;
};

export const fetchSongsForMultiEdit = async ({ ids }: { ids: IdType[]}) => {
	const queryStr = buildArrayQueryStr("itemIds", ids);
	const response = await webClient.get<SongInfoApiSavura>(
		`/song-info/songs/multi/${queryStr}`
	);
	return response.data;
};


export const saveSongEdits = async (
	{ id, data }: { id: IdType, data: SongInfoApiSavura}
) => {
	const response = await webClient.put<SongInfoForm>(
		`/song-info/songs/${id}`,
		data
	);
	return response.data;
};

export const saveSongsEditsMulti = async (
	{ ids, data }: { ids: IdType[], data: SongInfoApiSavura}
) => {
	const queryStr = buildArrayQueryStr("itemIds", ids);
	const response = await webClient
		.put<SongInfoForm>(`/song-info/songs/multi/${queryStr}`, data);
	return response.data;
};

export const fetchArtistList = async ({ params }: { params?: any}) => {
	const response = await webClient.get<ListData<ArtistInfo>>(
		"/song-info/artists/list",
		{
		params: params,
	});
	return response.data;
};

export const fetchAlbumList = async ({ params }: { params?: any}) => {
	const response = await webClient.get<ListData<AlbumInfo>>(
		"/song-info/albums/list",
		{
			params: params,
	});
	return response.data;
};

export const saveArtist = async ({ name }: { name: string }) => {
	const response = await webClient.post<ArtistInfo>(
		"/song-info/artists",
		null,
		{
			params: {
				name,
			},
		}
	);
	return response.data;
};

export const saveAlbum = async ({ data }: { data: AlbumCreationInfo}) => {
	const response = await webClient.post<AlbumInfo>("/song-info/albums", data);
	return response.data;
};

export const fetchSongTree = async ({ prefix }: { prefix: string }) => {
	const response = await webClient.get<ListData<SongTreeNodeInfo>>(
		"song-info/songs/ls",
		{
			params: {
				prefix
			},
		}
	);
	return response.data;
};

export const fetchPathUsers = async (
	params: PageableParams & { prefix: string}
) => {
	const url = "song-info/path/user_list";
	const response = await webClient.get<TableData<User>>(url, {
		params: params,
	});
	return response.data;
};

export const addPathUserRule = async (
	{ rule, ...params }: SubjectUserRoleAddition & { prefix: string | null }
) => {
	const url = "song-info/path/user_role";
	const response = await webClient.post<PathsActionRule>(url, rule, {
		params: params,
	});
	return response.data;
};

export const removePathUserRule = async (
	{ ...params }: SubjectUserRoleDeletion & { prefix: string | null }
) => {
	const url = "song-info/path/user_role";
	const response = await webClient.delete<void>(url, {
		params: params,
	});
	return response.data;
};