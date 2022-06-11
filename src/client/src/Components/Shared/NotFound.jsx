import React from "react";
import { Redirect } from "react-router-dom";
import { DomRoutes } from "../../constants";

export const GoToNotFound  = () => {
	return <Redirect to={`${DomRoutes.notFound}`} />;
};

export const NotFound = () => {
	return (
		<div>
			Page not found
		</div>
	);
};