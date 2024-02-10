import React from "react";

export type ButtonE = HTMLButtonElement;
export type AnchorE = HTMLAnchorElement;
export type ListE = HTMLLIElement;
export type ClickEvent<EType> = React.MouseEvent<EType, MouseEvent>;
export type ButtonClickEvent = React.MouseEvent<ButtonE, MouseEvent>;
export type FileAttachEvent = React.FormEvent<HTMLInputElement>;

export type ChangeEvent = React.SyntheticEvent<Element, Event>;

export type CustomEvent<T> = {
	target: {
		name: string,
		value: T | null
	},
};

export type CustomFileAttachEvent = {
	target: {
		name: string,
		value: { file: File }[]
	},
};

export type FileListEvent = {
	target: {
		name: string,
		value: FileList | null
	},
};