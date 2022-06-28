import React, {useReducer, useEffect, useState } from "react";
import { Box, Button, AppBar, Toolbar } from "@mui/material";
import { TreeView, TreeItem } from "@mui/lab";
import {
	waitingReducer,
	listDataInitialState,
	dispatches,
} from "../Shared/waitingReducer";
import { fetchSongDir } from "./songInfoService";
import Loader from "../Shared/Loader";
import PropTypes from "prop-types";
import { drawerWidth } from "../../style_config";
import { withCacheProvider, useCache } from "../Shared/CacheContextProvider";


export const SongTreeNode = (props) => {
	const { children, songNodeInfo, prefix, nodeId } = props;
	const { setCacheValue } = useCache();

	useEffect(() => {
		setCacheValue(nodeId, songNodeInfo);
	},[setCacheValue, songNodeInfo, nodeId]);

	const label = songNodeInfo.name ?
		songNodeInfo.name : songNodeInfo.path.replace(prefix, "");
	return (
		<TreeItem nodeId={nodeId} label={label}>
			{children}
		</TreeItem>
	);
};

SongTreeNode.propTypes = {
	nodeId: PropTypes.string,
	prefix: PropTypes.string,
	children: PropTypes.oneOfType([
		PropTypes.arrayOf(PropTypes.node),
		PropTypes.node,
	]).isRequired,
	songNodeInfo: PropTypes.shape({
		path: PropTypes.string,
		id: PropTypes.number,
		name: PropTypes.string,
	}),
	mapValueToNodeId: PropTypes.func,
};

export const SongDirectory = (props) => {
	const { prefix, level, dirIdx } = props;
	const [state, dispatch] = useReducer(waitingReducer(), listDataInitialState);
	const { callStatus } = state;
	const { getCacheValue, setCacheValue } = useCache();

	useEffect(() => {
		const fetch = async () => {
			try {
				if(!callStatus) {
					dispatch(dispatches.started());
					const cachedResults = getCacheValue(prefix);
					if(cachedResults) {
						dispatch(dispatches.done(cachedResults));
					}
					else {
						const data = await fetchSongDir({ params: { prefix } });
						setCacheValue(prefix, data);
						dispatch(dispatches.done(data));
					}
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

				return (
					<SongTreeNode
						nodeId={key}
						key={key}
						prefix={prefix}
						songNodeInfo={d}
					>
						{!d.id &&
							<SongDirectory
								prefix={d.path}
								level={level + 1}
								dirIdx={idx}
							/>}
					</SongTreeNode>
				);
			})}
		</Loader>
	);
};

SongDirectory.propTypes = {
	nodeId: PropTypes.string,
	prefix: PropTypes.string,
	level: PropTypes.number,
	dirIdx: PropTypes.number,
	mapValueToNodeId: PropTypes.func,
};

export const SongTree = withCacheProvider()(() => {
	const [selectedNodes, setSelectedNodes] = useState([]);
	const { getCacheValue } = useCache();

	const onNodeSelect = (e, nodeIds) => {
		if(nodeIds.lenth === 1) {
			if(selectedNodes[0] === nodeIds[0]) { //unselect
				setSelectedNodes([]);
			}
			setSelectedNodes([...nodeIds]);
		}
		else {
			setSelectedNodes([...nodeIds]);
		}
	};

	const getSelectedSongInfo = () => {
		if(selectedNodes.length !== 1) {
			return null;
		}
		const songInfo = getCacheValue(selectedNodes[0]);
		return songInfo;
	};

	const isSongSelected = () => {
		const songInfo = getSelectedSongInfo();
		return !!songInfo?.id && songInfo.id > 0;
	};

	const openSongEdit = () => {
		const songInfo = getSelectedSongInfo();
		if(!songInfo) {
			console.warn("No song selected.");
		}
		console.log(songInfo);
	};

	return (
		<>
			{selectedNodes &&
			<AppBar
				sx={{
					top: (theme) => theme.spacing(6),
					backgroundColor: (theme) => theme.palette.background.default,
					width: `calc(100% - ${drawerWidth}px)`,
					ml: `${drawerWidth}px`,
					height: (theme) => theme.spacing(4),
				}}
			>
				<Toolbar variant="dense" sx={{ pb: 1, alignItems: "baseline"}}>
					{isSongSelected() &&
					<Button
						onClick={openSongEdit}
					>
						Edit Song Info
					</Button>}
				</Toolbar>
			</AppBar>}
			<Box sx={{ height: (theme) => theme.spacing(3), width: "100%"}} />
			<TreeView
				selected={selectedNodes}
				onNodeSelect={onNodeSelect}
				multiSelect
			>
				<SongDirectory
					prefix=""
					level={0}
					dirIdx={0}
				/>
			</TreeView>
		</>
	);
});