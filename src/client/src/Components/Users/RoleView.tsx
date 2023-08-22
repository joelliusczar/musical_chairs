import React from "react";
import { Paper, Button, Box } from "@mui/material";
import { buildTimespanMsg, secondsToTuple } from "../../Helpers/time_helper";
import { ActionRule} from "../../Types/user_types";


type RoleViewProps = {
	data: ActionRule,
	remove: (r: ActionRule) => void
};

export const RoleView = (props: RoleViewProps) => {

	const { data, remove } = props;

	const limitLabel = (span: number, count: number) => {
		if (span === 0 && count === 0) return "No Limit";
		if (span !== 0 && count === 0) return "Blocked";
		const timespanMsg = buildTimespanMsg(secondsToTuple(span));
		if (count === 1) {
			return "This action can be invoked" +
			` once per ${timespanMsg}`;
		}
		return "This action can be invoked" +
			` ${count} times per ${timespanMsg}`;
	};

	return (<Paper className="rule-body" elevation={3}>
		<Box>
			<Box component="span" className="rule-name">
				{data.name}
			</Box>
			<Button
				onClick={() => remove(data)}
			>
				Remove
			</Button>
		</Box>
		<Box>
			<Box>
				{limitLabel(data.span, data.count)}
			</Box>
			<Box>
			</Box>
		</Box>
	</Paper>);

};
