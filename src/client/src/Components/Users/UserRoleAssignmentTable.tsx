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
import {
	ActionRule,
	RoledUser,
	ActionRuleCreationInfo,
} from "../../Types/user_types";
import { SelectItem } from "../../Types/generic_types";


interface UserRoleAssignmentTableProps {
	onUserSelect?: (selected: RoledUser | null) => void | Promise<void>
	users: RoledUser[]
	removeRole: (role: ActionRule, user: RoledUser) => void
	removeUser?: (user: RoledUser) => void
	availableRoles: SelectItem[]
	addRole: (
		role: ActionRuleCreationInfo, 
		user: RoledUser
	) => void | Promise<void>,
}

export const UserRoleAssignmentTable = (
	props: UserRoleAssignmentTableProps
) => {

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
			{!!users?.length && users.map((u, uidx: number) => {
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
								{u.displayname || u.username}
								{removeUser && <Button
									onClick={() => removeUser(u)}
								>
									Remove
								</Button>}
							</Box>
						</AccordionSummary>
						<AccordionDetails>
							<>
								{!!u.roles?.length && u.roles.map((
									r: ActionRule,
									ridx: number
								) => {
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
