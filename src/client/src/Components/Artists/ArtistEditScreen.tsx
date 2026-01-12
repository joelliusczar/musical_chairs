import React, { useCallback, useEffect } from "react";
import { ArtistEdit } from "../Artists/ArtistEdit";
import {
	useArtistData,
} from "../../Context_Providers/AppContext/AppContext";
import { 
	update as saveArtist, 
	get as fetchArtist,
	removeRecordCaller as deleteArtist,
} from "../../API_Calls/artistCalls";
import { useForm } from "react-hook-form";
import {
	ArtistInfo,
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
import {
	isCallPending,
} from "../../Helpers/request_helpers";
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
import { openSongInTab } from "../../API_Calls/songInfoCalls";


const initialValues = {
	name: "",
};

export const ArtistEditScreen = () => {

	const id  = parseInt((useParams().id || "0"));
	const { enqueueSnackbar } = useSnackbar();
	const navigate = useNavigate();

	const [state, dispatch] = useDataWaitingReducer<SongListDisplayItem[]>(
		new RequiredDataStore([])
	);
	const { callStatus, error } = state;
	const isPending = isCallPending(callStatus);

	const canEditSongs = useHasAnyRoles([UserRoleDef.PATH_EDIT]);
	const canDownloadAnySong = useHasAnyRoles([UserRoleDef.PATH_DOWNLOAD]);

	const currentUser = useCurrentUser();

	const {
		update: updateArtist,
		remove: removeArtist,
	} = useArtistData();

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

	const formMethods = useForm<ArtistInfo>({
		defaultValues: {
			name: "",
		},
	});
	const { handleSubmit, reset, getValues } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const requestObj = saveArtist({ id, data: {
				name: values.name,
			} });
			const artist = await requestObj.call();
			enqueueSnackbar("Save successful", { variant: "success"});
			updateArtist(artist);
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
			const requestObj = deleteArtist({ id });
			await requestObj.call();
			removeArtist(getValues());
			enqueueSnackbar("Delete successful", { variant: "success"});
			navigate(DomRoutes.artistPage(), { replace: true });
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
			const requestObj = fetchArtist({
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
		<ArtistEdit 
			formMethods={formMethods}
			callSubmit={callSubmit}
		/>
		<>
			{canDeleteItem() && <YesNoModalOpener
				promptLabel="Delete Artist"
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
							<TableCell>Song</TableCell>
							<TableCell>Artist</TableCell>
							<TableCell></TableCell>
						</TableRow>
					</TableHead>
					<TableBody>
						{state.data.map((item,idx) => {
							return <TableRow key={`song_${idx}`}>
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

export default ArtistEditScreen;