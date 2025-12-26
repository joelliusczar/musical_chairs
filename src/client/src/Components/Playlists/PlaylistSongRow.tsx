import React from "react";
import {
	TableCell,
	TableRow,
	Button,
} from "@mui/material";
import { useDrag, useDrop } from "react-dnd";
import {
	SongListDisplayItem,
} from "../../Types/song_info_types";
import {
	useHasAnyRoles,
} from "../../Context_Providers/AuthContext/AuthContext";
import { Link } from "react-router-dom";
import { OptionsButton } from "../Shared/OptionsButton";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import { 
	UserRoleDef,
	DomRoutes,
} from "../../constants";
import { openSongInTab } from "../../API_Calls/songInfoCalls";
import { IdValue, IdItem } from "../../Types/generic_types";

type PlaylistSongRowProps = {
	song: SongListDisplayItem,
	idx: number,
	order: number,
	removeSong: (song: SongListDisplayItem) => Promise<void>,
	moveSong: (songId: IdValue, order: number) => Promise<void> | void
};

export const PlaylistSongRow = (props: PlaylistSongRowProps) => {
	const { song, removeSong, idx, order, moveSong } = props;

	const canEditSongs = useHasAnyRoles([UserRoleDef.PATH_EDIT]);
	const canDownloadAnySong = useHasAnyRoles([UserRoleDef.SONG_DOWNLOAD]);
	const canEditPlaylist = useHasAnyRoles([UserRoleDef.PLAYLIST_EDIT]);

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

		if (canEditPlaylist) rowButtonOptions.push({
			label: "Remove",
			onClick: () => removeSong(item),
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


	const [, dragRef] = useDrag<IdItem>({
		type: "row",
		item: { id: song.id },
	});

	const [{ isOver },dropRef] = useDrop<
		IdItem,
		unknown,
		{ isOver: boolean }
	>(() => ({
		accept: "row",
		drop: async (item, monitor) => {
			if(!monitor.didDrop()) {
				moveSong(item.id, order);
			}
		},
		collect: (monitor) => ({
			isOver: !!monitor.isOver({ shallow: true }) && !!monitor.canDrop(),
		}),
	}));

	const attachRefs = (el: HTMLTableRowElement | null) => {
		dragRef(el);
		dropRef(el);
	};

	return (<TableRow
		ref={attachRefs}
		style={ isOver ? { border: "1px solid"} : {}}
	>
		<TableCell>{song.name}</TableCell>
		<TableCell>{song.disc}</TableCell>
		<TableCell>{song.artist}</TableCell>
		<TableCell>{rowButton(song, idx)}</TableCell>
	</TableRow>);
};