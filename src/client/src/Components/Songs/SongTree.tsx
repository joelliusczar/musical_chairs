import React, { useEffect, useState, useCallback } from "react";
import { Button } from "@mui/material";
import { css } from "@emotion/react";
import { SimpleTreeView, TreeItem } from "@mui/x-tree-view";
import {
	fetchSongsLs,
	fetchSongLsParents,
	deletePrefix,
	movePath,
} from "../../API_Calls/songInfoCalls";
import Loader from "../Shared/Loader";
import { YesNoModalOpener } from "../Shared/YesNoControl";
import {
	useTree,
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
import {
	normalizeOpeningSlash,
	unicodeToUrlSafeBase64,
	urlSafeBase64ToUnicode,
} from "../../Helpers/string_helpers";
import {
	SongTreeNodeInfo,
	DirectoryTransferSource,
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
import { useDrag, useDrop, DndProvider } from "react-dnd";
import {
	HTML5Backend,
} from "react-dnd-html5-backend";
import { SongListener } from "./SongListener";

const treeId = "song-tree";

const styles = {
	toolbar: css`
		display: flex;
		align-items: center;
		position: sticky;
		top: 0;
		background-color: #FFF;
		z-index: 2;
	`,
};


const isNodeDirectory = (node: SongTreeNodeInfo) => {
	return node.path?.endsWith("/");
};

const songTreeParentInfoToNodeIds = (
	treeInfo: Dictionary<ListData<SongTreeNodeInfo>>
) => {
	const keys = Object.keys(treeInfo);
	const result = [];
	for (let i = 0; i < keys.length; i++) {
		const currentKey = keys[i];
		if (!currentKey) continue;
		result.push(unicodeToUrlSafeBase64(normalizeOpeningSlash(currentKey)));
	}
	return result;
};

const firstNode = (nodes: ListData<SongTreeNodeInfo>) => {
	if (nodes.items.length) {
		return nodes.items[0];
	}
	return null;
};


type SongTreeNodeProps = {
	children: React.ReactNode
	prefix: string
	songNodeInfo: SongTreeNodeInfo
	nodeId: string,
	onNodeLoaded: (node: SongTreeNodeInfo, nodeId: string) => void,
};

const SongTreeNode = (props: SongTreeNodeProps) => {
	const { children, songNodeInfo, prefix, nodeId, onNodeLoaded } = props;
	const { dispatch , updateTree, setExpandedNodes } = useTree<
		ListData<SongTreeNodeInfo>
	>();
	const { enqueueSnackbar } = useSnackbar();

	const [, dragRef] = useDrag<DirectoryTransferSource>({
		type: "branch",
		item: { prefix, path: songNodeInfo.path },
	});

	const dropPath = songNodeInfo.path;

	const [{ isOver },dropRef] = useDrop<
	DirectoryTransferSource,
		unknown,
		{ isOver: boolean }
	>(() => ({
		accept: "branch",
		drop: async (item, monitor) => {
			if(!monitor.didDrop()) {
				try {
					const requestObj = movePath({
						...item,
						newprefix: dropPath,
					});
					const result = await requestObj.call();
					updateTree(result);

					const expanded = dropPath
						.split("/")
						// .filter(s => !!s)
						.reduce((a, c) => {
							if (a.length) {
								const last = a[a.length - 1];
								a.push(`${last}${c}/`);
								return a;
							}
							else {
								a.push(`${c}/`);
								return a;
							}
						},[] as string[]);
					expanded.pop();
					setExpandedNodes(expanded.map(p => unicodeToUrlSafeBase64(
						normalizeOpeningSlash(p)
					)));
				}
				catch (err) {
					enqueueSnackbar(formatError(err),{ variant: "error"});
				}
			}
		},
		canDrop: (item) => {
			if (!dropPath.endsWith("/")) return false;
			if (dropPath === item.path) return false;
			return true;
		},
		collect: (monitor) => ({
			isOver: !!monitor.isOver({ shallow: true }) && !!monitor.canDrop(),
		}),
	}));

	useEffect(() => {
		dispatch(dispatches.done({
			[nodeId] : { items: [songNodeInfo], totalRows: 1 },
		}));
	},[dispatch, songNodeInfo, nodeId]);

	useEffect(() => {
		onNodeLoaded(songNodeInfo, nodeId);
	},[onNodeLoaded, songNodeInfo, nodeId]);


	const label = songNodeInfo.name ?
		songNodeInfo.name : songNodeInfo.path.replace(prefix, "");

	return (
		<div
			style={ isOver ? { border: "1px solid"} : {}}
			ref={dropRef}
		>
			<TreeItem
				className="song-tree-item"
				itemId={nodeId}
				label={label}
				ref={dragRef}
			>
				{children}
			</TreeItem>
		</div>
	);
};


type SongDirectoryProps = {
	prefix: string
	level: number,
	onNodeLoaded: (node: SongTreeNodeInfo, nodeId: string) => void,
};

const SongDirectory = (props: SongDirectoryProps) => {
	const { prefix, level, onNodeLoaded } = props;
	const { state, dispatch, setExpandedNodes } = useTree<
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
	const queryObj = new URLSearchParams(queryStr);
	const urlNodeId = queryObj.get("nodeid");
	const urlSegement = `${location.pathname}${queryStr}`;
	const navigate = useNavigate();

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
		if (!!urlNodeId && !prefix) {
			const urlPrefix = urlSafeBase64ToUnicode(urlNodeId);
			const requestObj = fetchSongLsParents({ nodeId: urlNodeId });
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
					if (Object.keys(data).length < 1) {
						navigate("", { replace: true, relative: "path" });
					}
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
		urlNodeId,
		prefix,
		dispatch,
		urlSegement,
		enqueueSnackbar,
		setExpandedNodes,
		isPending,
		navigate,
	]);

	useEffect(() => {
		if (!urlNodeId || !!prefix) {
			const nodeId = unicodeToUrlSafeBase64(prefix);
			const requestObj = fetchSongsLs({ nodeId });
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
		urlNodeId,
		enqueueSnackbar,
		dispatch,
		isPending,
	]);


	const currentLevelData = !!prefixData ? prefixData : { items: []};

	return (
		<Loader status={callStatus} error={error}>
			{currentLevelData.items.map((d) => {
				const nodeId = unicodeToUrlSafeBase64(normalizeOpeningSlash(d.path));

				return (
					<SongTreeNode
						nodeId={nodeId}
						key={nodeId}
						prefix={prefix}
						songNodeInfo={d}
						onNodeLoaded={onNodeLoaded}
					>
						{!d.id &&
							<SongDirectory
								prefix={d.path}
								level={level + 1}
								onNodeLoaded={onNodeLoaded}
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
		const [selectedNodes, setSelectedNodes] = useState<string[]>([]);
		const [selectedPrefixRules, setSelectedPrefixRules] =
			useState<PathsActionRule[]>([]);

		const { treeData, updateTree, expandedNodes, setExpandedNodes } = useTree<
			ListData<SongTreeNodeInfo>
		>();
		const { enqueueSnackbar } = useSnackbar();
		const navigate = useNavigate();
		const location = useLocation();
		const queryStr = location.search;
		const queryObj = new URLSearchParams(queryStr);
		const urlNodeId = queryObj.get("nodeid");
		const selectedPrefix = selectedNodes.length == 1 ?
			urlSafeBase64ToUnicode(selectedNodes[0]) :
			null;

		const updateUrl = (path: string) => {
			const nodeId = unicodeToUrlSafeBase64(path);
			navigate(
				`${location.pathname}?nodeid=${nodeId}`,
				{ replace: true }
			);
		};

		const onNodeSelect = (e: React.SyntheticEvent, nodeIds: string[]) => {
			if(nodeIds.length === 1) {
				const songNodeInfo = firstNode(treeData[nodeIds[0]]);
				if(selectedNodes[0] === nodeIds[0]) { //unselect
					setSelectedNodes([]);
				}
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
							const isFoundSelected = selectedNodes
								.some(n => n === expandedNodes[expandedFoundIdx]);
							if (isFoundSelected) {
								expandedCopy.splice(expandedFoundIdx, 1);
							}
						}
						setExpandedNodes(expandedCopy);

					}
				}
				if (!!songNodeInfo && "rules" in songNodeInfo) {
					setSelectedPrefixRules(songNodeInfo?.rules || []);
				}
				setSelectedNodes([nodeIds[0]]);
			}
			else {
				if(nodeIds.length < 100) {
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
				const value = firstNode(treeData[s]);
				if (value && "id" in value) {
					return value?.id;
				}
				return null;
			}).filter(n => !!n) as number[];
		};

		const isDirectorySelected = () => {
			if (selectedNodes.length !== 1) return false;
			const songNodeInfo = firstNode(treeData[selectedNodes[0]]);
			if (!songNodeInfo) return false;
			if (!("path" in songNodeInfo)) return false;
			return isNodeDirectory(songNodeInfo);
		};

		const getSongEditUrl = (ids: IdValue[]) => {
			const queryStr = buildArrayQueryStr("ids", ids);
			return `${DomRoutes.songEdit()}${queryStr}`;
		};

		const getUserAssignUrl = () => {
			if (selectedNodes.length !== 1) return DomRoutes.pathUsers();
			const nodeId = selectedNodes[0];
			return `${DomRoutes.pathUsers()}?nodeid=${nodeId}`;
		};

		const selectedSongIds = getSelectedSongIds();

		const canAssignUsers = () => {
			if (isDirectorySelected()) return false;
			if (selectedNodes.length === 1) {
				const selectedPrefix = urlSafeBase64ToUnicode(selectedNodes[0]);
				const hasRule = selectedPrefixRules
					.filter(r => r.name === UserRoleDef.PATH_USER_LIST ||
						r.domain === UserRoleDomain.SITE
					)
					.some(r =>
						(r.path &&
							selectedPrefix.startsWith(normalizeOpeningSlash(r.path))) ||
						r.domain === UserRoleDomain.SITE
					);
				return hasRule;
			}
			return false;
		};

		const canDeletePath = () => {
			if (selectedNodes.length !== 1) return false;
			const selectedPrefix = urlSafeBase64ToUnicode(selectedNodes[0]);
			const hasRule = selectedPrefixRules
				.filter(r => r.name === UserRoleDef.PATH_DELETE ||
					r.domain === UserRoleDomain.SITE
				)
				.some(r =>
					(r.path &&
						selectedPrefix.startsWith(normalizeOpeningSlash(r.path))) ||
					r.domain === UserRoleDomain.SITE
				);
			return hasRule;
		};

		const canDownloadSelection = () => {
			if (isDirectorySelected()) return false;
			if (selectedNodes.length !== 1) return false;
			const songNodeInfo = firstNode(treeData[selectedNodes[0]]);
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

		const scrollToNode = useCallback((nodeId: string) => {
			const selector = `#${treeId}-${nodeId} .MuiTreeItem-label`;
			const el = document.querySelectorAll(selector)[0];
			if (el) {
				el.scrollIntoView({ block: "center", behavior: "smooth"});
			}
		},[]);

		const addEmptyDirectory = (
			nodes: Dictionary<ListData<SongTreeNodeInfo>>,
			fullPath: string
		) => {
			updateTree(nodes);
			const normalizedPath = normalizeOpeningSlash(fullPath);
			updateUrl(normalizedPath);
			const escapedNodeId = unicodeToUrlSafeBase64(normalizedPath)
				.replaceAll("=","\\=");
			setTimeout(() => {
				scrollToNode(escapedNodeId);
			});
		};

		const deleteNode = async () => {
			if (selectedNodes.length === 1) {
				const nodeId = selectedNodes[0];
				try {
					const requestObj = deletePrefix({ nodeId });
					const result = await requestObj.call();
					updateTree(result);
				}
				catch (err) {
					enqueueSnackbar(formatError(err),{ variant: "error"});
				}
			}
		};

		const onNodeLoaded = useCallback((
			node: SongTreeNodeInfo,
			nodeId: string
		) => {
			const escapedNodeId = nodeId.replaceAll("=","\\=");
			if (!isNodeDirectory(node)) return;
			if (nodeId !== urlNodeId) return;
			setSelectedNodes([nodeId]);
			scrollToNode(escapedNodeId);
		},[urlNodeId, setSelectedNodes, scrollToNode]);

		return (
			<>
				{(!!selectedSongIds.length || selectedPrefixRules) &&
				<div css={styles.toolbar}>
					{canEditSongInfo() && <Button
						component={Link}
						to={getSongEditUrl(selectedSongIds)}
					>
						Edit Song Info
					</Button>}
					{canDownloadSelection() &&  <SongListener
						audioId={selectedSongIds[0]}
					/>}
					{canAssignUsers() && <Button
						component={Link}
						to={getUserAssignUrl()}
					>
						Assign users
					</Button>}
					{isDirectorySelected() && selectedPrefix &&
						<DirectoryNewModalOpener
							add={addEmptyDirectory}
							prefix={selectedPrefix}
						/>}
					{isDirectorySelected() && selectedPrefix &&
						<SongUploadNewModalOpener
							add={onAddNewSong}
							prefix={selectedPrefix}
						/>}
					{canDeletePath() && <YesNoModalOpener
						promptLabel="Delete Path"
						message={`Are you sure you want to delete ${selectedPrefix}`}
						onYes={() => deleteNode()}
						onNo={() => {}}
					/>}
				</div>}
				<div id="dndRoot">
					{/*
						conditiionally render on document.getElementById
						so that it exists when passed as rootElement in options
					*/}
					{!!document.getElementById("dndRoot") && <DndProvider
						backend={HTML5Backend}
						options={{
							rootElement: document.getElementById("dndRoot"),
						}}
					>
						<SimpleTreeView
							selectedItems={selectedNodes}
							expandedItems={expandedNodes}
							onSelectedItemsChange={onNodeSelect}
							multiSelect
							id={treeId}
						>
							<SongDirectory
								prefix=""
								level={0}
								onNodeLoaded={onNodeLoaded}
							/>
						</SimpleTreeView>
					</DndProvider>}
				</div>
			</>
		);
	});