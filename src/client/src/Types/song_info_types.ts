import { IdType, Named, NamedIdItem } from "./generic_types";
import { PathsActionRule, ActionRule, User } from "./user_types";
import { StationTableData, StationInfo } from "./station_types";
import { VoidStore } from "../Reducers/reducerStores";
import {
	FieldValues,
} from "react-hook-form";

export interface ArtistInfo {
	id: IdType
	name: string
	owner: User
};

export interface AlbumInfo {
	id: IdType
	name: string
	year: number | null
	albumArtist: ArtistInfo | null
	owner: User
};

export interface AlbumCreationInfo {
	name: string
	year?: number
	albumArtist?: ArtistInfo
}

export interface NowPlayingInfo {
	song: string
	album: string
	artist: string
};

export interface SongListDisplayItem extends NamedIdItem {
	album: string | null
	artist: string | null
	path: string
	queuedTimestamp: number
	requestedTimestamp: number | null
	playedTimestamp: number | null
	rules: ActionRule[]
}

export interface CurrentPlayingInfo
	extends StationTableData<SongListDisplayItem>
{
	nowPlaying: NowPlayingInfo | null
}


export class InitialQueueState extends VoidStore {
	data: CurrentPlayingInfo

	constructor() {
		super();
		this.data = {
			items: [],
			totalRows: 0,
			stationRules: [],
			nowPlaying: {
				song: "",
				album: "",
				artist: "",
			},
		}
	}
};

export interface SongTreeNodeInfo {
	path: string
	totalChildCount: number
	id: number | null
	name: string | null
	rules: PathsActionRule[]
};

export enum TouchTypes {
	set = "set",
	unset = "unset",
	edited = "edited",
};

export type TouchedObject = {
	[key: string]: TouchTypes
};

export interface SongInfoBase extends Named {
	path: string
	artists: ArtistInfo[]
	primaryArtist: ArtistInfo
	album: AlbumInfo
	stations: StationInfo[]
	genre: string
}

export interface SongInfoForm extends SongInfoBase, FieldValues {
	rules: ActionRule[]
	touched: TouchedObject
};

export interface SongInfoApiSavura extends SongInfoBase {
	touched: string[]
}