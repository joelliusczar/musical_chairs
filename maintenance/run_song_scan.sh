#!/bin/sh

test_flag="$1"
[ "$test_flag" = "test" ] && defs_home='../' || defs_home="$HOME"/radio

. "$defs_home"/radio_common.sh

link_to_music_files

if [ "$test_flag" = "test" ]; then 
  env_path='./src/maintenance' 
else 
  env_path="$maintenance_dir_cl"
fi

export config_file
. "$env_path"/env/bin/activate &&
python3 "$env_path"/scan_new_songs.py
deactivate
