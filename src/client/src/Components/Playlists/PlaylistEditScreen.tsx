import React, { useCallback, useEffect, useState } from "react";
import { PlaylistEdit } from "./PlaylistEdit";
import {
	checkValuesCaller,
	get as getPlaylist,
	add as addPlaylist,
	update as updatePlaylist,
	remove as deletePlaylist,
} from "../../API_Calls/playlistCalls";
import { useForm } from "react-hook-form";
import {
	SongListDisplayItem,
} from "../../Types/song_info_types";
import {
	PlaylistInfo,
	PlaylistInfoForm,
} from "../../Types/playlist_types";
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
import { 
	UserRoleDef,
	DomRoutes,
	RulePriorityLevel,
	CallStatus,
} from "../../constants";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import { OptionsButton } from "../Shared/OptionsButton";
import { YesNoModalOpener } from "../Shared/YesNoControl";
import {
	buildArrayQueryStr,
} from "../../Helpers/request_helpers";
import { PlaylistListener } from "./PlaylistListener";
import { openSongInTab } from "../../API_Calls/songInfoCalls";
import * as Yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";

const viewSecurityOptions = [
	{
		id: RulePriorityLevel.PUBLIC,
		name: "Public",
	},
	{
		id: RulePriorityLevel.ANY_USER,
		name: "Any User",
	},
	{
		id: RulePriorityLevel.INVITED_USER,
		name: "Invited Users Only",
	},
	{
		id: RulePriorityLevel.OWENER_USER,
		name: "Private",
	},
];

const playlistInfoToFormData = (data: PlaylistInfo) => {
	const viewSecurityLevel = viewSecurityOptions
		.filter(o => o.id === data.viewsecuritylevel);
	const formData = {
		...data,
		viewsecuritylevel: viewSecurityLevel.length ?
			viewSecurityLevel[0] : viewSecurityOptions[0],
	};
	return formData;
};

const validatePhraseIsUnused = async (
	value: string | undefined,
	context: Yup.TestContext<Partial<PlaylistInfoForm>>
) => {
	const id = context?.parent?.id;
	if (!value) return true;
	const requestObj = checkValuesCaller({ id, values: {
		[context.path]: value,
	}});
	const used = await requestObj.call();
	return !(context.path in used) || !used[context.path];
};

const initialValues = {
	name: "",
	viewsecuritylevel: viewSecurityOptions[0],
};

export const PlaylistEditScreen = () => {

	const { enqueueSnackbar } = useSnackbar();
	const navigate = useNavigate();
	const pathVars = useParams();
	const currentUser = useCurrentUser();


	const [state, dispatch] = useDataWaitingReducer<SongListDisplayItem[]>(
		new RequiredDataStore([])
	);
	const { callStatus, error } = state;
	const isPending = isCallPending(callStatus);
	const [nextUpIndex, setNextUpIndex] = useState<number>(0);

	const canEditSongs = useHasAnyRoles([UserRoleDef.PATH_EDIT]);
	const canDownloadAnySong = useHasAnyRoles([UserRoleDef.SONG_DOWNLOAD]);


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

	const schema = Yup.object().shape({
		name: Yup.string().required()
			.matches(/^[a-zA-Z0-9_]*$/, "Name can only contain a-zA-Z0-9_")
			.test(
				"name",
				(value) => `${value.path} is already used`,
				validatePhraseIsUnused
			),
		requestsecuritylevel: Yup.object().required().test(
			"requestsecuritylevel",
			"Request Security cannot be public or lower than view security",
			(value, context) => {
				return (value.id) !== RulePriorityLevel.PUBLIC
					&& value.id >= context.parent.viewsecuritylevel.id;
			}
		),
	});

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
		resolver: yupResolver(schema),
	});
	const { handleSubmit, reset, getValues, watch } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			if (values.id) {
				const requestObj = updatePlaylist({
					id: values.id, 
					data: {
						name: values.name,
						description: values.description,
						viewsecuritylevel: values.viewsecuritylevel.id,
					},
				});
				const playlist = await requestObj.call();
				enqueueSnackbar("Save successful", { variant: "success" });
				afterSubmit(playlist);
			}
			else {
				const requestObj = addPlaylist({
					data: {
						name: values.name,
						description: values.description,
						viewsecuritylevel: values.viewsecuritylevel.id,
					},
				});
				const playlist = await requestObj.call();
				enqueueSnackbar("Save successful", { variant: "success" });
				afterSubmit(playlist);
			}
		}
		catch (err) {
			enqueueSnackbar(formatError(err), { variant: "error" });
			console.error(err);
		}
	});

	const savedId = watch("id");

	const canDeleteItem = () => {
		const ownerId = getValues("owner.id");
		if (currentUser.id === ownerId) return true;
		return false;
	};


	const deleteItem = async () => {
		try {
			if (!savedId) return;

			const requestObj = deletePlaylist({ id: savedId });
			await requestObj.call();
			enqueueSnackbar("Delete successful", { variant: "success" });
			navigate(DomRoutes.playlistsPage(), { replace: true });
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
			const requestObj = getPlaylist({
				ownerkey: pathVars.ownerkey,
				playlistkey: pathVars.playlistkey,
			});
			if (!isPending) return;
			const fetch = async () => {
				try {
					dispatch(dispatches.started());
					const data = await requestObj.call();
					const formData = playlistInfoToFormData(data);
					reset(formData);
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
		pathVars.ownerkey,
		pathVars.playlistkey,
		enqueueSnackbar,
		reset,
	]);

	const loadStatus = pathVars.playlistkey ? callStatus: CallStatus.done;

	const playNext = useCallback((step: number) => {
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
						playNext={playNext}
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

export default PlaylistEditScreen;