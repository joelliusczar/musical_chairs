import React from "react";
import PropTypes from "prop-types";
import { useHistory, useLocation, Link } from "react-router-dom";
import { MenuItem,
	Select,
	Pagination,
	PaginationItem,
} from "@mui/material";
import {
	getRowsCount,
	getPageCount,
} from "../../Helpers/pageable_helpers";

export const UrlPagination = (props) => {

	const { getPageUrl, totalRows } = props;

	const urlHistory = useHistory();
	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const page = parseInt(queryObj.get("page") || "1");

	return (
		<>
			<Select
				displayEmpty
				defaultValue={50}
				label="Row Count"
				onChange={(e) => {
					urlHistory.replace(
						getPageUrl(
							{ rows: e.target.value, page: 1 },
							location.search
						)
					);
				}}
				renderValue={(v) => v || "Select Row Count"}
				value={getRowsCount(location.search)}
			>
				{[10, 50, 100, 1000].map((size) => {
					return (<MenuItem key={`size_${size}`} value={size}>
						{size}
					</MenuItem>);
				})}
			</Select>
			<Pagination
				count={getPageCount(
					location.search,
					totalRows
				)}
				page={page}
				renderItem={item => {
					return (<PaginationItem
						component={Link}
						to={getPageUrl(
							{ page: item.page },
							location.search
						)}
						{...item} />);
				} }
				sx={{}} />
		</>
	);
};

UrlPagination.propTypes = {
	getPageUrl: PropTypes.func,
	totalRows: PropTypes.number,
};