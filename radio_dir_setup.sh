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

cp ./templates/configs/config.yml "$config_file" &&
sed -i -e "s@<searchbase>@$music_home/@" "$config_file" &&
sed -i -e "s@<dbname>@$sqlite_file@" "$config_file" &&
rm -f "$config_file"-e


#keep a copy in the parent radio directory
cp ./radio_common.sh "$radio_home"/radio_common.sh
cp ./icecast_check.sh "$radio_home"/icecast_check.sh
cp ./requirements.txt "$radio_home"/requirements.txt

#check if personal scripts folder exists, clear out if it does,
#delete otherwise
empty_dir_contents "$maintenance_dir_cl" &&
sudo -p 'Pass required for copying maintenance files: ' \
	cp -rv ./maintenance/* "$maintenance_dir_cl" &&
setup_py3_env "$maintenance_dir_cl" &&

mkdir -pv "$templates_dir_cl" &&
cp -rv ./templates/* "$templates_dir_cl" && 

sudo -p 'Pass required for changing owner of maintenance files: ' \
	chown -R "$current_user": "$maintenance_dir_cl" || 
show_err_and_exit 

#create the folder for the start up scripts
empty_dir_contents "$start_up_dir_cl" &&

sudo -p 'Pass required for copying start up files: ' \
	cp -v ./start_up/* "$start_up_dir_cl" &&
sudo -p 'Pass required for changing owner of start up files: ' \
	chown -R "$current_user": "$start_up_dir_cl" || 
show_err_and_exit 
