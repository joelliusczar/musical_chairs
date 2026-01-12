import React from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { MenuItem,
	Select,
	Pagination,
	PaginationItem,
} from "@mui/material";
import {
	getRowsCount,
	getPageCount,
} from "../../Helpers/pageable_helpers";
import { PageableParams } from "../../Types/pageable_types";

type CurrentPageParams = Pick<PageableParams, "page" | "limit"> |
	Pick<PageableParams, "page">;

type UrlPaginationProps = {
	getPageUrl: (
		params: CurrentPageParams,
		currentLocation: string,
		currentPathName: string,
	) => string,
	totalRows: number
};

export const UrlPagination = (props: UrlPaginationProps) => {

	const { getPageUrl, totalRows } = props;

	const navigate = useNavigate();
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
					navigate(
						getPageUrl(
							{
								limit: e.target.value ? +e.target.value : undefined,
								page: 1,
							},
							location.search,
							location.pathname
						),
						{ replace: true }
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
							location.search,
							location.pathname
						)}
						{...item} />);
				} }
				sx={{}} />
		</>
	);
};
