import React, { useContext } from "react";
import { Route, NavLink } from "react-router-dom";
import PropTypes from "prop-types";
import { ListItem } from "@mui/material";
import { NoPermissions } from "./RoutingErrors";
import {
	useCurrentUser,
	useHasAnyRoles,
	AuthContext,
} from "../../Context_Providers/AuthContext";
import { Loader } from "../Shared/Loader";



export const PrivateRoute = (props) => {
	const { scopes, children, ...routeProps } = props;
	const {
		state: { error, callStatus },
	} = useContext(AuthContext);
	const currentUser = useCurrentUser();
	const hasAnyRoles = useHasAnyRoles(scopes);
	return (
		<Loader status={callStatus} error={error}>
			{currentUser.username && hasAnyRoles ?
				<Route {...routeProps}>
					{children}
				</Route> :
				<NoPermissions />
			}
		</Loader>
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