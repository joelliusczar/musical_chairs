import React from "react";
import {
	Autocomplete,
	TextField,
	FormHelperText,
	Theme,
	SxProps,
	AutocompleteFreeSoloValueMapping
} from "@mui/material";
import {
	useController,
	UseFormReturn,
	FieldValues,
	FieldPath,
} from "react-hook-form";
import { Named, SelectItem } from "../../Types/generic_types";
import { CustomEvent, ChangeEvent } from "../../Types/browser_types";

type TransformType<T> = {
	input: (value: T) => T,
	output: (
		e: CustomEvent<T>
	) => CustomEvent<T>
};

const defaultTransformFactory =
	<T,>(): TransformType<T> => ({
	input: (value: T): T => value,
	output: (
		e
	) => e,
});

type GetOptionsLabelType<
	OptionT,
	FreeSolo extends boolean | undefined = false
> =
	FreeSolo extends false | undefined ?
	(option: OptionT) => string :
	(option: OptionT | AutocompleteFreeSoloValueMapping<FreeSolo>) => string;

interface FormSelectBaseProps<
	T,
	FormT extends FieldValues,
	OptionT extends T = T,
	Multiple extends boolean | undefined = false,
	DisableClearable extends boolean | undefined = false,
	FreeSolo extends boolean | undefined = false,
> {
	name: FieldPath<FormT>
	label: string
	formMethods: UseFormReturn<FormT>
	transform?: TransformType<OptionT>
	sx?: SxProps<Theme>
	options: OptionT[]
	isOptionEqualToValue?: (option: OptionT, value: OptionT) => boolean
	getOptionLabel: GetOptionsLabelType<OptionT, FreeSolo>
	filterOptions?: (option: OptionT[]) => OptionT[]
	inputValue?: string
	onInputChange?: (e: ChangeEvent, newValue: string) => void
	freeSolo: FreeSolo,
	// renderOption?: (renderProps: any, option: OptionT) => JSX.Element
	// getOptionDisabled?: (option: OptionT) => boolean
	[key: string]: any
}


export interface FormSelectPropsDefault
<
	T extends SelectItem,
	FormT extends FieldValues,
	OptionT extends T = T,
	Multiple extends boolean | undefined = false,
	DisableClearable extends boolean | undefined = false,
	FreeSolo extends boolean | undefined = false,
>
extends FormSelectBaseProps<
	T,
	FormT,
	OptionT,
	Multiple,
	DisableClearable,
	FreeSolo
> {};

export interface FormSelectPropsUnconstained
<
	T,
	FormT extends FieldValues,
	OptionT extends T = T
>
extends FormSelectBaseProps<T, FormT, OptionT> {
	getOptionLabel: (option: OptionT) => string
};

type SelectedPropTypes<
	T,
	FormT extends FieldValues,
	OptionT extends T = T
> = T extends SelectItem ?
		FormSelectPropsDefault<T, FormT, OptionT> :
	 	FormSelectPropsUnconstained<T, FormT, OptionT>

export function FormSelect
<T extends SelectItem,
FormT extends FieldValues,
OptionT extends T = T,
Multiple extends boolean | undefined = false,
DisableClearable extends boolean | undefined = false,
FreeSolo extends boolean | undefined = false,
>
(props: FormSelectPropsDefault<
	T,
	FormT,
	OptionT,
	Multiple,
	DisableClearable,
	FreeSolo
>)
{
	const {
		name,
		options,
		label,
		formMethods,
		transform,
		getOptionLabel,
		freeSolo,
		...otherProps
	} = props;
	const { control } = formMethods;

	const { field, fieldState: { error } }
		= useController({
			name,
			control,
		});

	const _getOptionLabel = (option: OptionT | AutocompleteFreeSoloValueMapping<FreeSolo>) => {
				if (option && typeof option === "string") {
					return option;
				}
				else if(typeof option === "object" && "name" in option) {
					return option.name
				}
				return "";
			};
	const _transform = {
		...defaultTransformFactory<OptionT>(),
		...(transform || {})
	};

	return (
		<>
			<Autocomplete<OptionT, Multiple, DisableClearable, FreeSolo>
				id={field.name}
				options={options}
				getOptionLabel={_getOptionLabel}
				onChange={(e, value) => field.onChange(_transform.output({
					target: { name: field.name, value: value} ,
				}))}
				onBlur={field.onBlur}
				value={_transform.input(field.value)}
				freeSolo={freeSolo}
				renderInput={(params) => {
					return <TextField
						{...params}
						label={label}
						variant="standard"
					/>;
				}}
				componentsProps={{
					popper: {
						style: { minWidth: "fit-content" },
						placement: "bottom-start",
					},
					paper: {
						style: { lineHeight: "unset" },
					},
				}}
				{...otherProps}
			/>
			{error && <FormHelperText error={true}>
				{error?.message}
			</FormHelperText>}
		</>
	);
}