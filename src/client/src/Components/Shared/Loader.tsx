import React from "react";
import PropTypes from "prop-types";
import { CircularProgress, Typography } from "@mui/material";
import { CallStatus } from "../../constants";

export const Loader = ({status, children, error, defaultEmptyMessage}) => {

	switch(status) {
	case CallStatus.done:
		return children;
	case CallStatus.failed:
		return (<Typography color="error">
			{error}
		</Typography>);
	case CallStatus.loading:
		return <CircularProgress />;
	default:
		if (error) {
			return (<Typography color="error">{JSON.stringify(error)}</Typography>);
		}
		return <Typography>
			{defaultEmptyMessage !== undefined ?
				defaultEmptyMessage : "No records have been fetched."}
		</Typography>;
	}
};

Loader.propTypes = {
	status: PropTypes.string,
	children: PropTypes.oneOfType([
		PropTypes.arrayOf(PropTypes.node),
		PropTypes.node,
	]).isRequired,
	error: PropTypes.string,
	defaultEmptyMessage: PropTypes.string,
};

export default Loader;