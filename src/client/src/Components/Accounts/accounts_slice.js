import { createAsyncThunk } from "@reduxjs/toolkit";
import { defaultWebClient as webClient } from "../../api";
import { ApiRoutes } from "../../constants";

export const login = createAsyncThunk(
	"accounts/login",
	async ({username, password}) => {
		const formData = new window.FormData();
		formData.append("username", username);
		formData.append("password", password);
		const response = await webClient.post(ApiRoutes.login, formData);
		return response.data;
	}
);