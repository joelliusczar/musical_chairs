import React from "react";
import { Menu, MenuItem } from "@mui/material";
import PropTypes from "prop-types";
import { useDispatch, useSelector } from "react-redux";
import { logout } from "./accounts_slice";
import { Link } from "react-router-dom";
import { DomRoutes } from "../../constants";
import { currentUserSelector } from "./accounts_slice";

export function UserMenu(props) {
	const { anchorEl } = props;
	const dispatch = useDispatch();
	const user = useSelector(currentUserSelector);

	const open = !!anchorEl;

	const logoutClick = () => {
		dispatch(logout());
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
}

UserMenu.propTypes = {
	anchorEl: PropTypes.object,
	closeMenu: PropTypes.func,
};