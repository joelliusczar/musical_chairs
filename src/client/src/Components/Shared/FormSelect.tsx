import React from "react";
import {
	Autocomplete,
	TextField,
	FormHelperText,
	Theme,
	SxProps,
	AutocompleteFreeSoloValueMapping,
	AutocompleteValue,
	AutocompleteProps,
	AutocompleteRenderInputParams,
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


interface FormSelectBaseProps<
	T,
	FormT extends FieldValues,
	Multiple extends boolean | undefined = false,
	DisableClearable extends boolean | undefined = false,
	FreeSolo extends boolean | undefined = false,
> extends Partial<AutocompleteProps<T, Multiple, DisableClearable, FreeSolo>> {
	name: FieldPath<FormT>
	label: string
	formMethods: UseFormReturn<FormT>
	freeSolo?: FreeSolo,
	multiple?: Multiple,
	transform?: Partial<
		TransformType<T, Multiple, DisableClearable, FreeSolo>
	>
	sx?: SxProps<Theme>
	options: T[]
	isOptionEqualToValue?: (option: T, value: T) => boolean
	getOptionLabel?: (
		option: T | AutocompleteFreeSoloValueMapping<FreeSolo>
	) => string
	filterOptions?: (option: T[]) => T[]
	inputValue?: string
	onInputChange?: (e: ChangeEvent, newValue: string) => void,
	renderInput?: (params: AutocompleteRenderInputParams) => React.ReactNode,
}


export interface FormSelectPropsDefault
<
	T extends SelectItem,
	FormT extends FieldValues,
	Multiple extends boolean | undefined = false,
	DisableClearable extends boolean | undefined = false,
	FreeSolo extends boolean | undefined = false,
>
extends FormSelectBaseProps<
	T,
	FormT,
	Multiple,
	DisableClearable,
	FreeSolo
> {}

export interface FormSelectPropsUnconstained
<
	T,
	FormT extends FieldValues,
	Multiple extends boolean | undefined = false,
	DisableClearable extends boolean | undefined = false,
	FreeSolo extends boolean | undefined = false,
>
extends FormSelectBaseProps<T,
	FormT,
	Multiple,
	DisableClearable,
	FreeSolo
> {
}

export type FormSelectPropsSelected<
	T,
	FormT extends FieldValues,
	Multiple extends boolean | undefined = false,
	DisableClearable extends boolean | undefined = false,
	FreeSolo extends boolean | undefined = false,
> = T extends SelectItem ?
		FormSelectPropsDefault<
			T,
			FormT,
			Multiple,
			DisableClearable,
			FreeSolo
		> :
		FormSelectPropsUnconstained<
			T,
			FormT,
			Multiple,
			DisableClearable,
			FreeSolo
		>

export function FormSelect
<T,
FormT extends FieldValues,
Multiple extends boolean | undefined = false,
DisableClearable extends boolean | undefined = false,
FreeSolo extends boolean | undefined = false,
>
(props: FormSelectPropsSelected<
	T,
	FormT,
	Multiple,
	DisableClearable,
	FreeSolo
>)
{
	const _getOptionLabel = (
		option: T | AutocompleteFreeSoloValueMapping<FreeSolo>
	) => {
		if (option && typeof option === "string") {
			return option;
		}
		else if(!!option && typeof option === "object" && "name" in option) {
			return option.name as string;
		}
		return "";
	};

	const _renderInput = (params: AutocompleteRenderInputParams) => {
		return <TextField
			{...params}
			label={label}
			variant="standard"
		/>;
	};
	const {
		name,
		options,
		label,
		formMethods,
		transform,
		getOptionLabel = _getOptionLabel,
		freeSolo,
		renderInput,
		...otherProps
	} = props;
	const { control } = formMethods;

	const { field, fieldState: { error } }
		= useController({
			name,
			control,
		});


	const _transform = {
		...defaultTransformFactory<T, Multiple, DisableClearable, FreeSolo>(),
		...(transform || {}),
	};

	return (
		<>
			<Autocomplete<T, Multiple, DisableClearable, FreeSolo>
				id={field.name}
				options={options}
				getOptionLabel={getOptionLabel || _getOptionLabel}
				onChange={(e, value) => field.onChange(_transform.output({
					target: { name: field.name, value: value} ,
				}))}
				onBlur={field.onBlur}
				value={_transform.input(field.value)}
				freeSolo={freeSolo}
				renderInput={renderInput || _renderInput}
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