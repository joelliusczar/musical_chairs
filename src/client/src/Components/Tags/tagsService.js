import webClient from "../../api";


export const fetchTags = async () => {
	const response = await webClient.get("stations/tags");
	return response.data;
};

export const saveTag = async ({ tagName }) => {
	const response = await webClient.post("stations/tags", null, {
		params: {
			tagName: tagName,
		},
	});
	return response.data;
};
