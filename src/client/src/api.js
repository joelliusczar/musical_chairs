import axios from "axios";
import { apiAddress } from "./constants";

export function constructWebClient() {
	return axios.create({
		baseURL: apiAddress,
	});
}

export const defaultWebClient = constructWebClient();

export default defaultWebClient;