import React, { lazy, Suspense } from "react";
import { Dialog } from "@mui/material";
const LoginForm = lazy(() => import("./AccountsLoginForm"));;


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
		<Dialog open={open} onClose={handleCancel} >
			<Suspense fallback={<div>Loading...</div>} >
				<LoginForm afterSubmit={closeModal} onCancel={handleCancel}/>
			</Suspense>
		</Dialog>
	);
}
