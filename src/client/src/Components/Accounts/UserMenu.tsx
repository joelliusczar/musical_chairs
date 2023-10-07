import React, { useState } from "react";
import { Menu, MenuItem, Button} from "@mui/material";
import { Link } from "react-router-dom";
import { DomRoutes } from "../../constants";
import {
	useCurrentUser,
	useLogin,
} from "../../Context_Providers/AuthContext";
import {
	ButtonClickEvent,
	ClickEvent,
	ListE,
} from "../../Types/browser_types";

type UserMenuProps = {
	closeMenu: <EType>(e: ClickEvent<EType>) => void
	btnLabel: string
};

export const UserMenu = (props: UserMenuProps) => {
	const { closeMenu, btnLabel } = props;
	const [, logout] = useLogin();
	const [anchorEl, setAnchorEl ] = useState<
		(EventTarget & HTMLButtonElement) | null
			>(null);

	const user = useCurrentUser();

	const open = !!anchorEl;

	const _closeMenu = <EType,>(e: ClickEvent<EType>) => {
		closeMenu && closeMenu(e);
		setAnchorEl(null);
	};

	const logoutClick = (e: ClickEvent<ListE>) => {
		_closeMenu(e);
		logout();
	};

	const openUserMenu = (e: ButtonClickEvent) => {
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
						subjectuserkey: encodeURIComponent(user.username),
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
