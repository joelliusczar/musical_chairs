import React, { useCallback, useEffect, useState } from "react";
import { AlbumEdit } from "../Albums/AlbumEdit";
import {
	useAlbumData,
} from "../../Context_Providers/AppContext/AppContext";
import {
	Calls,
} from "../../API_Calls/albumCalls";
import { useForm } from "react-hook-form";
import {
	AlbumInfo,
	SongListDisplayItem,
} from "../../Types/song_info_types";
import { Link, useParams, useNavigate } from "react-router-dom";
import { useSnackbar } from "notistack";
import { formatError } from "../../Helpers/error_formatter";
import {
	useCurrentUser,
	useHasAnyRoles,
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
import { UserRoleDef, DomRoutes } from "../../constants";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import { OptionsButton } from "../Shared/OptionsButton";
import { YesNoModalOpener } from "../Shared/YesNoControl";
import {
	buildArrayQueryStr,
} from "../../Helpers/request_helpers";
import { PlaylistListener } from "../Playlists/PlaylistListener";
import { openSongInTab } from "../../API_Calls/songInfoCalls";



const initialValues = {
	name: "",
};

export const AlbumEditScreen = () => {

	const id = parseInt((useParams().id || "0"));
	const { enqueueSnackbar } = useSnackbar();
	const navigate = useNavigate();

	const [state, dispatch] = useDataWaitingReducer<SongListDisplayItem[]>(
		new RequiredDataStore([])
	);
	const { callStatus, error } = state;
	const isPending = isCallPending(callStatus);
	const [nextUpIndex, setNextUpIndex] = useState<number>(0);

	const canEditSongs = useHasAnyRoles([UserRoleDef.PATH_EDIT]);
	const canDownloadAnySong = useHasAnyRoles([UserRoleDef.SONG_DOWNLOAD]);

	const currentUser = useCurrentUser();

	const {
		update: updateAlbum,
		remove: removeAlbum,
	} = useAlbumData();

	const rowButton = (item: SongListDisplayItem, idx: number) => {
		const rowButtonOptions = [];
		const canEditThisSong = anyConformsToAnyRule(
			item?.rules,
			[UserRoleDef.PATH_EDIT]
		);
		const canDownloadThisSong = anyConformsToAnyRule(
			item?.rules,
			[UserRoleDef.PATH_DOWNLOAD]
		);
		if (canEditSongs || canEditThisSong) rowButtonOptions.push({
			label: "Edit",
			link: `${DomRoutes.songEdit()}?ids=${item.id}`,
		});

		if (canDownloadAnySong || canDownloadThisSong) rowButtonOptions.push({
			label: "Download",
			onClick: () => openSongInTab(item.id),
		});

		return (rowButtonOptions.length > 1 ? <OptionsButton
			id={`queue-row-btn-${idx}`}
			options={rowButtonOptions}
		/> :
			<Button
				variant="contained"
				component={Link}
				to={`${DomRoutes.songEdit()}?ids=${item.id}`}
			>
				{(canEditSongs || canEditThisSong) ? "Edit" : "View"}
			</Button>);
	};

	const formMethods = useForm<AlbumInfo>({
		defaultValues: {
			name: "",
			albumartist: null,
			versionnote: "",
		},
	});
	const { handleSubmit, reset, getValues } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const requestObj = Calls.update({
				id, data: {
					name: values.name,
					year: values.year || undefined,
					albumartist: values.albumartist || undefined,
					stations: values.stations,
					versionnote: values.versionnote,
				},
			});
			const album = await requestObj.call();
			enqueueSnackbar("Save successful", { variant: "success" });
			updateAlbum(album);
		}
		catch (err) {
			enqueueSnackbar(formatError(err), { variant: "error" });
			console.error(err);
		}
	});



	const canDeleteItem = () => {
		const ownerId = getValues("owner.id");
		if (currentUser.id === ownerId) return true;
		return false;
	};


	const deleteItem = async () => {
		try {
			const requestObj = Calls.remove({ id });
			await requestObj.call();
			removeAlbum(getValues());
			enqueueSnackbar("Delete successful", { variant: "success" });
			navigate(DomRoutes.albumPage(), { replace: true });
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
		if (id) {
			const requestObj = Calls.get({
				id,
			});
			if (!isPending) return;
			const fetch = async () => {
				try {
					dispatch(dispatches.started());
					const data = await requestObj.call();
					reset(data);
					dispatch(dispatches.done(data.songs));
				}
				catch (err) {
					enqueueSnackbar(formatError(err), { variant: "error" });
					dispatch(dispatches.failed(formatError(err)));
				}
			};
			fetch();
			return () => requestObj.abortController.abort();
		}
		else {
			reset(initialValues);
		}
	}, [
		dispatch,
		isPending,
		id,
		enqueueSnackbar,
		reset,
	]);

	const queueNext = useCallback((step: number) => {
		setNextUpIndex(index => {
			return index + step;
		});
	},[setNextUpIndex]);

	const getNextUp = () => {
		if (!state.data) return null;
		if (nextUpIndex < state.data.length && nextUpIndex >= 0) {
			return state.data[nextUpIndex];
		}
		return null;
	};

	const songIdQueryStr = state.data?.length > 0 ?
		buildArrayQueryStr("ids", state.data.map(i => i.id)) :
		"";


	return <Loader status={callStatus} error={error}>
		<>
			{canDeleteItem() && <YesNoModalOpener
				promptLabel="Delete Album"
				message={`Are you sure you want to delete ${""}?`}
				onYes={() => deleteItem()}
				onNo={() => { }}
			/>}
		</>
		<AlbumEdit
			id={id}
			formMethods={formMethods}
			callSubmit={callSubmit}
		/>
		<Button
			component={Link}
			to={
				`${DomRoutes.songEdit()}${songIdQueryStr}`}
			disabled={(state.data?.length || 0) < 1}
		>
			Batch Edit Songs
		</Button>
		{state.data?.length > 0 ?
			<>
				<Box>
					<PlaylistListener
						audioItems={state.data}
						nextUp={getNextUp()}
						queueNext={queueNext}
						parentId={id}
					/>
				</Box>
				<TableContainer>
					<Table>
						<TableHead>
							<TableRow>
								<TableCell>Track</TableCell>
								<TableCell>Song</TableCell>
								<TableCell>Disc</TableCell>
								<TableCell>Artist</TableCell>
								<TableCell></TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{state.data.map((item, idx) => {
								return <TableRow key={`song_${idx}`}>
									<TableCell>{item.track}</TableCell>
									<TableCell>{item.name}</TableCell>
									<TableCell>{item.disc}</TableCell>
									<TableCell>{item.artist}</TableCell>
									<TableCell>{rowButton(item, idx)}</TableCell>
								</TableRow>;
							})}
						</TableBody>
					</Table>
				</TableContainer>
			</> :
			<Typography>No Songs</Typography>
		}
	</Loader>;
};

export default AlbumEditScreen;