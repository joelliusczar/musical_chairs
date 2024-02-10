import { IdValue, Named, NamedIdItem } from "./generic_types";
import { PathsActionRule, ActionRule, User } from "./user_types";
import { StationTableData, StationInfo } from "./station_types";
import { VoidStore } from "../Reducers/reducerStores";
import {
	FieldValues,
} from "react-hook-form";

export interface ArtistInfo {
	id: IdValue
	name: string
	owner: User
}

export interface AlbumInfo {
	id: IdValue
	name: string
	year: number | null
	albumartist: ArtistInfo | null
	owner: User
}

export interface AlbumCreationInfo {
	name: string
	year?: number
	albumartist?: ArtistInfo
}

export interface NowPlayingInfo {
	song: string
	album: string
	artist: string
}

export interface SongListDisplayItem extends NamedIdItem {
	album: string | null
	artist: string | null
	path: string
	queuedtimestamp: number
	requestedtimestamp: number | null
	playedtimestamp: number | null
	rules: ActionRule[]
}

export interface CurrentPlayingInfo
	extends StationTableData<SongListDisplayItem>
{
	nowplaying: NowPlayingInfo | null
}


export class InitialQueueState extends VoidStore {
	data: CurrentPlayingInfo;

	constructor() {
		super();
		this.data = {
			items: [],
			totalrows: 0,
			stationrules: [],
			nowplaying: {
				song: "",
				album: "",
				artist: "",
			},
		};
	}
}

export interface SongTreeNodeInfo {
	path: string
	totalChildCount: number
	id: number | null
	name: string | null
	rules: PathsActionRule[]
}

export enum TouchTypes {
	set = "set",
	unset = "unset",
	edited = "edited",
}

export type TouchedObject = {
	[key: string]: TouchTypes
};

export interface SongInfoBase extends Named {
	path: string
	artists: ArtistInfo[]
	primaryartist: ArtistInfo
	album: AlbumInfo
	stations: StationInfo[]
	genre: string
}

export interface SongInfoForm extends SongInfoBase, FieldValues {
	rules: ActionRule[]
	touched: TouchedObject
}

export interface SongInfoApiSavura extends SongInfoBase {
	touched: string[]
}

export interface DirectoryInfo {
	prefix: string,
	suffix: string
};

export type UploadItem = {
	suffix: string,
	file: File
};

export interface MultiUploadInfo {
	files: UploadItem[],
};

export interface UploadInfo extends DirectoryInfo {
	files: File[] | null
}