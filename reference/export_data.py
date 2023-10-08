
from sqlalchemy import create_engine
from typing import Optional

#"/Users/joelpridgen/Documents/Code/radio/musical_chairs/reference/songs_db.sqlite"
engine = create_engine(
	"sqlite:////Users/joelpridgen/Documents/Code/radio/musical_chairs/reference/songs_db.sqlite"
	
)
conn = engine.connect()

res = conn.exec_driver_sql("SELECT * FROM Users;").fetchall()

def handle_str(val: Optional[str]):
	if val is None:
		return "NULL"
	return f"'{val}'"

# with open("/Users/joelpridgen/Documents/Code/radio/musical_chairs/reference/users.sql","w") as f:
# 	for row in res:
# 		f.write("INSERT INTO `users` "
# 			"(`pk` ,`username` ,`displayname` ,`hashedpw` ,`email` ,"
# 			"`isdisabled` ,`creationtimestamp` ,`dirroot` ,`viewsecuritylevel`)"
# 			f" VALUES({row[0]}, '{row[1]}', '{row[2]}', CONVERT('{row[3]}' USING BINARY), '{row[4]}', "
# 			f"{row[5] or 'NULL'}, {row[6]}, '{row[7]}', {row[8] or 'NULL'});")

res = conn.exec_driver_sql("SELECT * FROM Artists;").fetchall()

# with open("/Users/joelpridgen/Documents/Code/radio/musical_chairs/reference/artists.sql","w") as f:
# 	for row in res:
# 		name = (row[1] or 'NULL').replace("'",r"\'")
# 		f.write("INSERT INTO `artists` "
# 			"(`pk` ,`name` ,`lastmodifiedbyuserfk` ,`lastmodifiedtimestamp` ,`ownerfk`) "
# 			f"VALUES ({row[0] or 'NULL'}, '{name}', {row[2] or 'NULL'}, {row[3] or 0}, {row[4] or 1});\n")

res = conn.exec_driver_sql("SELECT * FROM Albums;").mappings().fetchall()

# with open("/Users/joelpridgen/Documents/Code/radio/musical_chairs/reference/albums.sql","w") as f:
# 	for row in res:
# 		name = (row["name"] or 'NULL').replace("'",r"\'")
# 		f.write("INSERT INTO `albums` "
# 			"(`pk` ,`name` , `albumartistfk`, `year`, `lastmodifiedbyuserfk`,`lastmodifiedtimestamp` ,`ownerfk`) "
# 			f"VALUES ({row['pk'] or 'NULL'}, '{name}', "
# 			f"{row['albumArtistFk'] or 'NULL'}, {row['year'] or 'NULL'}, "
# 			f"{row['lastModifiedByUserFk'] or 1}, "
# 			f"{row['lastModifiedTimestamp'] or 0}, {row['ownerFk'] or 1});\n")


res = conn.exec_driver_sql("SELECT * FROM Songs;").mappings().fetchall()


# with open("/Users/joelpridgen/Documents/Code/radio/musical_chairs/reference/songs.sql","w") as f:
# 	for row in res:
# 		name = handle_str(row['name'].replace("'",r"\'") if row['name'] else None)
# 		path = handle_str(row['path'].replace("'",r"\'") if row['path'] else None)

		# f.write("INSERT INTO `songs` "
		# 	"(`pk` ,"
		# 	"`path` , "
		# 	"`name` , "
		# 	"`albumfk`,"
		# 	" `track`, "
		# 	" `disc`, "
		# 	" `genre`, "
		# 	" `explicit`, "
		# 	" `bitrate`, "
		# 	" `comment`, "
		# 	" `lyrics`, "
		# 	" `duration`, "
		# 	" `samplerate`, "
		# 	"`lastmodifiedbyuserfk`,"
		# 	"`lastmodifiedtimestamp` "
		# 	",`isdirectoryplaceholder`) "
		# 	"VALUES ("
		# 	f"{row['pk'] or 'NULL'}, "
		# 	f"{path}, "
		# 	f"{name}, "
		# 	f"{row['albumFk'] or 'NULL'}, "
		# 	f"{handle_str(row['track'])}, "
		# 	f"{row['disc'] or 'NULL'}, "
		# 	f"{handle_str(row['genre'])}, "
		# 	f"{row['explicit'] or 'NULL'}, "
		# 	f"{row['bitrate'] or 'NULL'}, "
		# 	f"{handle_str(row['comment'])}, "
		# 	f"{handle_str(row['lyrics'])}, "
		# 	f"{row['duration'] or 'NULL'}, "
		# 	f"{row['sampleRate'] or 'NULL'}, "
		# 	f"{row['lastModifiedByUserFk'] or 1}, "
		# 	f"{row['lastModifiedTimestamp'] or 0}, "
		# 	f"{row['isDirectoryPlaceholder'] or 0}"
		# 	");\n")


res = conn.exec_driver_sql("SELECT * FROM SongsArtists;").mappings().fetchall()

# with open("/Users/joelpridgen/Documents/Code/radio/musical_chairs/reference/songsartists.sql","w") as f:
# 	for row in res:
# 		artistFk = row['artistFk']
# 		if artistFk == 52:
# 			artistFk = 51
# 		elif artistFk == 273:
# 			artistFk = 272

# 		f.write("INSERT INTO `songsartists` "
# 			"(`pk` ,`songfk` , `artistfk`, `isprimaryartist`, `comment`, "
# 			"`lastmodifiedbyuserfk` ,`lastmodifiedtimestamp`) "
# 			f"VALUES ({row['pk'] or 'NULL'}, {row['songFk'] or 'NULL'}, "
# 			f"{artistFk or 'NULL'}, {row['isPrimaryArtist'] or 0}, "
# 			f"{handle_str(row['comment'])}, "
# 			f"{row['lastModifiedByUserFk'] or 1}, {row['lastModifiedTimestamp'] or 0});\n")



res = conn.exec_driver_sql("SELECT * FROM Stations;").mappings().fetchall()

# with open("/Users/joelpridgen/Documents/Code/radio/musical_chairs/reference/stations.sql","w") as f:
# 	for row in res:


# 		f.write("INSERT INTO `stations` "
# 			"(`pk` ,`name` , `displayname`, `procid`, "
# 			"`lastmodifiedbyuserfk` ,`lastmodifiedtimestamp`,"
# 			"`ownerfk`, `requestsecuritylevel`, `viewsecuritylevel`"
# 			") "
# 			f"VALUES ({row['pk'] or 'NULL'}, {handle_str(row['name'])}, "
# 			f"{handle_str(row['displayName'])}, NULL, "
# 			f"{row['lastModifiedByUserFk'] or 1}, {row['lastModifiedTimestamp'] or 0}, "
# 			f"{row['ownerFk'] or 1}, {row['requestSecurityLevel'] or 'NULL'}, "
# 			f"{row['viewSecurityLevel'] or 'NULL'}"
# 			");\n")


res = conn.exec_driver_sql("SELECT * FROM StationsSongs;").mappings().fetchall()

# with open("/Users/joelpridgen/Documents/Code/radio/musical_chairs/reference/stationssongs.sql","w") as f:
# 	for row in res:


# 		f.write("INSERT INTO `stationssongs` "
# 			"(`songfk` ,`stationfk` , "
# 			"`lastmodifiedbyuserfk` ,`lastmodifiedtimestamp`"
# 			") "
# 			f"VALUES ({row['songFk'] or 'NULL'}, {row['stationFk'] or 'NULL'}, "
# 			f"{row['lastModifiedByUserFk'] or 1}, {row['lastModifiedTimestamp'] or 0} "
# 			");\n")
		

res = conn.exec_driver_sql("SELECT * FROM UserRoles;").mappings().fetchall()

with open("/Users/joelpridgen/Documents/Code/radio/musical_chairs/reference/userroles.sql","w") as f:
	for row in res:


		f.write("INSERT INTO `userroles` "
			"(`userfk` ,`role` , "
			"`creationTimestamp` ,`count`, "
			"`span` ,`priority`"
			") "
			f"VALUES ({row['userFk'] or 'NULL'}, {handle_str(row['role'])}, "
			f"{row['creationTimestamp'] or 1}, {row['count'] or 0}, "
			f"{row['span'] or 1}, {row['priority'] or 'NULL'} "
			");\n")