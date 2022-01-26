#!/bin/sh

test_flag="$1"
[ "$test_flag" = "test" ] && defs_home='../' || defs_home="$HOME"/radio

. "$defs_home"/radio_common.sh

app_name='musical_chairs_app'
app_path=/var/www/"$app_name"

"$app_path"/api/env/bin/python3 "$app_path"/api/index.py