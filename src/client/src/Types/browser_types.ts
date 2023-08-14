import React from "react";

export type ClickEvent = React.MouseEvent<HTMLButtonElement, MouseEvent>;

export type ChangeEvent = React.SyntheticEvent<Element, Event>;

export type CustomEvent<T> = {
	target: {
		name: string,
		value: T | null
	},
};