import { IdValue, Named, NamedTokenItem, Token } from "./generic_types";
import { ActionRule, User } from "./user_types";
import { StationTableData, StationInfo } from "./station_types";
import { VoidStore } from "../Reducers/reducerStores";
import {
	FieldValues,
} from "react-hook-form";

export interface ArtistInfo {
	id: Token
	name: string
	owner: User
}

export interface AlbumInfo {
	id: Token
	name: string
	year: number | null
	albumartist: ArtistInfo | null
	versionnote: string
	stations: StationInfo[]
	owner: User
	rules: ActionRule[]
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

export interface SongListDisplayItem extends NamedTokenItem {
	album: string | null
	artist: string | null
	treepath: string
	track: number | null
	discnum: number | null
	queuedtimestamp: number
	playedtimestamp: number | null
	rules: ActionRule[]
}

export interface CatalogueItem extends NamedTokenItem {
	parentname: string
	creator: string | null
	itemtype: string
	requesttypeid: number
	year: number | null
	description: string | null
	rules: ActionRule[]
	owner: User
	playedcount: number
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
				id: "",
				name: "",
				album: "",
				artist: "",
				track: null,
				discnum: null,
				queuedtimestamp: 0,
				playedtimestamp: null,
				rules: [],
				treepath: "",
			},
		};
	}
}

export interface DirectoryInfoNodeInfo {
	treepath: string,
	nodeId: string
};

export interface BreadcrumbNodeInfo extends DirectoryInfoNodeInfo {
	segment: string,
};

export interface DirectoryTransferSource {
	treepath: string,
	prefix: string
};

export interface DirectoryTransfer extends DirectoryTransferSource {
	newprefix: string
};

export interface SongTreeNodeInfo {
	treepath: string
	totalChildCount: number
	id: Token | null
	name: string | null
	rules: ActionRule[]
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
	treepath: string
	artists: ArtistInfo[]
	primaryartist: ArtistInfo
	album: AlbumInfo
	stations: StationInfo[]
	genre: string
	track: string
	tracknum: number
	discnum: number | null
}


export interface SongInfoForm extends SongInfoBase, FieldValues {
	rules: ActionRule[]
	touched: TouchedObject
	trackinfo: {[id: Token]: TrackListing}
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