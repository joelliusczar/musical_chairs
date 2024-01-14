import React, { useContext } from "react";
import { NoPermissions } from "./RoutingErrors";
import {
	useCurrentUser,
	useHasAnyRoles,
	AuthContext,
} from "../../Context_Providers/AuthContext/AuthContext";
import { Loader } from "./Loader";

type PrivateRouteTypes = {
	scopes: string[],
	element: JSX.Element
};

export const PrivateRoute = (props: PrivateRouteTypes) => {
	const { scopes, element } = props;
	const {
		state: { error, callStatus },
	} = useContext(AuthContext);
	const currentUser = useCurrentUser();
	const hasAnyRoles = useHasAnyRoles(scopes);
	return (
		<Loader status={callStatus} error={error}>
			{currentUser.username && hasAnyRoles ?
				<>
					{element}
				</> :
				<NoPermissions />
			}
		</Loader>
	);
};
