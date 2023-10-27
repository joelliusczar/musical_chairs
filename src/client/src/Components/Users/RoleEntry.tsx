import React from "react";
import PropTypes from "prop-types";
import { Paper, Button, Box } from "@mui/material";
import { useForm } from "react-hook-form";
import { FormTextField } from "../Shared/FormTextField";
import { FormSelect } from "../Shared/FormSelect";
import { Named, SelectItem } from "../../Types/generic_types";
import { ActionRuleCreationInfo } from "../../Types/user_types";
import { SubmitButton } from "../Shared/SubmitButton";


const initialValues = {
	role: {
		id: "",
		name: "",
	},
	days: 0,
	hours: 0,
	minutes: 0,
	count: 0,
};

type RoleEntryProps = {
	save: (rule: ActionRuleCreationInfo) => void,
	cancel: () => void,
	availableRoles: SelectItem[]
};

export const RoleEntry = (props: RoleEntryProps) => {

	const { save, cancel, availableRoles } = props;

	const formMethods = useForm({
		defaultValues: initialValues,
	});
	const { handleSubmit, reset, formState } = formMethods;
	const callSubmit = handleSubmit(values => {

		const span = values.minutes * 60 + values.hours * 60 * 60
			+ values.days * 60 * 60 * 24;
		save({
			name: values.role.id,
			count: values.count,
			span: span,
		});
	});

	const handleCancel = () => {
		reset(initialValues);
		cancel && cancel();
	};

	return (<Paper className="rule-entry-body" elevation={3}>
		<Box className="rule-name-input">
			<FormSelect
				name="role"
				label="Role"
				options={availableRoles}
				formMethods={formMethods}
				getOptionLabel={(option: Named) => option ? option.name : ""}
				sx={{ width: 195 }}
				isOptionEqualToValue={(option, value) => {
					return option.id === value.id;
				}}
			/>
		</Box>
		<Box className="rule-entry">
			<Box className="rule-entry-first-text">
				This action can be invoked
			</Box>
			<FormTextField
				className="small-number-input"
				name="count"
				label="Count"
				type="number"
				min="0"
				formMethods={formMethods}
			/>
			<Box component="span" className="between-text">times per</Box>
			<FormTextField
				className="small-number-input"
				name="hours"
				label="Hours"
				type="number"
				min="0"
				formMethods={formMethods}
			/>


			<FormTextField
				className="small-number-input"
				name="days"
				label="Days"
				type="number"
				min="0"
				formMethods={formMethods}
			/>
			<FormTextField
				className="small-number-input"
				name="minutes"
				label="Minutes"
				type="number"
				min="0"
				formMethods={formMethods}
			/>
		</Box>
		<Box>
			<Button
				onClick={handleCancel}
			>
				Cancel
			</Button>
			<SubmitButton
				loading={formState.isSubmitting}
				onClick={callSubmit}
			>
				Save
			</SubmitButton>
		</Box>
	</Paper>);

};

RoleEntry.propTypes = {
	save: PropTypes.func.isRequired,
	cancel: PropTypes.func.isRequired,
	availableRoles: PropTypes.arrayOf(PropTypes.shape({
		id: PropTypes.oneOfType([PropTypes.number,PropTypes.string]),
		name: PropTypes.string,
	})).isRequired,
};