import React, { useState } from "react";
import {
	Button,
	ButtonGroup,
	Menu,
	MenuItem,
} from "@mui/material";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";

export const OptionsButton = (props) => {
	const { options, id } = props;
	const [selectedIndex, setSelectedIndex] = useState(0);
	const [anchorEl, setAnchorEl] = useState(null);

	const handleButtonClick = (e) => {
		options[selectedIndex].onClick && options[selectedIndex].onClick(e);
	};

	const handleMenuClick = (index) => {
		setSelectedIndex(index);
		setAnchorEl(null);
	};

	return <>
		{!!options && options.length > 0 ? (
			<>
				<ButtonGroup variant="contained">
					{typeof options[selectedIndex].onClick === "string" ?
						<Button
							component={Link}
							to={options[selectedIndex].onClick}
						>
							{options[selectedIndex].label}
						</Button>:
						<Button
							onClick={handleButtonClick}
						>
							{options[selectedIndex].label}
						</Button>
					}
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

OptionsButton.propTypes = {
	id: PropTypes.string.isRequired,
	options: PropTypes.arrayOf(PropTypes.shape({
		onClick: PropTypes.oneOfType([PropTypes.func, PropTypes.string]),
		label: PropTypes.string,
	})),
};