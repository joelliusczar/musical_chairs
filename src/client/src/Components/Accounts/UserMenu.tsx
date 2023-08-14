import React, { useState } from "react";
import { Menu, MenuItem, Button} from "@mui/material";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { DomRoutes } from "../../constants";
import {
	useCurrentUser,
	useLogin,
} from "../../Context_Providers/AuthContext";

export const UserMenu = (props) => {
	const { closeMenu, btnLabel } = props;
	const [, logout] = useLogin();
	const [anchorEl, setAnchorEl ] = useState(null);

	const user = useCurrentUser();

	const open = !!anchorEl;

	const _closeMenu = (e) => {
		closeMenu && closeMenu(e);
		setAnchorEl(null);
	};

	const logoutClick = (e) => {
		_closeMenu(e);
		logout();
	};

	const openUserMenu = (e) => {
		setAnchorEl(e.currentTarget);
	};

	return (
		<>
			<Button
				color="inherit"
				onClick={openUserMenu}
			>
				{btnLabel}
			</Button>
			<Menu
				open={open}
				anchorEl={anchorEl}
				onClose={_closeMenu}
			>
				<MenuItem
					component={Link}
					to={DomRoutes.accountsEdit({
						userKey: encodeURIComponent(user.username),
					})}
					onClick={_closeMenu}
				>
					Account Edit
				</MenuItem>
				<MenuItem onClick={logoutClick}>Logout</MenuItem>
			</Menu>
		</>
	);
};

UserMenu.propTypes = {
	anchorEl: PropTypes.object,
	closeMenu: PropTypes.func,
	btnLabel: PropTypes.string,
};