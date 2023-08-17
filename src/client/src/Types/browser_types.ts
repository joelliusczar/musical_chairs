import React from "react";

export type ButtonE = HTMLButtonElement;
export type AnchorE = HTMLAnchorElement;
export type ListE = HTMLLIElement;
export type ClickEvent<EType> = React.MouseEvent<EType, MouseEvent>;
export type ButtonClickEvent = React.MouseEvent<ButtonE, MouseEvent>;

export type ChangeEvent = React.SyntheticEvent<Element, Event>;

export type CustomEvent<T> = {
	target: {
		name: string,
		value: T | null
	},
};