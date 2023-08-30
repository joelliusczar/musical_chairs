import React, { useState } from "react";
import {
	Button,
	ButtonGroup,
	Menu,
	MenuItem,
} from "@mui/material";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import { Link } from "react-router-dom";
import { ButtonClickEvent } from "../../Types/browser_types";

interface OptionBase {
	onClick?: (e: ButtonClickEvent) => void | Promise<void>,
	label?: string
}

interface LinkOption extends OptionBase {
	link: string,
	href?: undefined,
}

interface HrefOption extends OptionBase {
	link?: undefined,
	href: string,
}

interface ClickOnlyOption extends OptionBase {
	onClick: (e: ButtonClickEvent) => void | Promise<void>,
	link?: undefined,
	href?: undefined,
}

type OptionsButton = {
	id: string,
	options: (LinkOption | HrefOption | ClickOnlyOption)[]
}

export const OptionsButton = (props: OptionsButton) => {
	const { options, id } = props;
	const [selectedIndex, setSelectedIndex] = useState(0);
	const [anchorEl, setAnchorEl] = useState<
		EventTarget & HTMLButtonElement | null
	>(null);

	const handleButtonClick = (e: ButtonClickEvent) => {
		setAnchorEl(null);
		if (options.length < selectedIndex || selectedIndex < 0) {
			return;
		}
		const option = options[selectedIndex];
		option.onClick && option.onClick(e);
	};

	const handleMenuClick = (index: number) => {
		setSelectedIndex(index);
		setAnchorEl(null);
	};


	const linkConfig = options[selectedIndex].href ?
		{ href: options[selectedIndex].href } :
		options[selectedIndex].link ?
			{ component: Link, to: options[selectedIndex].link } :
			null;

	return <>
		{!!options && options.length > 0 ? (
			<>
				<ButtonGroup variant="contained">
					<Button
						onClick={handleButtonClick}
						{...linkConfig}
					>
						{options[selectedIndex].label}
					</Button>
					<Button
						size="small"
						onClick={e => setAnchorEl(e.currentTarget)}
					>
						<ArrowDropDownIcon />
					</Button>
				</ButtonGroup>
				<Menu
					open={!!anchorEl}
					anchorEl={anchorEl}
					onClose={() => setAnchorEl(null)}
				>
					{options.map((o, i) => {
						return <MenuItem
							onClick={() => handleMenuClick(i)}
							key={`${id}_${i}`}>
							{o.label}
						</MenuItem>;
					})}
				</Menu>
			</>) :
			<Button variant="contained" disabled>
				No Options
			</Button>
		}
	</>;
};
