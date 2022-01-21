#!/bin/sh

. ./radio_common.sh

link_to_music_files

env_path="$process_dir_cl"/maintenance
[ "$test_flag" = "test" ] && script_path='./src/maintenance' || script_path="$env_path"

py_maintenance_path="$env_path"/maintenance

. "$env_path"/env/bin/activate &&
python3 "$script_path"/scan_new_songs.py
deactivate
