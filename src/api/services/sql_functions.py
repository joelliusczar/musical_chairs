from tinytag import TinyTag

def song_name(path, searchBase):
  songFullPath = (searchBase + "/" + path).encode('utf-8')
  try:
    tag = TinyTag.get(songFullPath)
    return tag.title
  except:
    return ""

def artist_name(path, searchBase):
  songFullPath = (searchBase + "/" + path).encode('utf-8')
  try:
    tag = TinyTag.get(songFullPath)
    return tag.artist
  except:
    return ""

def album_name(path, searchBase):
  songFullPath = (searchBase + "/" + path).encode('utf-8')
  try:
    tag = TinyTag.get(songFullPath)
    return tag.album
  except:
    return ""