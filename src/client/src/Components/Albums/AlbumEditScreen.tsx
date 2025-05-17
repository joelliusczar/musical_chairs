import React, { useCallback, useEffect } from "react";
import { AlbumEdit } from "../Albums/AlbumEdit";
import {
	useAlbumData,
} from "../../Context_Providers/AppContext/AppContext";
import { 
	update as saveAlbum, 
	get as fetchAlbum,
	remove as deleteAlbum,
} from "../../API_Calls/albumCalls";
import { downloadSong } from "../../API_Calls/songInfoCalls";
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



const initialValues = {
	name: "",
};

export const AlbumEditScreen = () => {

	const id  = parseInt((useParams().id || "0"));
	const { enqueueSnackbar } = useSnackbar();
	const navigate = useNavigate();

	const [state, dispatch] = useDataWaitingReducer<SongListDisplayItem[]>(
		new RequiredDataStore([])
	);
	const { callStatus, error } = state;
	const isPending = isCallPending(callStatus);

	const canEditSongs = useHasAnyRoles([UserRoleDef.PATH_EDIT]);
	const canDownloadAnySong = useHasAnyRoles([UserRoleDef.SONG_DOWNLOAD]);

	const currentUser = useCurrentUser();

	const {
		add: addAlbum,
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
			onClick: () => downloadSong(item.id),
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
		},
	});
	const { handleSubmit, reset, getValues } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const requestObj = saveAlbum({ id, data: {
				name: values.name,
				year: values.year || undefined,
				albumartist: values.albumartist || undefined,
			} });
			const album = await requestObj.call();
			enqueueSnackbar("Save successful", { variant: "success"});
			addAlbum(album);
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
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
			const requestObj = deleteAlbum({ id });
			await requestObj.call();
			removeAlbum(getValues());
			enqueueSnackbar("Delete successful", { variant: "success"});
			navigate(DomRoutes.albumPage(), { replace: true });
		}
		catch (err) {
			enqueueSnackbar(formatError(err),{ variant: "error"});
		}
	};


	const authReset = useCallback(() => {
		dispatch(dispatches.restart());
	}, [dispatch]);

	useAuthViewStateChange(authReset);

	useEffect(() => {
		if(id) {
			const requestObj = fetchAlbum({
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
				catch(err) {
					enqueueSnackbar(formatError(err), { variant: "error"});
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


	return <Loader status={callStatus} error={error}>
		<AlbumEdit 
			formMethods={formMethods}
			callSubmit={callSubmit}
		/>
		<>
			{canDeleteItem() && <YesNoModalOpener
				promptLabel="Delete Album"
				message={`Are you sure you want to delete ${""}?`}
				onYes={() => deleteItem()}
				onNo={() => {}}
			/>}
		</>
		{state.data?.length > 0 ? 
			<TableContainer>
				<Table>
					<TableHead>
						<TableRow>
							<TableCell>Track</TableCell>
							<TableCell>Song</TableCell>
							<TableCell>Artist</TableCell>
							<TableCell></TableCell>
						</TableRow>
					</TableHead>
					<TableBody>
						{state.data.map((item,idx) => {
							return <TableRow key={`song_${idx}`}>
								<TableCell>{item.track}</TableCell>
								<TableCell>{item.name}</TableCell>
								<TableCell>{item.artist}</TableCell>
								<TableCell>{rowButton(item, idx)}</TableCell>
							</TableRow>;
						})}
					</TableBody>
				</Table>
			</TableContainer> :
			<Typography>No Songs</Typography>
		}
	</Loader>;
};

export default AlbumEditScreen;