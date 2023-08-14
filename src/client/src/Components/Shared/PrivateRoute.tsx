import React, { useContext } from "react";
import { Route } from "react-router-dom";
import PropTypes from "prop-types";
import { NoPermissions } from "./RoutingErrors";
import {
	useCurrentUser,
	useHasAnyRoles,
	AuthContext,
} from "../../Context_Providers/AuthContext";
import { Loader } from "./Loader";

type PrivateRouteTypes = {
	path: string,
	scopes: string[],
	element: JSX.Element,
	children?: JSX.Element | JSX.Element[]
};

export const PrivateRoute = (props: PrivateRouteTypes) => {
	const { scopes, element, children, ...routeProps } = props;
	const {
		state: { error, callStatus },
	} = useContext(AuthContext);
	const currentUser = useCurrentUser();
	const hasAnyRoles = useHasAnyRoles(scopes);
	return (
		<Loader status={callStatus} error={error}>
			{currentUser.username && hasAnyRoles ?
				<Route
					element={element}
					{...routeProps}
				>
					{children}
				</Route> :
				<NoPermissions />
			}
		</Loader>
	);
};

PrivateRoute.propTypes = {
	scopes: PropTypes.arrayOf(PropTypes.string),
	element: PropTypes.node.isRequired,
	children: PropTypes.oneOfType([
		PropTypes.arrayOf(PropTypes.node),
		PropTypes.node,
	]),
};