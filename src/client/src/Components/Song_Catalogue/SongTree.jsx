import React, {useReducer, useEffect } from "react";
import { TreeView, TreeItem } from "@mui/lab";
import {
	waitingReducer,
	listDataInitialState,
	dispatches,
} from "../Shared/waitingReducer";
import { fetchSongDir } from "./songInfoService";
import Loader from "../Shared/Loader";
import PropTypes from "prop-types";

export const SongDirectory = (props) => {
	const { prefix, level, dirIdx } = props;
	const [state, dispatch] = useReducer(waitingReducer(), listDataInitialState);
	const { callStatus } = state;

	useEffect(() => {
		const fetch = async () => {
			try {
				if(!callStatus) {
					dispatch(dispatches.started());
					const data = await fetchSongDir({ params: { prefix } });
					dispatch(dispatches.done(data));
				}
			}
			catch(err) {
				dispatch(dispatches.failed(err.response.data.detail[0].msg));
			}
		};
		fetch();
	}, [callStatus, dispatch, prefix]);

	return (
		<Loader status={callStatus} error={state.error}>
			{state.data.items.map((d, idx) => {
				const key = `${level}_${dirIdx}_${idx}`;
				const label = d.path.replace(prefix, "");
				return (
					<TreeItem nodeId={key} key={key} label={label}>
						{d.totalChildCount > 0 ?
							<SongDirectory
								prefix={d.path}
								level={level + 1}
								dirIdx={idx}
							/> :
							<span>??</span>
						}
					</TreeItem>
				);
			})}
		</Loader>
	);
};

SongDirectory.propTypes = {
	prefix: PropTypes.string,
	level: PropTypes.number,
	dirIdx: PropTypes.number,
};

export const SongTree = () => {
	return (
		<TreeView>
			<SongDirectory prefix="" level={0} dirIdx={0} />
		</TreeView>
	);
};