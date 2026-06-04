import React, { useCallback, useEffect, useState } from "react";
import { PlaylistEdit } from "./PlaylistEdit";
import {
	Calls,
} from "../../API_Calls/playlistCalls";
import { useForm } from "react-hook-form";
import {
	SongListDisplayItem,
} from "../../Types/song_info_types";
import {
	PlaylistInfo,
	PlaylistInfoForm,
	PlaylistsSongsInfo,
} from "../../Types/playlist_types";
import { Link, useParams, useNavigate } from "react-router-dom";
import { useSnackbar } from "notistack";
import { formatError } from "../../Helpers/error_formatter";
import {
	useCurrentUser,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext/AuthContext";
import {
	useDataWaitingReducer,
	dataDispatches as dispatches,
} from "../../Reducers/dataWaitingReducer";
import { isCallPending } from "../../Helpers/request_helpers";
import { Loader } from "../Shared/Loader";
import {
	Box,
	Table,
	TableBody,
	TableContainer,
	TableCell,
	TableHead,
	TableRow,
	Typography,
	Button,
} from "@mui/material";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import { 
	DomRoutes,
	CallStatus,
} from "../../constants";
import { YesNoModalOpener } from "../Shared/YesNoControl";
import {
	buildArrayQueryStr,
} from "../../Helpers/request_helpers";
import { PlaylistListener } from "./PlaylistListener";
import { yupResolver } from "@hookform/resolvers/yup";
import { viewSecurityOptions } from "./common";
import {
	usePlaylistData,
} from "../../Context_Providers/AppContext/AppContext";
import { DndProvider } from "react-dnd";
import {
	HTML5Backend,
} from "react-dnd-html5-backend";
import { PlaylistSongRow } from "./PlaylistSongRow";
import { Token } from "../../Types/generic_types";
import { UserRoleDef } from "../../constants";
import {
	useHasAnyRoles,
} from "../../Context_Providers/AuthContext/AuthContext";
import { playlistFormSchema } from "../../Types/Validation_Types/playlist";
import get from "just-safe-get";


const playlistInfoToFormData = (data: PlaylistInfo) => {
	const viewSecurityLevel = viewSecurityOptions
		.filter(o => o.id === data.viewsecuritylevel);
	const formData = {
		...data,
		displayname: data.displayname || "",
		viewsecuritylevel: viewSecurityLevel.length ?
			viewSecurityLevel[0] : viewSecurityOptions[0],
	};
	return formData;
};

const initialValues = {
	name: "",
	viewsecuritylevel: viewSecurityOptions[0],
	stations: [],
	rules: [],
};

export const PlaylistEditScreen = () => {

	const { enqueueSnackbar } = useSnackbar();
	const navigate = useNavigate();
	const pathVars = useParams();
	const currentUser = useCurrentUser();


	const [state, dispatch] 
		= useDataWaitingReducer<PlaylistsSongsInfo>(
			new RequiredDataStore({
				id: "",
				name: "",
				displayname: "",
				owner: currentUser,
				viewsecuritylevel: viewSecurityOptions[0].id,
				rules: [],
				songs: [],
			})
		);
	const { callStatus, error } = state;
	const isPending = isCallPending(callStatus);
	const [nextUpIndex, setNextUpIndex] = useState<number>(0);

	const {
		items: playlists,
		add: addPlaylist,
		update: updatePlaylist,
		remove: removePlaylist,
	} = usePlaylistData();

	const getPageUrl = (params: { name: string }) => {
		return DomRoutes.playlistEdit({
			ownerkey: pathVars.ownerkey || currentUser.username,
			playlistkey: params.name,
		});
	};
	
	const afterSubmit = (data: PlaylistInfo) => {
		reset(playlistInfoToFormData(data));
		navigate(getPageUrl({ name: data.name }), { replace: true});
	};
	

	const formMethods = useForm<PlaylistInfoForm>({
		defaultValues: initialValues,
		reValidateMode: "onSubmit",
		resolver: yupResolver(playlistFormSchema),
	});
	const { handleSubmit, reset } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			if (get(state, "data.id")) {
				const requestObj = Calls.update({
					id: state.data.id,
					data: {
						name: values.name,
						displayname: values.displayname || "",
						viewsecuritylevel: values.viewsecuritylevel.id,
						stations: values.stations,
					},
				});
				const playlist = await requestObj.call();
				enqueueSnackbar("Save successful", { variant: "success" });
				afterSubmit(playlist);
				updatePlaylist(playlist);
			}
			else {
				const requestObj = Calls.add({
					data: {
						name: values.name,
						displayname: values.displayname || "",
						viewsecuritylevel: values.viewsecuritylevel.id,
						stations: values.stations,
					},
				});
				const playlist = await requestObj.call();
				enqueueSnackbar("Save successful", { variant: "success" });
				afterSubmit(playlist);
				addPlaylist(playlist);
			}
		}
		catch (err) {
			enqueueSnackbar(formatError(err), { variant: "error" });
			console.error(err);
		}
	});

	const savedId = state.data.id;



	const canPlayPlaylists = useHasAnyRoles([
		UserRoleDef.PATH_DOWNLOAD,
	]);
	const canPlayThisPlaylist = () => {

		return canPlayPlaylists;
	};


	const canDeleteItem = () => {
		const ownerId = get(state, "data.owner.id");
		if (currentUser.id === ownerId) return true;
		return false;
	};


	const deleteItem = async () => {
		try {
			if (!savedId) return;

			const requestObj = Calls.remove({ id: savedId });
			await requestObj.call();
			enqueueSnackbar("Delete successful", { variant: "success" });
			const deletedPlaylist = playlists.filter(p => p.id === savedId);
			if (deletedPlaylist.length) {
				removePlaylist(deletedPlaylist[0]);
			}
			navigate(DomRoutes.playlistsPageAll(), { replace: true });
		}
		catch (err) {
			enqueueSnackbar(formatError(err), { variant: "error" });
		}
	};

	const removeSong = async (item: SongListDisplayItem) => {
		if (!savedId) return;
		try {
			const requestObj = Calls.removeSongs({
				ids: [item.id],
				playlistid: savedId,
			});
			await requestObj.call();
			enqueueSnackbar("Removal successful", { variant: "success" });
			dispatch(dispatches.update((state) => {
				const songs = [...state.data.songs].filter(s => s.id !== item.id);

				return {
					...state,
					data: {
						...state.data,
						songs,
					},
				};
			}));
		}
		catch (err) {
			enqueueSnackbar(formatError(err), { variant: "error" });
		}
	};

	const moveSong = async (songId: Token, order: number) => {
		if (!savedId) return;
		try {
			const requestObj = Calls.moveSong({
				playlistid: savedId,
				songid: songId,
				order,
			});
			await requestObj.call();
			enqueueSnackbar("Removal successful", { variant: "success" });
			dispatch(dispatches.update((state) => {
				
				const songs = [...state.data.songs];
				const movedSongOldIdx = songs.findIndex(s => s.id === songId);
				const song = songs[movedSongOldIdx];
				songs.splice(movedSongOldIdx, 1);
				songs.splice(order, 0, song);

				return {
					...state,
					data: {
						...state.data,
						songs,
					},
				};
			}));
		}
		catch (err) {
			enqueueSnackbar(formatError(err), { variant: "error" });
		}
	};


	const authReset = useCallback(() => {
		dispatch(dispatches.restart());
	}, [dispatch]);

	useAuthViewStateChange(authReset);


	useEffect(() => {
		if(pathVars.playlistkey && pathVars.ownerkey) {
			const playlistRequestObj = Calls.get({
				ownerkey: pathVars.ownerkey,
				playlistkey: pathVars.playlistkey,
			});
			if (!isPending) return;
			const fetch = async () => {
				try {
					dispatch(dispatches.started());
					const data = await playlistRequestObj.call();
					const formData = playlistInfoToFormData(data);
					reset(formData);
					dispatch(dispatches.done(data));
				}
				catch(err) {
					enqueueSnackbar(formatError(err), { variant: "error"});
					dispatch(dispatches.failed(formatError(err)));
				}
			};
			fetch();
			return () => playlistRequestObj.abortController.abort();
		}
		else {
			reset(initialValues);
		}
	}, [
		dispatch,
		isPending,
		pathVars.ownerkey,
		pathVars.playlistkey,
		enqueueSnackbar,
		reset,
	]);

	const loadStatus = pathVars.playlistkey ? callStatus: CallStatus.done;

	const queueNext = useCallback((step: number) => {
		setNextUpIndex(index => {
			return index + step;
		});
	},[setNextUpIndex]);

	const getNextUp = () => {
		if (!state.data) return null;
		if (nextUpIndex < state.data.songs.length && nextUpIndex >= 0) {
			return state.data.songs[nextUpIndex];
		}
		return null;
	};

	const songIdQueryStr = state.data?.songs?.length > 0 ?
		buildArrayQueryStr("ids", state.data.songs.map(i => i.id)) :
		"";



	return <Loader status={loadStatus} error={error}>
		<>
			{canDeleteItem() && <YesNoModalOpener
				promptLabel="Delete Playlist"
				message={`Are you sure you want to delete ${""}?`}
				onYes={() => deleteItem()}
				onNo={() => { }}
			/>}
		</>
		<PlaylistEdit
			formMethods={formMethods}
			callSubmit={callSubmit}
			referenceRecord={state.data}
		/>
		<Button
			component={Link}
			to={
				`${DomRoutes.songEdit()}${songIdQueryStr}`}
			disabled={(state.data?.songs?.length || 0) < 1}
		>
			Batch Edit Songs
		</Button>
		{state.data?.songs?.length > 0 ?
			<>
				<Box>
					{canPlayThisPlaylist() && savedId && <PlaylistListener
						audioItems={state.data.songs}
						nextUp={getNextUp()}
						queueNext={queueNext}
						parentId={savedId}
					/>}
				</Box>
				<DndProvider
					backend={HTML5Backend}
				>
					<TableContainer>
						<Table>
							<TableHead>
								<TableRow>
									<TableCell>Song</TableCell>
									<TableCell>Disc</TableCell>
									<TableCell>Artist</TableCell>
									<TableCell></TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{state.data.songs.map((item, idx) => 
									<PlaylistSongRow 
										key={`song_${idx}`}
										song={item}
										idx={idx}
										order={idx}
										removeSong={removeSong}
										moveSong={moveSong}
									/>)
								}
							</TableBody>
						</Table>
					</TableContainer>
				</DndProvider>
			</> :
			<Typography>No Songs</Typography>
		}
	</Loader>;
};

export default PlaylistEditScreen;