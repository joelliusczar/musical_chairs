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
import { CallStatus, DomRoutes, CallType } from "../../constants";


const useStyles = makeStyles(() => ({
  select: {
    width: 150,
  },
}));

export default function History() {
  const [selectedStation, setSelectedStation] = useState("");
  const [selectTouched, setSelectTouched] = useState();
  const { station: stationParam } = useParams();
  const urlHistory = useHistory();
  const dispatch = useDispatch();
  const classes = useStyles();
  const stations = useSelector((appState) => 
    appState.stations.values[CallType.fetch]);
  const stationsStatus =  useSelector((appState) => 
    appState.stations.status[CallType.fetch]);
  const songHistoryObj = useSelector((appState) => 
    appState.history.values[CallType.fetch]);
  const songHistoryStatus =  useSelector((appState) => 
    appState.history.status[CallType.fetch]);
  const songHistoryError =  useSelector((appState) => 
    appState.history.error[CallType.fetch]);
  

  useEffect(() => {
    if(!stationsStatus || stationsStatus === CallStatus.idle) { 
      dispatch(fetchStations());
    }
  }, [dispatch, stationsStatus]);

  useEffect(() => {
    document.title = `Musical Chairs - History${`- ${stationParam || ""}`}`;
  },[stationParam]);

  useEffect(() => {
    if(!selectTouched) return;
    urlHistory.replace(`${DomRoutes.history}${selectedStation}`);
  }, [urlHistory, selectedStation, selectTouched]);

  useEffect(() => {
    if (!stationParam) return;
    const station = stationParam.toLowerCase();
    if(stations.items.some(s => s.name.toLowerCase() === station)) {
      setSelectedStation(stationParam);
      setSelectTouched(false);
      dispatch(fetchHistory({ station: stationParam }));
    }
  }, [stationParam, dispatch, setSelectedStation, setSelectTouched, stations]);

  return (
    <>
      <h1>History: {stationParam}</h1>
      {stations && (
        <Select
          className={classes.select}
          displayEmpty
          label="Stations"
          onChange={(e) => {
            setSelectTouched(true);
            setSelectedStation(e.target.value);
          }}
          renderValue={(v) => v || "Select Station"}
          value={selectedStation}
        >
          {stations.items.map((s) => {
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
              {songHistoryObj.items.map((item, idx) => {
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
