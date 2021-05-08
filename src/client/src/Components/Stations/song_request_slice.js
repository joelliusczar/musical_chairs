import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import webClient from "../../api";
import { CallStatus, ApiRoutes, CallType } from "../../constants";

export const requestSong = createAsyncThunk("stations/request", 
  async ({station, songId}) => {
    const response = await webClient
      .post(ApiRoutes.songRequest(station, songId));
    return response.data;
  });

const initialState = {
  status: {},
  values: {
    items: [],
  },
  error: {},
};

const slice = createSlice({
  name: "stations",
  initialState,
  extraReducers: {
    [requestSong.pending]: (state) => {
      state[CallType.post].status = CallStatus.loading;
    },
    [requestSong.fulfilled]: (state, action) => {
      state[CallType.post].status = CallStatus.done;
      state[CallType.post].values = action.payload;
    },
    [requestSong.rejected]: (state, action) => {
      state[CallType.post].status = CallStatus.failed;
      state[CallType.post].error = action.error;
    },
  },
});

export default slice.reducer;
