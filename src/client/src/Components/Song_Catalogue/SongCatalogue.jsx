import React, { useEffect, useState } from "react";
import { useHistory, useParams } from "react-router-dom";
import { fetchStations } from "../Stations/stations_slice";
import { fetchSongCatalogue } from "./song_catalogue_slice";
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
  Button,
} from "@material-ui/core";
import Loader from "../Shared/Loader";
import { CallStatus, DomRoutes, CallType } from "../../constants";
import { requestSong } from "../Stations/song_request_slice";


const useStyles = makeStyles(() => ({
  select: {
    width: 150,
  },
}));

export default function SongCatalogue() {
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
  const songCatalogueObj = useSelector((appState) => 
    appState.songCatalogue.values[CallType.fetch]);
  const songCatalogueStatus =  useSelector((appState) => 
    appState.songCatalogue.status[CallType.fetch]);
  const songCatalogueError =  useSelector((appState) => 
    appState.songCatalogue.error[CallType.fetch]);
  
  const dispatchSongRequest = (songId) => {
    dispatch(requestSong({station: stationParam, songId }));
  };

  useEffect(() => {
    if(!stationsStatus || stationsStatus === CallStatus.idle) { 
      dispatch(fetchStations());
    }
  }, [dispatch, stationsStatus]);

  useEffect(() => {
    document.title = 
      `Musical Chairs - Song Catalogue${`- ${stationParam || ""}`}`;
  },[stationParam]);

  useEffect(() => {
    if(!selectTouched) return;
    urlHistory.replace(`${DomRoutes.songCatalogue}${selectedStation}`);
  }, [urlHistory, selectedStation, selectTouched]);

  useEffect(() => {
    if (!stationParam) return;
    const station = stationParam.toLowerCase();
    if(stations.items.some(s => s.name.toLowerCase() === station)) {
      setSelectedStation(stationParam);
      setSelectTouched(false);
      dispatch(fetchSongCatalogue({ station: stationParam }));
    }
  }, [stationParam, dispatch, setSelectedStation, setSelectTouched, stations]);

  return (
    <>
      <h1>SongCatalogue: {stationParam}</h1>
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
        status={songCatalogueStatus} 
        error={songCatalogueError} 
        isReady={!!stationParam}
      >
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Song</TableCell>
                <TableCell>Album</TableCell>
                <TableCell>Artist</TableCell>
                <TableCell>Request</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {songCatalogueObj.items.map((item, idx) => {
                return (
                  <TableRow key={`song_${idx}`}>
                    <TableCell>{item.song || "{No song name}"}</TableCell>
                    <TableCell>{item.album || "{No album name}"}</TableCell>
                    <TableCell>{item.artist || "{No artist name}"}</TableCell>
                    <TableCell>
                      <Button 
                        color="primary"
                        variant="contained"
                        onClick={() => dispatchSongRequest(item.id)}
                      >
                        Request
                      </Button>
                    </TableCell>
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
