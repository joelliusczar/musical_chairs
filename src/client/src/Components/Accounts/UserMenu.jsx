import React from "react";
import { Menu, MenuItem } from "@mui/material";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { DomRoutes } from "../../constants";
import {
	useCurrentUser,
	useLogin,
} from "../../Context_Providers/AuthContext";

export const UserMenu = (props) => {
	const { anchorEl, closeMenu } = props;
	const [, logout] = useLogin();

	const user = useCurrentUser();

	const open = !!anchorEl;

	const logoutClick = () => {
		closeMenu && closeMenu();
		logout();
	};

	return (
		<Menu
			open={open}
			anchorEl={anchorEl}
		>
			<MenuItem
				component={Link}
				to={`${DomRoutes.accountsEdit}/${user.userId}`}
			>
				Account Edit
			</MenuItem>
			<MenuItem onClick={logoutClick}>Logout</MenuItem>
		</Menu>
	);
};

UserMenu.propTypes = {
	anchorEl: PropTypes.object,
	closeMenu: PropTypes.func,
};