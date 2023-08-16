import React from "react";
import {
	Autocomplete,
	TextField,
	FormHelperText,
	Theme,
	SxProps,
	AutocompleteFreeSoloValueMapping,
	AutocompleteValue
} from "@mui/material";
import {
	useController,
	UseFormReturn,
	FieldValues,
	FieldPath,
} from "react-hook-form";
import { SelectItem } from "../../Types/generic_types";
import { CustomEvent, ChangeEvent } from "../../Types/browser_types";

type TransformType
<
	T,
	Multiple extends boolean | undefined = false,
	DisableClearable extends boolean | undefined = false,
	FreeSolo extends boolean | undefined = false
> = {
	input: (
		value: AutocompleteValue<T, Multiple, DisableClearable, FreeSolo>
	) => AutocompleteValue<T, Multiple, DisableClearable, FreeSolo>,
	output: (
		e: CustomEvent<AutocompleteValue<T, Multiple, DisableClearable, FreeSolo>>
	) => CustomEvent<AutocompleteValue<T, Multiple, DisableClearable, FreeSolo>>
};

const defaultTransformFactory =
	<
		T,
		Multiple extends boolean | undefined = false,
		DisableClearable extends boolean | undefined = false,
		FreeSolo extends boolean | undefined = false
	>(): TransformType<T, Multiple, DisableClearable, FreeSolo> => ({
	input: (
		value: AutocompleteValue<T, Multiple, DisableClearable, FreeSolo>
	): AutocompleteValue<T, Multiple, DisableClearable, FreeSolo> => value,
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
	freeSolo?: FreeSolo,
	transform?: Partial<
		TransformType<OptionT, Multiple, DisableClearable, FreeSolo>
	>
	sx?: SxProps<Theme>
	options: OptionT[]
	isOptionEqualToValue?: (option: OptionT, value: OptionT) => boolean
	getOptionLabel?: GetOptionsLabelType<OptionT, FreeSolo>
	filterOptions?: (option: OptionT[]) => OptionT[]
	inputValue?: string
	onInputChange?: (e: ChangeEvent, newValue: string) => void
	renderOption?: (renderProps: any, option: OptionT) => JSX.Element
	getOptionDisabled?: (option: OptionT) => boolean
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
	OptionT extends T = T,
	Multiple extends boolean | undefined = false,
	DisableClearable extends boolean | undefined = false,
	FreeSolo extends boolean | undefined = false,
>
extends FormSelectBaseProps<T,
	FormT,
	OptionT,
	Multiple,
	DisableClearable,
	FreeSolo
> {
};

export type FormSelectPropsSelected<
	T,
	FormT extends FieldValues,
	OptionT extends T = T,
	Multiple extends boolean | undefined = false,
	DisableClearable extends boolean | undefined = false,
	FreeSolo extends boolean | undefined = false,
> = T extends SelectItem ?
		FormSelectPropsDefault<
			T,
			FormT,
			OptionT,
			Multiple,
			DisableClearable,
			FreeSolo
		> :
	 	FormSelectPropsUnconstained<
			T,
			FormT,
			OptionT,
			Multiple,
			DisableClearable,
			FreeSolo
		>

export function FormSelect
<T,
FormT extends FieldValues,
OptionT extends T = T,
Multiple extends boolean | undefined = false,
DisableClearable extends boolean | undefined = false,
FreeSolo extends boolean | undefined = false,
>
(props: FormSelectPropsSelected<
	T,
	FormT,
	OptionT,
	Multiple,
	DisableClearable,
	FreeSolo
>)
{
	const _getOptionLabel = (
		option: OptionT | AutocompleteFreeSoloValueMapping<FreeSolo>) => {
				if (option && typeof option === "string") {
					return option;
				}
				else if(!!option && typeof option === "object" && "name" in option) {
					return option.name
				}
				return "";
			};
	const {
		name,
		options,
		label,
		formMethods,
		transform,
		getOptionLabel = _getOptionLabel,
		freeSolo,
		...otherProps
	} = props;
	const { control } = formMethods;

	const { field, fieldState: { error } }
		= useController({
			name,
			control,
		});

	
	const _transform = {
		...defaultTransformFactory<OptionT, Multiple, DisableClearable, FreeSolo>(),
		...(transform || {})
	};

	return (
		<>
			<Autocomplete<OptionT, Multiple, DisableClearable, FreeSolo>
				id={field.name}
				options={options}
				getOptionLabel={getOptionLabel as any || _getOptionLabel}
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