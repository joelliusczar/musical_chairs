import React from "react";
import { Menu, MenuItem } from "@mui/material";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { logout } from "./accounts_slice";

export function UserMenu(props) {
	const { anchorEl } = props;
	const dispatch = useDispatch();

	const open = !!anchorEl;

	const logoutClick = () => {
		dispatch(logout());
	};

	return (
		<Menu
			open={open}
			anchorEl={anchorEl}
		>
			<MenuItem onClick={logoutClick}>Logout</MenuItem>
		</Menu>
	);
}

UserMenu.propTypes = {
	anchorEl: PropTypes.object,
	closeMenu: PropTypes.func,
};