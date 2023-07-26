import React from "react";
import PropTypes from "prop-types";
import { Redirect } from "react-router-dom";
import { DomRoutes } from "../../constants";

export const ErrorComponent = (props) => {
	const { message } = props;
	return (
		<div>
			{message}
		</div>
	);
};

ErrorComponent.propTypes = {
	message: PropTypes.string,
};

export const GoToNotFound  = () => {
	return <Redirect to={`${DomRoutes.notFound()}`} />;
};

export const NotFound = () => {
	return (<ErrorComponent
		message={"Page not found."}
	/>);
};

export const NoPermissions = () => {
	return (<ErrorComponent
		message={"You do not have permission to view this page."}
	/>);
};

