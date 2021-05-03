import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import webClient from "../../api";
import { CallStatus } from "../../constants"

export const fetchQueue = createAsyncThunk(
  "queue/fetch",
  async ({ station }) => {
    const response = await webClient.get(`queue/${station}`);
    return response.data;
  }
);

const initialState = {
    status: '',
    values: [],
    error: null,
    signal: null,
};

const slice = createSlice({
    name: 'queue',
    initialState,
    reducers: {
        sendRefreshSignal: (state) => {
            state.signal = {};
        }
    },
    extraReducers: {
        [fetchQueue.pending]: (state) => {
            state.status = CallStatus.loading;
        },
        [fetchQueue.fulfilled]: (state, action) => {
            state.status = CallStatus.done;
            state.values = action.payload;
        },
        [fetchQueue.rejected]: (state, action) => {
            state.status = CallStatus.failed;
            state.error = action.error;
        },
    }
});

export default slice.reducer;