#!/bin/sh

if [ -e ./radio_common.sh ]; then
. ./radio_common.sh
elif [ -e ../radio_common.sh]; then
. ../radio_common.sh
elif [ -e "$HOME"/radio/radio_common.sh]; then
. "$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

link_to_music_files

env_path="$maintenance_dir_cl"


export config_file
. "$env_path"/env/bin/activate &&
# #python_env
{ python  <<EOF
from fastapi import Depends
from musical_chairs_libs.dependencies import song_scanner
print("Starting")
stationService = Depends(song_scanner)
inserted = stationService.save_paths('${music_home}')
print(f"saving paths done: {inserted} inserted")
updated = stationService.update_metadata('${music_home}')
print(f"updating songs done: {updated}")
EOF
}
deactivate
