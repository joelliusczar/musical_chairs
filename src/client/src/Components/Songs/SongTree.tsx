import React, { useEffect, useState } from "react";
import { Box, Button, AppBar, Toolbar } from "@mui/material";
import { TreeView, TreeItem } from "@mui/lab";
import {
	dispatches,
} from "../../Reducers/waitingReducer";
import { 
	fetchSongsLs,
	fetchSongLsParents,
	songDownloadUrl,
} from "../../API_Calls/songInfoCalls";
import Loader from "../Shared/Loader";
import { drawerWidth } from "../../style_config";
import { withCacheProvider, useCache } from "../Shared/CacheContextProvider";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { DomRoutes, UserRoleDef, UserRoleDomain } from "../../constants";
import { formatError } from "../../Helpers/error_formatter";
import {
	buildArrayQueryStr,
} from "../../Helpers/url_helpers";
import { useSnackbar } from "notistack";
import { useAuthViewStateChange } from "../../Context_Providers/AuthContext";
import { normalizeOpeningSlash } from "../../Helpers/string_helpers";
import { SongTreeNodeInfo } from "../../Types/song_info_types";
import { IdType, Dictionary } from "../../Types/generic_types";
import { ListData } from "../../Types/pageable_types";
import { PathsActionRule } from "../../Types/user_types";
import { useVoidWaitingReducer } from "../../Reducers/voidWaitingReducer";
import { DirectoryNewModalOpener } from "./DirectoryEdit";
import { SongUploadNewModalOpener } from "./SongUpload";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";


type SongTreeNodeProps = {
	children: React.ReactNode
	prefix: string
	songNodeInfo: SongTreeNodeInfo
	nodeId: string
};

export const SongTreeNode = (props: SongTreeNodeProps) => {
	const { children, songNodeInfo, prefix, nodeId } = props;
	const { setCacheValue } = useCache<
		SongTreeNodeInfo | ListData<SongTreeNodeInfo>
	>();

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


type SongDirectoryProps = {
	prefix: string
	level: number
	dirIdx: number,
	setExpandedNodes: (p: string[]) => void,
};

export const SongDirectory = (props: SongDirectoryProps) => {
	const { prefix, level, dirIdx, setExpandedNodes } = props;
	const [state, dispatch] = useVoidWaitingReducer();
	const { callStatus } = state;
	const { getCacheValue, setCacheValue } = useCache<
		ListData<SongTreeNodeInfo>
	>();
	const location = useLocation();
	const [currentQueryStr, setCurrentQueryStr] = useState("");



	useAuthViewStateChange(dispatch);
	useEffect(() => {
		const songTreeParentInfoToNodeIds = (
			treeInfo: Dictionary<ListData<SongTreeNodeInfo>>
		) => {
			const keys = Object.keys(treeInfo).sort((a, b) => a.length - b.length);
			const result = [];
			let precomputedDirIdx = 0;
			for (let i = 1; i < keys.length; i++) {
				const foundIdx = treeInfo[keys[i - 1]]
					.items
					.findIndex(p => p.path === keys[i]);
				result.push(`${i - 1}_${precomputedDirIdx}_${foundIdx}`);
				precomputedDirIdx = foundIdx;
			}
			return result;
		};

		const fetch = async () => {
			if (currentQueryStr === `${location.pathname}${location.search}`) return;
			const queryObj = new URLSearchParams(location.search);
			const urlPrefix = queryObj.get("prefix");
			try {
				if(!callStatus) {
					dispatch(dispatches.started());
					if (!!urlPrefix && ! prefix) {
						const data = await fetchSongLsParents({ prefix: urlPrefix });
						Object.keys(data).forEach(key => {
							setCacheValue(normalizeOpeningSlash(key), data[key]);
						});
						dispatch(dispatches.done());
						setCurrentQueryStr(`${location.pathname}${location.search}`);
						const nodeIds = songTreeParentInfoToNodeIds(data);
						setExpandedNodes(nodeIds);
					}
					else {
						const cachedResults = getCacheValue(normalizeOpeningSlash(prefix));
						if(cachedResults) {
							dispatch(dispatches.done());
						}
						else {
							const data = await fetchSongsLs({ prefix });
							setCacheValue(normalizeOpeningSlash(prefix), data);
							dispatch(dispatches.done());
						}
					}
				}
			}
			catch(err) {
				dispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
	}, [
		callStatus,
		dispatch,
		prefix,
		location.search,
		location.pathname,
		setCacheValue,
		getCacheValue,
		setExpandedNodes,
		currentQueryStr,
	]);

	const currentLevelData = getCacheValue(normalizeOpeningSlash(prefix)) 
		|| { items: []};

	return (
		<Loader status={callStatus} error={state.error}>
			{currentLevelData.items.map((d, idx) => {
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
								setExpandedNodes={setExpandedNodes}
							/>}
					</SongTreeNode>
				);
			})}
		</Loader>
	);
};

export const SongTree = withCacheProvider<
	object,
	SongTreeNodeInfo | ListData<SongTreeNodeInfo>
>()(
	() => {
		const [expandedNodes, setExpandedNodes] = useState<string[]>([]); 
		const [selectedNodes, setSelectedNodes] = useState<string[]>([]);
		const [selectedPrefix, setSelectedPrefix] = useState<string | null>(null);
		const [selectedPrefixRules, setSelectedPrefixRules] =
			useState<PathsActionRule[]>([]);
		const { getCacheValue, setCacheValue } = useCache<
			SongTreeNodeInfo | ListData<SongTreeNodeInfo>
		>();
		const { enqueueSnackbar } = useSnackbar();
		const navigate = useNavigate();
		const location = useLocation();

		const isNodeDirectory = (node: SongTreeNodeInfo) => {
			return node.path?.endsWith("/");
		};

		const getDirectoryPart = (path: string) => {
			const directoryPart = path.replace(/[^/]+$/, "");
			return directoryPart;
		};

		const updateUrl = (path: string) => {
			const directoryPart = getDirectoryPart(path);
			navigate(
				`${location.pathname}?prefix=${encodeURIComponent(directoryPart)}`,
				{ replace: true }
			);
		};

		const onNodeSelect = (e: React.SyntheticEvent, nodeIds: string[]) => {
			if(nodeIds.length === 1) {
				if(selectedNodes[0] === nodeIds[0]) { //unselect
					setSelectedNodes([]);
				}
				const songNodeInfo = getCacheValue(nodeIds[0]);
				if (!!songNodeInfo && "path" in songNodeInfo) {
					if (isNodeDirectory(songNodeInfo)) {
						updateUrl(normalizeOpeningSlash(songNodeInfo?.path));
						const expandedCopy = [...expandedNodes];
						const expandedFoundIdx = 
							expandedNodes.findIndex(n => n === nodeIds[0]);
						if (expandedFoundIdx === -1) {
							expandedCopy.push(nodeIds[0]);
						}
						else {
							expandedCopy.splice(expandedFoundIdx, 1);
						}
						setExpandedNodes(expandedCopy);

					}
				}
				if (!!songNodeInfo &&
					 "rules" in songNodeInfo && "path" in songNodeInfo
				) {
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

		const isDirectorySelected = () => {
			if (selectedNodes.length !== 1) return false;
			const songNodeInfo = getCacheValue(selectedNodes[0]);
			if (!songNodeInfo) return false;
			if (!("path" in songNodeInfo)) return false;
			return isNodeDirectory(songNodeInfo);
		};

		const getSongEditUrl = (ids: IdType[]) => {
			const queryStr = buildArrayQueryStr("ids", ids);
			return `${DomRoutes.songEdit()}${queryStr}`;
		};

		const getUserAssignUrl = () => {
			return `${DomRoutes.pathUsers()}?prefix=${selectedPrefix}`;
		};

		const downloadSong = async () => {
			const url = await songDownloadUrl({id : selectedSongIds[0]});
			window?.open(url, "_blank")?.focus();
		};

		const selectedSongIds = getSelectedSongIds();

		const canAssignUsers = () => {
			if (isDirectorySelected()) return false;
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

		const canDownloadSelection = () => {
			if (isDirectorySelected()) return false;
			if (selectedNodes.length !== 1) return false;
			const songNodeInfo = getCacheValue(selectedNodes[0]);
			if (songNodeInfo && "rules" in songNodeInfo) {
				const canDownloadThisSong = anyConformsToAnyRule(
					songNodeInfo?.rules,
					[UserRoleDef.PATH_DOWNLOAD]
				);
				return canDownloadThisSong;
			};
			return false;
		};

		const canEditSongInfo = () => {
			if (isDirectorySelected()) return false;
			return !!selectedSongIds.length;
		};

		const onAddNewSong = (node: SongTreeNodeInfo) => {
			if (node && node.id) {
				navigate(getSongEditUrl([node.id]));
			}
		};

		const onAddNewNode = (nodes: Dictionary<ListData<SongTreeNodeInfo>>) => {
			Object.keys(nodes).forEach(key => {
				setCacheValue(normalizeOpeningSlash(key), nodes[key]);
			});
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
						{canEditSongInfo() && <Button
							component={Link}
							to={getSongEditUrl(selectedSongIds)}
						>
							Edit Song Info
						</Button>}
						{canDownloadSelection() &&<Button
							onClick={downloadSong}
						>
							Download song
						</Button>}
						{canAssignUsers() && <Button
							component={Link}
							to={getUserAssignUrl()}
						>
							Assign users
						</Button>}
						{isDirectorySelected() && selectedPrefix &&
							<DirectoryNewModalOpener 
								add={onAddNewNode}
								prefix={selectedPrefix} 
							/>}
						{isDirectorySelected() && selectedPrefix &&
							<SongUploadNewModalOpener 
								add={onAddNewSong}
								prefix={selectedPrefix} 
							/>}
					</Toolbar>
				</AppBar>}
				<Box sx={{ height: (theme) => theme.spacing(3), width: "100%"}} />
				<TreeView
					selected={selectedNodes}
					expanded={expandedNodes}
					onNodeSelect={onNodeSelect}
					multiSelect
				>
					<SongDirectory
						prefix=""
						level={0}
						dirIdx={0}
						setExpandedNodes={setExpandedNodes}
					/>
				</TreeView>
			</>
		);
	});