import { 
	Named, 
	NamedIdItem, 
	KeyValue, 
	IdValue,
	NamedTokenItem,
} from "./generic_types";
import { User, OwnerParams, ActionRule } from "./user_types";
import { SongListDisplayItem } from "./song_info_types";
import { StationInfo } from "./station_types";



export interface PlaylistCreationInfo extends Named {
	displayname: string
	viewsecuritylevel: IdValue
	stations: StationInfo[]
}

export interface PlaylistInfo extends NamedTokenItem {
	displayname?: string | null
	owner: User
	viewsecuritylevel: IdValue
	rules: ActionRule[]
}

export interface PlaylistsSongsInfo extends PlaylistInfo{
	songs: SongListDisplayItem[],
}

export type OwnedPlaylistParams = OwnerParams & {
	playlistkey?: KeyValue
}

export interface PlaylistInfoForm extends Named {
	// id?: Token
	displayname?: string
	// owner: User
	viewsecuritylevel: NamedIdItem
	stations: StationInfo[],
	// rules: ActionRule[],
}
