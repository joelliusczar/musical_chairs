import React from "react";
import PropTypes from "prop-types";
import { Navigate } from "react-router-dom";
import { DomRoutes } from "../../constants";

type ErrorComponentTypes = {
	message: string
};

export const ErrorComponent = (props: ErrorComponentTypes) => {
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
	return <Navigate to={`${DomRoutes.notFound()}`} />;
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