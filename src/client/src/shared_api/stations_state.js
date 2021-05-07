import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import webClient from "../api";
import { CallStatus } from "../constants";

export const fetchStations = createAsyncThunk("stations/fetch", async () => {
  const response = await webClient.get("/stations");
  return response.data;
});

const initialState = {
  status: "",
  values: [],
  error: null,
};

const slice = createSlice({
  name: "stations",
  initialState,
  extraReducers: {
    [fetchStations.pending]: (state) => {
      state.status = CallStatus.loading;
    },
    [fetchStations.fulfilled]: (state, action) => {
      state.status = CallStatus.done;
      state.values = action.payload;
    },
    [fetchStations.rejected]: (state, action) => {
      state.status = CallStatus.failed;
      state.error = action.error;
    },
  },
});

export default slice.reducer;
