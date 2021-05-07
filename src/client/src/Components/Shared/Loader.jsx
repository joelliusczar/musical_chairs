import React from "react";
import PropTypes from "prop-types";
import { CircularProgress, Typography } from "@material-ui/core";
import { CallStatus } from "../../constants";

const Loader = ({status, children, error, isReady}) => {

  if(!isReady) {
    return null;
  }

  try {
    switch(status) {
    case CallStatus.done:
      return children;
    case CallStatus.failed:
      return (<Typography color="error">{JSON.stringify(error)}</Typography>);
    default:
      return <CircularProgress />;
    }
  }
  catch(err) {
    return (<Typography color="error">{JSON.stringify(err)}</Typography>);
  } 
};

Loader.propTypes = {
  status: PropTypes.string,
  children: PropTypes.node,
  isReady: PropTypes.bool,
};

export default Loader;