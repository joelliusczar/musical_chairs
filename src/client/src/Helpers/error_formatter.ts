export const formatError = (err) => {
	if(!err?.response?.data) {
		return "Unable to hit api.";
	}
	return err.response.data.detail[0].msg;
};