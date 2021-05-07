import axios from "axios";
import { apiAddress } from "./constants";

export function constructWebClient() {
  return axios.create({
    baseURL: apiAddress,
  });
}

const defaultWebClient = constructWebClient();

export default defaultWebClient;