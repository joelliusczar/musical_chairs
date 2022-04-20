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

setup_config_file ||
	show_err_and_exit

#keep a copy in the parent radio directory
cp ./radio_common.sh "$radio_home"/radio_common.sh
cp ./icecast_check.sh "$radio_home"/icecast_check.sh
cp ./requirements.txt "$radio_home"/requirements.txt

#check if personal scripts folder exists, clear out if it does,
#delete otherwise
setup_dir_with_py './maintenance' "$maintenance_dir_cl" || 
	show_err_and_exit 

setup_dir './templates' "$templates_dir_cl" || 
	show_err_and_exit 

#create the folder for the start up scripts
setup_dir './start_up' "$start_up_dir_cl" || 
	show_err_and_exit 

