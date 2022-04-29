#!/bin/sh

if [ -e ./radio_common.sh ]; then
. ./radio_common.sh
elif [ -e ../radio_common.sh ]; then
. ../radio_common.sh
elif [ -e "$HOME"/radio/radio_common.sh ]; then
. "$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

sh ./radio_dir_setup.sh &&

sh ./setup_backend.sh &&
sh ./setup_client.sh &&

if [ -n "$copy_db_flag" ]; then
	cp -v "$reference_src_db" "$app_root"/"$sqlite_file" || 
	show_err_and_exit 
fi