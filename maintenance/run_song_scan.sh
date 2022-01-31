#!/bin/sh

test_flag="$1"
[ "$test_flag" = "test" ] && defs_home='.' || defs_home="$HOME"/radio

. "$defs_home"/radio_common.sh

link_to_music_files

env_path="$maintenance_dir_cl"


export config_file
. "$env_path"/env/bin/activate &&
{ python3  <<EOF
from musical_chairs_libs.song_scanner import save_paths, update_metadata
print("Starting")
inserted = save_paths('${music_home}')
print(f"saving paths done: {inserted} inserted")
updated = update_metadata('${music_home}')
print(f"updating songs done: {updated}")
EOF
}
deactivate
