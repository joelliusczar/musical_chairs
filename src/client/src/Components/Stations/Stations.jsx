import React, { useEffect } from "react";
import { 
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Chip,
  Grid,
  makeStyles,
  Tooltip,
  Typography,
} from "@material-ui/core";
import Loader from "../Shared/Loader";
import { fetchStations } from "./stations_slice";
import { useDispatch, useSelector } from "react-redux";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import { CallStatus, DomRoutes } from "../../constants";
import { Link } from "react-router-dom";

const useStyles = makeStyles(() => ({
  buttons: {
    marginRight: 10,
  },
}));

export default function Stations(){

  const stationsStatus =  useSelector((appState) => appState.stations.status);
  const stationsError =  useSelector((appState) => appState.stations.error);
  const stations = useSelector((appState) => appState.stations.values);
  const dispatch = useDispatch();
  const classes = useStyles();

  useEffect(() => {
    if(!stationsStatus || stationsStatus === CallStatus.idle) { 
      dispatch(fetchStations());
    }
  }, [dispatch, stationsStatus]);

  return (<>
    <h1>Stations</h1>
    <Loader
      status={stationsStatus}
      error={stationsError}
      isReady
    >
      {stations.map((s, idx) => {
        return (<Accordion 
          key={`station_${idx}`}
          defaultExpanded={false}
          square
        >
          <AccordionSummary 
            expandIcon={<ExpandMoreIcon />}
          >
            <Typography>{s.name}</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div>
              <Grid container>
                <Grid item>
                  <Tooltip title={`${DomRoutes.songCatalogue}${s.name}`}>
                    <Link to={`${DomRoutes.songCatalogue}${s.name}`} 
                      component={Button}
                      color="primary"
                      variant="contained"
                      className={classes.buttons}
                    >
                      Song Catalogue
                    </Link>
                  </Tooltip>
                </Grid>
                <Grid item>
                  <Tooltip title={`${DomRoutes.history}${s.name}`}>
                    <Link to={`${DomRoutes.history}${s.name}`} 
                      component={Button}
                      color="primary"
                      variant="contained"
                      className={classes.buttons}
                    >
                      Song History
                    </Link>
                  </Tooltip>
                </Grid>
                <Grid item>
                  <Tooltip title={`${DomRoutes.queue}${s.name}`}>
                    <Link 
                      to={`${DomRoutes.queue}${s.name}`} 
                      component={Button}
                      color="primary"
                      variant="contained"
                      className={classes.buttons}
                    >
                      Song Queue
                    </Link>
                  </Tooltip>
                </Grid>
              </Grid>
              <Typography display="block">Tags:</Typography>
              <div>
                {(s.tags || []).map((t,idx) => {
                  return (<Chip 
                    key={`tag_${idx}`} 
                    label={t.name}
                    className={classes.buttons}
                  />);
                })}
              </div>
            </div>
          </AccordionDetails>
        </Accordion>);
      })}
    </Loader>
  </>);
}