import { isAxiosError } from "axios";


export const formatError = (err: unknown): string => {
	if(isAxiosError(err)) {
		if (!err?.response?.data) {
			return "Unable to hit api.";
		}
		if ((!err?.response?.data?.detail)) {
			return "Probably some sort of misconfig error";
		}
		return err.response.data.detail[0].msg;
	}
	console.error(err);
	return "undocumented error has occured";
};