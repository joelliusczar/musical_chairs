import json
import requests
import re
import warnings
from musical_chairs_libs.dtos_and_utilities import (
	AlbumInfo,
	ConfigAcessors,
	SongEditInfo
)


warnings.filterwarnings(action="ignore")
print(ConfigAcessors.dev_app_user_name())

formData = {
	"username": ConfigAcessors.dev_app_user_name(),
	"password": ConfigAcessors.dev_app_user_pw()
}
baseUrl = "https://musicalchairs.radio.fm/api/v1/"
#baseUrl = "https://localhost:8032/"

verify = True

response = requests.post(f"{baseUrl}accounts/open", data=formData, verify=verify)
data = json.loads(response.content)
print(data)
accessToken = data["access_token"]
headers = {
	"Authorization": f"Bearer {accessToken}",
	"x-back-key": ConfigAcessors.back_key()
}

response = requests.get(f"{baseUrl}albums/list", headers=headers, verify=verify)
# response = requests.get(f"{baseUrl}albums/97", headers=headers)
data = json.loads(response.content)
# print(data)

def get_track(song: SongEditInfo) -> int:
	try:
		return int(song.track or "-")
	except:
		print(song)
		return 0

# songResponse = requests.get(
# 		f"{baseUrl}song-info/songs/list/?albumId=97", 
# 		headers=headers
# 	)
# songData = json.loads(songResponse.content)
# print(songData)



flaggedAlbums: list[tuple[AlbumInfo, list[SongEditInfo]]] = []
for album in (AlbumInfo(**d) for d in data["items"]):
	albumId = album.id
	songResponse = requests.get(
		f"{baseUrl}song-info/songs/list/?albumId={albumId}", 
		headers=headers,
		verify=verify
	)
	songData = json.loads(songResponse.content)

	songList = [SongEditInfo(**d) for d in songData]
	# print(songData)
	try:
		for song in songList:
			# print(get_track(song))
			try:
				int(song.track or "$")
			except:
				print(album.name)
				flaggedAlbums.append((album, songList))
				break

	except Exception as e:
		print(e)
for album in flaggedAlbums:
	discMap: dict[str, list[SongEditInfo]] = {}
	for song in album[1]:
		discSegment = song.treepath.split("/")[-2]
		discList = discMap.get(discSegment, [])
		discList.append(song)
		discMap[discSegment] = discList
	
	discCount = len(discMap)
	for i, discSegment in enumerate(sorted(discMap.keys())):
		songs = discMap[discSegment]
		songs = sorted(songs, key=lambda s: s.track or s.treepath.split("/")[-1])
		print(f"{album[0].name} id: {album[0].id}")
		for j, song in enumerate(songs):
			song.discnum = i + 1
			if song.tracknum:
				continue
			print(song.treepath.split("/")[-1])
			print(song.track)
			try:
				if song.track is None:
					song.track = str(j)
				song.tracknum = float(song.track or j)
			except:
				if match := re.match(r"(\d+)([a-zA-Z])([a-zA-Z]*)", song.track or ""):
					groups = match.groups()
					print(groups)
					s1 = int(match.group(1))
					s2 = ord(match.group(2).lower()) - ord("a") + 1
					s3 = (ord(match.group(3).lower()) - ord("a") + 1) \
						if len(groups)  > 2 and groups[2] else 0
					song.tracknum = s1 + (s2/10) + (s3/100)
				elif match := re.match(r"\D(\d+)-(\d+)", song.track or ""):
					s1 = int(match.group(1) + match.group(2))
					song.tracknum = s1
				elif match := re.match(r"s(\d+)", song.track or ""):
					s1 = int(match.group(1))
					song.tracknum = s1
					discCount += 1
					song.discnum = discCount
				else:
					raise
				
			saveResponse = requests.put(
				f"{baseUrl}song-info/songs/{song.id}",
				headers=headers,
				data=json.dumps(song.model_dump()),
				verify=verify
			)
			print(saveResponse.status_code)
			print(song.track)
			print(song.tracknum)
			if saveResponse.status_code != 200:
				# print(song.model_dump_json())
				print(saveResponse.content)
				
			assert saveResponse.status_code == 200
			

