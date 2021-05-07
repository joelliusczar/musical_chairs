import React, { useEffect, useState } from "react";
import { useHistory, useParams } from "react-router-dom";
import { fetchStations } from "../Stations/stations_slice";
import { fetchHistory } from "./history_slice";
import { useDispatch, useSelector } from "react-redux";
import { makeStyles, 
  MenuItem, 
  Select,
  Table, 
  TableBody, 
  TableContainer, 
  TableCell, 
  TableHead, 
  TableRow,
} from "@material-ui/core";
import Loader from "../Shared/Loader";
import { CallStatus } from "../../constants";

const useStyles = makeStyles(() => ({
  select: {
    width: 150,
  },
}));

export default function History() {
  const [selectedStation, setSelectedStation] = useState("");
  const { station: stationParam } = useParams();
  const history = useHistory();
  const dispatch = useDispatch();
  const classes = useStyles();
  const stations = useSelector((appState) => appState.stations.values);
  const stationsStatus =  useSelector((appState) => appState.stations.status);
  const songHistory= useSelector((appState) => appState.history.values);
  const songHistoryStatus =  useSelector((appState) => appState.history.status);
  const songHistoryError =  useSelector((appState) => appState.history.error);
  

  useEffect(() => {
    if(!stationsStatus || stationsStatus === CallStatus.idle) { 
      dispatch(fetchStations());
    }
  }, [dispatch, stationsStatus]);

  useEffect(() => {
    document.title = "Musical Chairs - History";
  });

  useEffect(() => {
    history.replace(`/history/${selectedStation}`);
  }, [history, selectedStation]);

  useEffect(() => {
    if (stationParam) {
      dispatch(fetchHistory({ station: stationParam }));
    }
  }, [stationParam, dispatch]);

  return (
    <>
      <h1>History: {stationParam}</h1>
      {stations && (
        <Select
          className={classes.select}
          displayEmpty
          label="Stations"
          onChange={(e) => setSelectedStation(e.target.value)}
          renderValue={(v) => v || "Select Station"}
          value={selectedStation}
        >
          {stations.map((s) => {
            return (
              <MenuItem key={s.name} value={s.name}>
                {s.name}
              </MenuItem>
            );
          })}
        </Select>
      )}
      <Loader 
        status={songHistoryStatus} 
        error={songHistoryError} 
        isReady={!!stationParam}
      >
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Song</TableCell>
                <TableCell>Album</TableCell>
                <TableCell>Artist</TableCell>
                <TableCell>Last Played</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {songHistory.map((item, idx) => {
                return (
                  <TableRow key={`song_${idx}`}>
                    <TableCell>{item.song || "{No song name}"}</TableCell>
                    <TableCell>{item.album || "{No album name}"}</TableCell>
                    <TableCell>{item.artist || "{No artist name}"}</TableCell>
                    <TableCell></TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Loader>
    </>
  );
}
