import { isAxiosError } from "axios";


export const formatError = (err: unknown): string => {
	if(isAxiosError(err)) {
		if(!err?.response?.data) {
			return "Unable to hit api.";
		}
		return err.response.data.detail[0].msg;
	}
	console.error(err);
	return "undocumented error has occured";
};