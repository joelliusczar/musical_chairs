#!/bin/sh

test_flag="$1"
[ "$test_flag" = "test" ] && defs_home='../' || defs_home="$HOME"/radio

. "$defs_home"/radio_common.sh

link_to_music_files