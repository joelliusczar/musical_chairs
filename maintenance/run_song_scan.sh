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
{ mc-python  <<EOF
from musical_chairs_libs.song_scanner import save_paths, update_metadata
print("Starting")
inserted = save_paths('${music_home}')
print(f"saving paths done: {inserted} inserted")
updated = update_metadata('${music_home}')
print(f"updating songs done: {updated}")
EOF
}
deactivate
