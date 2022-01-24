from sqlalchemy import select, desc
from musical_chairs_libs.station_manager import get_tag_pk
from musical_chairs_libs.tables import songs, SongsTags
from tinytag import TinyTag

def get_tag_song_catalogue(conn, searchBase, tagName, limit=50, offset=0):
  tagPK = get_tag_pk(tagName, conn)
  if not tagPK:
    return
  s = songs.c
  st = SongsTags.c
  query = select(s.songPK, s.path) \
    .select_from(SongsTags) \
    .join(songs, s.songPK == st.SongFK) \
    .where(st.tagFK = tagPK)
    .limit(limit)
    .offset(offset)
  records = conn.execute(query)
  for idx, row in enumerate(records):
    song_full_path = (searchBase + "/" + row["path"]).encode('utf-8')
    try:
        tag = TinyTag.get(song_full_path)
        yield { 
            'id': row["songPK"],
            'song': tag.title, 
            'album': tag.album,
            'artist': tag.artist,
        }
    except:
        yield {
            'id': row["songPK"]
        }

