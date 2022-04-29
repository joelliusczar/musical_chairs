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


setup_env_api_file ||
	show_err_and_exit "Hello?"
#keep a copy in the parent radio directory
cp ./radio_common.sh "$app_trunk"/radio_common.sh
cp ./icecast_check.sh "$app_trunk"/icecast_check.sh
cp ./requirements.txt "$app_trunk"/requirements.txt

cp ./radio_common.sh "$app_root"/radio_common.sh
cp ./icecast_check.sh "$app_root"/icecast_check.sh
cp ./requirements.txt "$app_root"/requirements.txt

#check if personal scripts folder exists, clear out if it does,
#delete otherwise
setup_dir_with_py "$maintenance_src" "$app_root"/"$maintenance_dir_cl" || 
	show_err_and_exit 

setup_dir "$templates_src" "$app_root"/"$templates_dir_cl" || 
	show_err_and_exit 

#create the folder for the start up scripts
setup_dir "$start_up_src" "$app_root"/"$start_up_dir_cl" || 
	show_err_and_exit 

