import React from "react";
import PropTypes from "prop-types";
import { CircularProgress, Typography } from "@mui/material";
import { CallStatus } from "../../constants";

const Loader = ({status, children, error}) => {

	try {
		switch(status) {
		case CallStatus.done:
			return children;
		case CallStatus.failed:
			return (<Typography color="error">
				{error}
			</Typography>);
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
	error: PropTypes.string,
};

export default Loader;