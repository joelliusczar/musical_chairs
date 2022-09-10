import webClient from "./api";


export const fetchTags = async () => {
	const response = await webClient.get("tags");
	return response.data;
};

export const saveTag = async ({ tagName }) => {
	const response = await webClient.post("tags", null, {
		params: {
			tagName: tagName,
		},
	});
	return response.data;
};
