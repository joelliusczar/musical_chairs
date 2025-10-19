import json
import requests
from musical_chairs_libs.services import EnvManager
from musical_chairs_libs.dtos_and_utilities import (AlbumInfo, SongEditInfo)

print(EnvManager.dev_app_user_name())

formData = {
	"username": EnvManager.dev_app_user_name(),
	"password": EnvManager.dev_app_user_pw()
}

baseUrl = "https://musicalchairs.radio.fm/api/v1/"
# baseUrl = "https://localhost:8032/"

response = requests.post(f"{baseUrl}accounts/open", data=formData)
data = json.loads(response.content)
print(data)
accessToken = data["access_token"]
headers = {
	"Authorization": f"Bearer {accessToken}",
	"x-back-key": EnvManager.back_key()
}

response = requests.get(f"{baseUrl}albums/list", headers=headers)
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



for album in (AlbumInfo(**d) for d in data["items"]):
	albumId = album.id
	songResponse = requests.get(
		f"{baseUrl}song-info/songs/list/?albumId={albumId}", 
		headers=headers
	)
	songData = json.loads(songResponse.content)
	# print(songData)
	try:
		for song in (SongEditInfo(**d) for d in songData):
			# print(get_track(song))
			try:
				int(song.track or "$")
			except:
				print(song.track)
				print(album.id)
				print(album.name)
				break
	except:
		print(songData)