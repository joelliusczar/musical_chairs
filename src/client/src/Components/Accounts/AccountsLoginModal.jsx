import React from "react";
import { Dialog } from "@mui/material";
import { LoginForm } from "./AccountsLoginForm";
import PropTypes from "prop-types";

export function LoginModal(props) {

	const { open, setOpen } = props;

	const closeModal = () => {
		setOpen(false);
	};


	return (
		<Dialog open={open} onClose={closeModal} >
			<LoginForm afterSubmit={closeModal} onCancel={closeModal}/>
		</Dialog>
	);
}

LoginModal.propTypes = {
	open: PropTypes.bool.isRequired,
	setOpen: PropTypes.func.isRequired,
};
