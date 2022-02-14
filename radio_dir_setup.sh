#!/bin/sh

. ./radio_common.sh

cp ./templates/configs/config.yml "$config_file"
sed -i -e "s@<searchbase>@$music_home/@" -e "s@<dbname>@$sqlite_file@" "$config_file"


#keep a copy in the parent radio directory
cp ./radio_common.sh "$radio_home"/radio_common.sh
cp ./icecast_check.sh "$radio_home"/icecast_check.sh
cp ./requirements.txt "$radio_home"/requirements.txt

#check if personal scripts folder exists, clear out if it does,
#delete otherwise
empty_dir_contents "$maintenance_dir_cl"
sudo cp -rv ./maintenance/* "$maintenance_dir_cl" &&
setup_py3_env "$maintenance_dir_cl" &&

mkdir -pv "$templates_dir_cl" &&
cp -rv ./templates/* "$templates_dir_cl"

sudo chown -R "$current_user": "$maintenance_dir_cl"

#create the folder for the start up scripts
empty_dir_contents "$start_up_dir_cl"

sudo cp -v ./start_up/* "$start_up_dir_cl"
sudo chown -R "$current_user": "$start_up_dir_cl"
