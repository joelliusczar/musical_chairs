import React, {useReducer, useEffect, useState } from "react";
import { Box, Button, AppBar, Toolbar } from "@mui/material";
import { TreeView, TreeItem } from "@mui/lab";
import {
	waitingReducer,
	dispatches,
} from "../Shared/waitingReducer";
import { fetchSongTree } from "../../API_Calls/songInfoCalls";
import Loader from "../Shared/Loader";
import PropTypes from "prop-types";
import { drawerWidth } from "../../style_config";
import { withCacheProvider, useCache } from "../Shared/CacheContextProvider";
import { Link } from "react-router-dom";
import { DomRoutes, UserRoleDef, UserRoleDomain } from "../../constants";
import { formatError } from "../../Helpers/error_formatter";
import {
	buildArrayQueryStr,
	getDownloadAddress,
} from "../../Helpers/url_helpers";
import { useSnackbar } from "notistack";
import { useAuthViewStateChange } from "../../Context_Providers/AuthContext";
import { normalizeOpeningSlash } from "../../Helpers/string_helpers";
import { RequiredDataState, ListDataShape } from "../../Types/reducer_types";
import { SongTreeNodeInfo } from "../../Types/song_info_types";
import { IdType } from "../../Types/generic_types"
import { ListData } from "../../Types/pageable_types";
import { PathsActionRule } from "../../Types/user_types";

type SongTreeNodeProps = {
	children: React.ReactNode
	prefix: string
	songNodeInfo: SongTreeNodeInfo
	nodeId: string
};

export const SongTreeNode = (props: SongTreeNodeProps) => {
	const { children, songNodeInfo, prefix, nodeId } = props;
	const { setCacheValue } = useCache<SongTreeNodeInfo | ListData<SongTreeNodeInfo>>();

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

type SongDirectoryProps = {
	prefix: string
	level: number
	dirIdx: number
};

export const SongDirectory = (props: SongDirectoryProps) => {
	const { prefix, level, dirIdx } = props;
	const [state, dispatch] = useReducer(
		waitingReducer<
			SongTreeNodeInfo,
			RequiredDataState<ListDataShape<SongTreeNodeInfo>>
		>(),
		new RequiredDataState<ListDataShape<SongTreeNodeInfo>>({ items: []})
	);
	const { callStatus } = state;
	const { getCacheValue, setCacheValue } = useCache<
		SongTreeNodeInfo | ListData<SongTreeNodeInfo>
	>();

	useAuthViewStateChange(dispatch);
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
						const data = await fetchSongTree({ prefix });
						setCacheValue(prefix, data);
						dispatch(dispatches.done(data));
					}
				}
			}
			catch(err) {
				dispatch(dispatches.failed(formatError(err)));
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

export const SongTree = withCacheProvider<
	SongTreeNodeInfo | ListData<SongTreeNodeInfo>
>()(
	() => {
	const [selectedNodes, setSelectedNodes] = useState<string[]>([]);
	const [selectedPrefix, setSelectedPrefix] = useState<string | null>(null);
	const [selectedPrefixRules, setSelectedPrefixRules] =
		useState<PathsActionRule[]>([]);
	const { getCacheValue } = useCache<
		SongTreeNodeInfo | ListData<SongTreeNodeInfo>
	>();
	const { enqueueSnackbar } = useSnackbar();

	const onNodeSelect = (e: React.SyntheticEvent, nodeIds: string[]) => {
		if(nodeIds.length === 1) {
			if(selectedNodes[0] === nodeIds[0]) { //unselect
				setSelectedNodes([]);
			}
			const songNodeInfo = getCacheValue(nodeIds[0]);
			if(songNodeInfo && "rules" in songNodeInfo && "path" in songNodeInfo) {
				setSelectedPrefixRules(songNodeInfo?.rules || []);
				setSelectedPrefix(normalizeOpeningSlash(songNodeInfo?.path));
			}
			setSelectedNodes([nodeIds[0]]);
		}
		else {
			if(nodeIds.length < 100) {
				setSelectedPrefix(null);
				setSelectedNodes([...nodeIds]);
			}
			else {
				enqueueSnackbar("Maximum songs (100) have been selected.",
					{ variant: "warning"});
			}
		}
	};

	const getSelectedSongIds = () => {
		return selectedNodes.map(s => {
			const value = getCacheValue(s);
			if (value && "id" in value) {
				return value?.id;
			}
			return null;
		}).filter(n => !!n) as number[];
	};

	const getSongEditUrl = (ids: IdType[]) => {
		const queryStr = buildArrayQueryStr("ids", ids);
		return `${DomRoutes.songEdit()}${queryStr}`;
	};

	const getUserAssignUrl = () => {
		return `${DomRoutes.pathUsers()}?prefix=${selectedPrefix}`;
	};

	const selectedSongIds = getSelectedSongIds();

	const canAssignUsers = () => {
		if (selectedPrefix !== null) {
			const hasRule = selectedPrefixRules
				.filter(r => r.name === UserRoleDef.PATH_USER_LIST)
				.some(r =>
					(r.path &&
						selectedPrefix.startsWith(normalizeOpeningSlash(r.path))) ||
					r.domain === UserRoleDomain.SITE
				);
			return hasRule;
		}
		return false;
	};

	return (
		<>
			{(!!selectedSongIds.length || selectedPrefixRules) &&
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
					{!!selectedSongIds.length && <Button
						component={Link}
						to={getSongEditUrl(selectedSongIds)}
					>
						Edit Song Info
					</Button>}
					{selectedSongIds.length === 1 &&<Button
						href={getDownloadAddress(selectedSongIds[0])}
					>
						Download song
					</Button>}
					{canAssignUsers() && <Button
						component={Link}
						to={getUserAssignUrl()}
					>
						Assign users
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