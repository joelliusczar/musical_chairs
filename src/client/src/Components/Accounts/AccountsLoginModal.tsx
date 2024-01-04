import React from "react";
import { Dialog } from "@mui/material";
import { LoginForm } from "./AccountsLoginForm";
import PropTypes from "prop-types";

type LoginModalProps = {
	open: boolean
	setOpen: (state: boolean) => void
	onCancel: (() => void) | null
};

export function LoginModal(props: LoginModalProps) {

	const { open, setOpen, onCancel } = props;

	const closeModal = () => {
		setOpen(false);
	};

	const handleCancel = () => {
		setOpen(false);
		onCancel && onCancel();
	};


	return (
		<Dialog open={open} onClose={closeModal} >
			<LoginForm afterSubmit={closeModal} onCancel={handleCancel}/>
		</Dialog>
	);
}

LoginModal.propTypes = {
	open: PropTypes.bool.isRequired,
	setOpen: PropTypes.func.isRequired,
	onCancel: PropTypes.func,
};