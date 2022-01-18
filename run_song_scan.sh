#!/bin/sh

. ./radio_common.sh

link_to_music_files

scan_home=${1:-"$process_dir_cl"}


py_maintenance_path="$scan_home"/maintenance

. "$py_maintenance_path"/env/bin/activate &&
python3 -m pip list &&
python3 "$py_maintenance_path"/scan_new_songs.py
deactivate
