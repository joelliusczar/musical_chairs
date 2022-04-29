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


setup_env_api_file ||
show_err_and_exit
echo "PYTHONPATH='$src_path'" >> "$app_root"/"$env_api_file"

setup_py3_env "$utest_env_dir"

cp -v "$reference_src_db" "$app_root"/"$sqlite_file" || 
show_err_and_exit 