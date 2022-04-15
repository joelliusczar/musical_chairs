#!/bin/sh

if [ -e ./radio_common.sh ]; then
. ./radio_common.sh test
elif [ -e ../radio_common.sh ]; then
. ../radio_common.sh test
elif [ -e "$HOME"/radio/radio_common.sh ]; then
. "$HOME"/radio/radio_common.sh test
else
	echo "radio_common.sh not found"
	exit 1
fi


setup_config_file ||
show_err_and_exit
echo "PYTHONPATH='$src_path'" >> "$config_file"

cp -v './reference/songs_db' "$sqlite_file" || 
show_err_and_exit 