import axios from "axios";
import { apiAddress } from "../constants";

export const constructWebClient = () => {
	return axios.create({
		baseURL: apiAddress,
		withCredentials: true,
	});
};

export const defaultWebClient = constructWebClient();

export default defaultWebClient;