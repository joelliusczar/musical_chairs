import React from "react";
import { Route, NavLink } from "react-router-dom";
import PropTypes from "prop-types";
import { ListItem } from "@mui/material";
import { NoPermissions } from "./RoutingErrors";
import {
	useCurrentUser,
	useHasAnyRoles,
} from "../../Context_Providers/AuthContext";



export const PrivateRoute = (props) => {
	const { scopes, children, ...routeProps } = props;
	const currentUser = useCurrentUser();
	const hasAnyRoles = useHasAnyRoles(scopes);
	return (
		<>
			{currentUser.username && hasAnyRoles ?
				<Route {...routeProps}>
					{children}
				</Route> :
				<NoPermissions />
			}
		</>
	);
};

PrivateRoute.propTypes = {
	scopes: PropTypes.arrayOf(PropTypes.string),
	children: PropTypes.oneOfType([
		PropTypes.arrayOf(PropTypes.node),
		PropTypes.node,
	]).isRequired,
};

export const PrivateNavLink = (props) => {
	const { scopes, children, ...navLinkProps } = props;
	const currentUser = useCurrentUser();
	const hasAnyRoles = useHasAnyRoles(scopes);
	return (
		<>
			{currentUser.username && hasAnyRoles &&
			<ListItem button component={NavLink} {...navLinkProps}>
				{children}
			</ListItem>}
		</>
	);
};

PrivateNavLink.propTypes = {
	scopes: PropTypes.arrayOf(PropTypes.string),
	children: PropTypes.oneOfType([
		PropTypes.arrayOf(PropTypes.node),
		PropTypes.node,
	]).isRequired,
};