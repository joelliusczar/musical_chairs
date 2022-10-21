import React from "react";
import PropTypes from "prop-types";
import { CircularProgress, Typography } from "@mui/material";
import { CallStatus } from "../../constants";

const Loader = ({status, children, error}) => {

	switch(status) {
	case CallStatus.done:
		return children;
	case CallStatus.failed:
		return (<Typography color="error">
			{error}
		</Typography>);
	default:
		if (error) {
			return (<Typography color="error">{JSON.stringify(error)}</Typography>);
		}
		return <CircularProgress />;
	}
};

Loader.propTypes = {
	status: PropTypes.string,
	children: PropTypes.oneOfType([
		PropTypes.arrayOf(PropTypes.node),
		PropTypes.node,
	]).isRequired,
	error: PropTypes.string,
};

export default Loader;