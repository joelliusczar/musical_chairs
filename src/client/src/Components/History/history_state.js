import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import webClient from "../../api";
import { CallStatus } from "../../constants";

export const fetchHistory = createAsyncThunk(
  "history/fetch",
  async ({ station }) => {
    const response = await webClient.get(`/history/${station}`);
    return response.data;
  }
);

const initialState = {
  status: "",
  values: [],
  error: null,
};

const slice = createSlice({
  name: "history",
  initialState,
  extraReducers: {
    [fetchHistory.pending]: (state) => {
      state.status = CallStatus.loading;
    },
    [fetchHistory.fulfilled]: (state, action) => {
      state.status = CallStatus.done;
      state.values = action.payload;
    },
    [fetchHistory.rejected]: (state, action) => {
      state.status = CallStatus.failed;
      state.error = action.error;
    },
  },
});

export default slice.reducer;