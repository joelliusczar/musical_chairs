import { defaultWebClient as webClient } from "./api";
import { buildArrayQueryStr } from "../Helpers/url_helpers";

export const fetchSongForEdit = async ({ id }) => {
	const response = await webClient.get(`/song-info/songs/${id}`);
	return response.data;
};

export const fetchSongsForMultiEdit = async ({ ids }) => {
	const queryStr = buildArrayQueryStr("itemIds", ids);
	const response = await webClient.get(`/song-info/songs/multi/${queryStr}`);
	return response.data;
};


export const saveSongEdits = async ({ id, data }) => {
	const response = await webClient.put(`/song-info/songs/${id}`, data);
	return response.data;
};

export const saveSongsEditsMulti = async ({ ids, data }) => {
	const queryStr = buildArrayQueryStr("itemIds", ids);
	const response = await webClient
		.put(`/song-info/songs/multi/${queryStr}`, data);
	return response.data;
};

export const fetchArtistList = async ({ params }) => {
	const response = await webClient.get("/song-info/artists/list", {
		params: params,
	});
	return response.data;
};

export const fetchAlbumList = async ({ params }) => {
	const response = await webClient.get("/song-info/albums/list", {
		params: params,
	});
	return response.data;
};

export const saveArtist = async ({ artistName }) => {
	const response = await webClient.post("/song-info/artists", null, {
		params: {
			artistName,
		},
	});
	return response.data;
};

export const saveAlbum = async ({ data }) => {
	const response = await webClient.post("/song-info/albums", data);
	return response.data;
};

export const fetchSongTree = async ({ params }) => {
	const response = await webClient.get("song-info/songs/ls", {
		params: params,
	});
	return response.data;
};