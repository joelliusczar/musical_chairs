import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import webClient from "../../api";
import { CallStatus, ApiRoutes, CallType } from "../../constants";

export const fetchHistory = createAsyncThunk(
  "history/fetch",
  async ({ station }) => {
    const response = await webClient.get(ApiRoutes.history(station));
    return response.data;
  }
);

const initialState = {
  status: {
    [CallType.fetch]: "",
  },
  values: { 
    [CallType.fetch]:{
      items: [],
    },
  },
  error: {},
};

const slice = createSlice({
  name: "history",
  initialState,
  extraReducers: {
    [fetchHistory.pending]: (state) => {
      state.status[CallType.fetch] = CallStatus.loading;
    },
    [fetchHistory.fulfilled]: (state, action) => {
      state.status[CallType.fetch] = CallStatus.done;
      state.values[CallType.fetch] = action.payload;
    },
    [fetchHistory.rejected]: (state, action) => {
      state.status[CallType.fetch] = CallStatus.failed;
      state.error[CallType.fetch] = action.error;
    },
  },
});

export default slice.reducer;