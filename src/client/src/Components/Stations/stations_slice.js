import webClient from "../../api";


export const fetchStations = async () => {
	const response = await webClient.get("stations/list");
	return response.data;
};
