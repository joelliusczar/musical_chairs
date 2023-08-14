import axios, { AxiosInstance } from "axios";
import { apiAddress } from "../constants";

export const constructWebClient = (): AxiosInstance => {
	return axios.create({
		baseURL: apiAddress,
		withCredentials: true,
	});
}

export const defaultWebClient = constructWebClient();

export default defaultWebClient;