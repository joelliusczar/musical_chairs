import { defaultWebClient as webClient } from "./api";

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