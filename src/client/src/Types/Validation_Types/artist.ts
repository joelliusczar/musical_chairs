import { ArtistInfo } from "../../Types/song_info_types";
import { userOptionSchema } from "./user";
import * as Yup from "yup";


export const artistOptionSchema: Yup.ObjectSchema<ArtistInfo> = 
Yup.object()
	.shape({
		id: Yup.string().required(),
		name: Yup.string().required(),
		owner: userOptionSchema.required(),
	});