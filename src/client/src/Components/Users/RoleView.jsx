import React from "react";
import PropTypes from "prop-types";
import { Paper, Button, Box } from "@mui/material";
import { buildTimespanMsg, secondsToTuple } from "../../Helpers/time_helper";

export const RoleView = (props) => {

	const { data, remove } = props;

	const limitLabel = (span, count) => {
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

RoleView.propTypes = {
	data: PropTypes.shape({
		name: PropTypes.string,
		span: PropTypes.number,
		count: PropTypes.number,
		priority: PropTypes.number,
	}),
	remove: PropTypes.func.isRequired,
};