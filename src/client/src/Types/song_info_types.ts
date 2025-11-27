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
	versionnote: string
	stations: StationInfo[]
	owner: User
}


export interface AlbumCreationInfo {
	name: string
	year?: number
	albumartist?: ArtistInfo
	stations: StationInfo[]
	versionnote: string
}

export interface NowPlayingInfo {
	name: string
	album: string
	artist: string
}

export interface SongListDisplayItem extends NamedIdItem {
	album: string | null
	artist: string | null
	path: string
	track: number | null
	disc: number | null
	queuedtimestamp: number
	playedtimestamp: number | null
	rules: ActionRule[]
}

export interface CollectionQueuedItem extends NamedIdItem {
	creator: string | null
	itemtype: string
	itemtypeid: number
	year: number | null
	description: string | null
	rules: ActionRule[]
}

export interface CurrentPlayingInfo
	extends StationTableData<SongListDisplayItem>
{
	nowplaying: SongListDisplayItem | null
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
				id: 0,
				name: "",
				album: "",
				artist: "",
				track: null,
				disc: null,
				queuedtimestamp: 0,
				playedtimestamp: null,
				rules: [],
				path: "",
			},
		};
	}
}

export interface DirectoryInfoNodeInfo {
	path: string,
	nodeId: string
};

export interface BreadcrumbNodeInfo extends DirectoryInfoNodeInfo {
	segment: string,
};

export interface DirectoryTransferSource {
	path: string,
	prefix: string
};

export interface DirectoryTransfer extends DirectoryTransferSource {
	newprefix: string
};

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

export interface TrackListing {
	name: string
	tracknum: number
	track: string | null
}

export interface SongInfoBase extends Named {
	path: string
	artists: ArtistInfo[]
	primaryartist: ArtistInfo
	album: AlbumInfo
	stations: StationInfo[]
	genre: string
	track: string
	tracknum: number
	disc: number | null
}


export interface SongInfoForm extends SongInfoBase, FieldValues {
	rules: ActionRule[]
	touched: TouchedObject
	trackinfo: {[id: IdValue]: TrackListing}
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

export interface SongsAlbumInfo extends AlbumInfo{
	songs: SongListDisplayItem[],
}

export interface SongsArtistInfo extends ArtistInfo{
	songs: SongListDisplayItem[],
}