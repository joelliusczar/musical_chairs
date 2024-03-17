import React, { useEffect, useState } from "react";
import { Box, Button, AppBar, Toolbar } from "@mui/material";
import { TreeView, TreeItem } from "@mui/lab";
import { 
	fetchSongsLs,
	fetchSongLsParents,
	songDownloadUrl,
} from "../../API_Calls/songInfoCalls";
import Loader from "../Shared/Loader";
import { drawerWidth } from "../../style_config";
import { 
	useCache,
} from "../../Context_Providers/TreeCacheContext/TreeCacheContext";
import {
	withCacheProvider,
} from "../../Context_Providers/TreeCacheContext/TreeCacheContextHOC";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { DomRoutes, UserRoleDef, UserRoleDomain } from "../../constants";
import { formatError } from "../../Helpers/error_formatter";
import {
	buildArrayQueryStr,
} from "../../Helpers/request_helpers";
import { useSnackbar } from "notistack";
import {
	useCurrentUser,
} from "../../Context_Providers/AuthContext/AuthContext";
import { normalizeOpeningSlash } from "../../Helpers/string_helpers";
import {
	SongTreeNodeInfo,
	DirectoryInfoNodeInfo,
} from "../../Types/song_info_types";
import { IdValue, Dictionary, KeyValue } from "../../Types/generic_types";
import { ListData } from "../../Types/pageable_types";
import { PathsActionRule } from "../../Types/user_types";
import {
	keyedDataDispatches as dispatches,
} from "../../Reducers/keyedDataWaitingReducer";
import { DirectoryNewModalOpener } from "./DirectoryEdit";
import { SongUploadNewModalOpener } from "./SongUpload";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import { isCallPending } from "../../Helpers/request_helpers";
import { cookieToObjectURIDecoded } from "../../Helpers/browser_helpers";
import { notNullPredicate } from "../../Helpers/array_helpers";

const treeId = "song-tree";

const buildNodeId = (level: number, dirIdx: number, idx: number) => {
	return`${level}-${dirIdx}-${idx}`;
};

const isNodeDirectory = (node: SongTreeNodeInfo) => {
	return node.path?.endsWith("/");
};

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
		result.push({
			path: keys[i - 1],
			nodeId: buildNodeId(i - 1, precomputedDirIdx, foundIdx),
		});
		precomputedDirIdx = foundIdx;
	}
	return result;
};


type SongTreeNodeProps = {
	children: React.ReactNode
	prefix: string
	songNodeInfo: SongTreeNodeInfo
	nodeId: string
};

const SongTreeNode = (props: SongTreeNodeProps) => {
	const { children, songNodeInfo, prefix, nodeId } = props;
	const { dispatch } = useCache<
		SongTreeNodeInfo | ListData<SongTreeNodeInfo>
	>();

	useEffect(() => {
		dispatch(dispatches.done({
			[nodeId] : songNodeInfo,
		}));
	},[dispatch, songNodeInfo, nodeId]);

	useEffect(() => {
		if (!isNodeDirectory(songNodeInfo)) return;
		const selector = `#${treeId}-${nodeId} .Mui-expanded`;
		const el = document.querySelectorAll(selector)[0];
		if (el) {
			el.scrollIntoView({ block: "center", behavior: "smooth"});
		}
	},[nodeId, songNodeInfo]);

	const label = songNodeInfo.name ?
		songNodeInfo.name : songNodeInfo.path.replace(prefix, "");

	return (
		<TreeItem 
			nodeId={nodeId} 
			label={label}
		>
			{children}
		</TreeItem>
	);
};


type SongDirectoryProps = {
	prefix: string
	level: number
	dirIdx: number,
	setExpandedNodes: (p: DirectoryInfoNodeInfo[]) => void,
};

const SongDirectory = (props: SongDirectoryProps) => {
	const { prefix, level, dirIdx, setExpandedNodes } = props;
	const { state, dispatch } = useCache<
		ListData<SongTreeNodeInfo>
	>();
	
	const storedAtPrefix = normalizeOpeningSlash(prefix) in state ? 
		state[normalizeOpeningSlash(prefix)] : null;
	const prefixData = storedAtPrefix?.data;

	const callStatus = !!storedAtPrefix ? storedAtPrefix.callStatus : null;
	const error = !!storedAtPrefix ? storedAtPrefix.error : null;

	const isPending = isCallPending(callStatus);
	const { enqueueSnackbar } = useSnackbar();
	const queryStr = location.search;
	const urlSegement = `${location.pathname}${queryStr}`;

	const currentUser = useCurrentUser();
	const cookieObj = cookieToObjectURIDecoded(document.cookie);
	const username = currentUser.username || cookieObj["username"] || "";
	const loggedIn = !!(currentUser.access_token || cookieObj["access_token"]);
	const fullyLogedOut = !username;

	useEffect(() => {
		if (!prefix) { //only execute at top node
			if (fullyLogedOut) {
				dispatch(dispatches.restart());
			}
		}
	},[prefix, fullyLogedOut, dispatch]);

	useEffect(() => {
		const newLogin = !!username && loggedIn;
		if (!prefix) { //only execute at top node
			if (newLogin) {
				dispatch(dispatches.restart());
			}
		}
		//only execute if error is at this node
		else if (newLogin) {
			dispatch(dispatches.restart([
				normalizeOpeningSlash(prefix),
			]));
		}
	}, [loggedIn, dispatch, prefix, username]);


	useEffect(() => {
		const queryObj = new URLSearchParams(queryStr);
		const urlPrefix = queryObj.get("prefix");
		if (!!urlPrefix && !prefix) {
			const requestObj = fetchSongLsParents({ prefix: urlPrefix });
			if (!isPending) return;
			const fetch = async () => {
				try {
					dispatch(dispatches.started([
						normalizeOpeningSlash(urlPrefix),
						normalizeOpeningSlash(""),
					]));
					const data = await requestObj.call();
					const cacheAdditions: {
						[key: KeyValue]: ListData<SongTreeNodeInfo>
					} = {};
					//only setting this to flip the callstatus
					//don't think we're actually using it
					cacheAdditions[normalizeOpeningSlash(urlPrefix)] = { items: []};
					Object.keys(data).forEach(key => {
						cacheAdditions[normalizeOpeningSlash(key)] = data[key];
					});
					dispatch(dispatches.done(cacheAdditions));
					const nodeIds = songTreeParentInfoToNodeIds(data);
					setExpandedNodes(nodeIds);
				}
				catch(err) {
					const errMsg = formatError(err);
					enqueueSnackbar(errMsg,{ variant: "error"});
					dispatch(
						dispatches.failed({
							[urlSegement]: errMsg,
							[normalizeOpeningSlash("")]: errMsg,
						})
					);
				}
			};

			fetch();

			return () => requestObj.abortController.abort();
		}
	},[
		queryStr,
		prefix,
		dispatch,
		urlSegement,
		enqueueSnackbar,
		setExpandedNodes,
		isPending,
	]);

	useEffect(() => {
		const queryObj = new URLSearchParams(queryStr);
		const urlPrefix = queryObj.get("prefix");

		if (!urlPrefix || !!prefix) {
			const requestObj = fetchSongsLs({ prefix });
			const normalizedPrefix = normalizeOpeningSlash(prefix);
			if (!isPending) return;
			const fetch = async () => {
				try {
					dispatch(dispatches.started([normalizedPrefix]));
					const data = await requestObj.call();
					dispatch(dispatches.done({
						[normalizedPrefix]: data,
					}));
				}
				catch(err) {
					enqueueSnackbar(formatError(err),{ variant: "error"});
					dispatch(
						dispatches.failed({
							[normalizedPrefix]: formatError(err),
						})
					);
				}
			};
			fetch();

			return () => requestObj.abortController.abort();
		}
	}, [
		prefix,
		queryStr,
		enqueueSnackbar,
		dispatch,
		isPending,
	]);


	const currentLevelData = !!prefixData ? prefixData : { items: []};


	return (
		<Loader status={callStatus} error={error}>
			{currentLevelData.items.map((d, idx) => {
				const key = buildNodeId(level, dirIdx, idx);

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
		const [expandedNodes, setExpandedNodes] = useState<
			DirectoryInfoNodeInfo[]
		>([]); 
		const [selectedNodes, setSelectedNodes] = useState<string[]>([]);
		const [selectedPrefix, setSelectedPrefix] = useState<string | null>(null);
		const [selectedPrefixRules, setSelectedPrefixRules] =
			useState<PathsActionRule[]>([]);
		const { dispatch, treeData } = useCache<
			SongTreeNodeInfo | ListData<SongTreeNodeInfo>
		>();
		const { enqueueSnackbar } = useSnackbar();
		const navigate = useNavigate();
		const location = useLocation();

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
				const songNodeInfo = treeData[nodeIds[0]];
				if(selectedNodes[0] === nodeIds[0]) { //unselect
					setSelectedNodes([]);
				}
				if (!!songNodeInfo && "path" in songNodeInfo) {
					if (isNodeDirectory(songNodeInfo)) {
						updateUrl(normalizeOpeningSlash(songNodeInfo?.path));
						const expandedCopy = [...expandedNodes];
						const expandedFoundIdx = 
							expandedNodes.findIndex(n => n.nodeId === nodeIds[0]);
						if (expandedFoundIdx === -1) {
							expandedCopy.push({
								path: songNodeInfo.path,
								nodeId: nodeIds[0],
							});
						}
						else {
							const isFoundSelected = selectedNodes
								.some(n => n === expandedNodes[expandedFoundIdx].nodeId);
							if (isFoundSelected) {
								expandedCopy.splice(expandedFoundIdx, 1);
							}
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
					enqueueSnackbar(
						"Maximum songs (100) have been selected.",
						{ variant: "warning"}
					);
				}
			}
		};

		const getSelectedSongIds = () => {
			return selectedNodes.map(s => {
				const value = treeData[s];
				if (value && "id" in value) {
					return value?.id;
				}
				return null;
			}).filter(n => !!n) as number[];
		};

		const isDirectorySelected = () => {
			if (selectedNodes.length !== 1) return false;
			const songNodeInfo = treeData[selectedNodes[0]];
			if (!songNodeInfo) return false;
			if (!("path" in songNodeInfo)) return false;
			return isNodeDirectory(songNodeInfo);
		};

		const getSongEditUrl = (ids: IdValue[]) => {
			const queryStr = buildArrayQueryStr("ids", ids);
			return `${DomRoutes.songEdit()}${queryStr}`;
		};

		const getUserAssignUrl = () => {
			return `${DomRoutes.pathUsers()}?prefix=${selectedPrefix}`;
		};

		const downloadSong = async () => {
			const requestObj = songDownloadUrl({id : selectedSongIds[0]});
			const url = await requestObj.call();
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
			const songNodeInfo = treeData[selectedNodes[0]];
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

		const onAddNewSong = (nodes: SongTreeNodeInfo[]) => {
			const nodeIds = nodes.map(n => n.id).filter(notNullPredicate);
			navigate(getSongEditUrl(nodeIds));
		};

		const onAddNewNode = (nodes: Dictionary<ListData<SongTreeNodeInfo>>) => {
			Object.keys(nodes).forEach(key => {
				dispatch(dispatches.done({
					[normalizeOpeningSlash(key)]: nodes[key],
				}));
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
					expanded={expandedNodes.map(n => n.nodeId)}
					onNodeSelect={onNodeSelect}
					multiSelect
					id={treeId}
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