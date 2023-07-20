import React, { useState } from "react";
import {
	Accordion,
	AccordionSummary,
	AccordionDetails,
	Box,
	Button,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { UserSearchModalOpener } from "../Accounts/UserSearch";
import { RoleView } from "./RoleView";
import { RoleEntry } from "./RoleEntry";
import PropTypes from "prop-types";




export const UserRoleAssignmentTable = (props) => {

	const {
		onUserSelect,
		users,
		removeRole,
		removeUser,
		availableRoles,
		addRole,
	} = props;
	const [showAddRole, setShowAddRole] = useState(false);

	return (
		<>
			{onUserSelect && <Box m={1}>
				<UserSearchModalOpener
					onConfirm={onUserSelect}
				/>
			</Box>}
			{!!users?.length && users.map((u, uidx) => {
				return (
					<Accordion
						className="user-role-container"
						key={`user${uidx}`}
						defaultExpanded={false}
						square
					>
						<AccordionSummary
							expandIcon={<ExpandMoreIcon />}
						>
							<Box component="span">
								{u.displayName || u.username}
								{removeUser && <Button
									onClick={() => removeUser(u)}
								>
									Remove
								</Button>}
							</Box>
						</AccordionSummary>
						<AccordionDetails>
							<>
								{!!u.roles?.length && u.roles.map((r, ridx) => {
									return (<Box
										key={`rule_${uidx}_${ridx}`}
										className="role-item"
									>
										<RoleView remove={r => removeRole(r, u)} data={r} />
									</Box>);
								})}
							</>
							<>
								{showAddRole
									? <Box className="role-item ">
										<RoleEntry
											save={(r) => addRole(r, u)}
											cancel={() => setShowAddRole(false)}
											availableRoles={availableRoles}
										/>
									</Box>
									: <Button onClick={() => setShowAddRole(true)}>
										Add Role
									</Button>
								}
							</>
						</AccordionDetails>
					</Accordion>);
			})}
		</>
	);
};

UserRoleAssignmentTable.propTypes = {
	onUserSelect: PropTypes.func,
	addRole: PropTypes.func.isRequired,
	removeRole: PropTypes.func.isRequired,
	removeUser: PropTypes.func,
	users: PropTypes.arrayOf(PropTypes.shape({
		username: PropTypes.string,
		displayName: PropTypes.string,
		roles: PropTypes.arrayOf(PropTypes.shape({
			name: PropTypes.string,
			span: PropTypes.number,
			count: PropTypes.number,
			priority: PropTypes.number,
		})),
	})).isRequired,
	availableRoles: PropTypes.arrayOf(PropTypes.shape({
		id: PropTypes.oneOfType([PropTypes.number,PropTypes.string]),
		name: PropTypes.string,
	})).isRequired,
};

