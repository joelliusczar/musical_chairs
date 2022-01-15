#!/bin/bash

. ./radio_common.sh

link_to_music_files

pyMaintenancePath="$radio_home"/process/maintenance
"$pyMaintenancePath"/env/bin/python3 "$pyMaintenancePath"/scan_new_songs.py
