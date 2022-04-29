#!/bin/sh

if [ -e ./radio_common.sh ]; then
. ./radio_common.sh
elif [ -e ../radio_common.sh ]; then
. ../radio_common.sh
elif [ -e "$HOME"/radio/radio_common.sh ]; then
. "$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

link_to_music_files

env_path="$app_root"/"$maintenance_dir_cl"


export dbName="$app_root"/"$sqlite_file"
. "$env_path"/"$py_env"/bin/activate &&
# #python_env
{ python  <<EOF
from musical_chairs_libs.song_scanner import SongScanner
print("Starting")
stationService = SongScanner()
inserted = stationService.save_paths('${app_root}/${content_home}')
print(f"saving paths done: {inserted} inserted")
updated = stationService.update_metadata('${app_root}/${content_home}')
print(f"updating songs done: {updated}")
EOF
}
deactivate
