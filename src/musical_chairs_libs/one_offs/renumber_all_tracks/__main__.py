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
baseUrl = "https://localhost:8032/"

response = requests.post(f"{baseUrl}accounts/open", data=formData, verify=False)
data = json.loads(response.content)
print(data)
accessToken = data["access_token"]
headers = {
	"Authorization": f"Bearer {accessToken}",
	"x-back-key": EnvManager.back_key()
}

#response = requests.get(f"{baseUrl}albums/list", headers=headers, verify=False)
response = requests.get(f"{baseUrl}albums/97", headers=headers, verify=False)
data = json.loads(response.content)
print(data)

songResponse = requests.get(
		f"{baseUrl}song-info/songs/list/?albumId=97", 
		headers=headers,
		verify=False
	)
songData = json.loads(songResponse.content)
print(songData)
# for album in (AlbumInfo(**d) for d in data["items"]):

# 	songResponse = requests.get(
# 		f"{baseUrl}song-info/songs/list/?albumId={album.id}", 
# 		headers=headers
# 	)
# 	songData = json.loads(songResponse.content)
# 	try:
# 		for song in (SongEditInfo(**d) for d in songData):
# 			try:
# 				int(song.track or "-")
# 			except:
# 				break
# 				print(album)
# 	except:
# 		print(songData)