#!/bin/sh

. ./radio_common.sh

cp ./templates/configs/config.yml "$config_file"
sed -i -e "s@<searchbase>@$music_home/@" -e "s@<dbname>@$sqlite_file@" "$config_file"

app_path_cl=/srv/"$app_name"

#keep a copy in the parent radio directory
test_flag="$1"
if [ "$test_flag" != "test" ]; then
	cp ./radio_common.sh "$radio_home"/radio_common.sh
	cp ./icecast_check.sh "$radio_home"/icecast_check.sh
fi

#check if personal scripts folder exists, clear out if it does,
#delete otherwise
empty_dir_contents "$maintenance_dir_cl"
cp ./radio_common.sh "$maintenance_dir_cl"/radio_common.sh
mkdir -pv "$templates_dir_cl" &&
cp -rv ./templates/* "$templates_dir_cl"

#check if web application folder exists, clear out if it does,
#delete otherwise
empty_dir_contents "$app_path_cl"


sudo cp -rv ./src/api/* "$app_path_cl/" &&
setup_py3_env "$app_path_cl" &&
sudo chown -R "$current_user": "$app_path_cl/"

echo 'creating maintenance dir'
sudo cp -rv ./maintenance/* "$maintenance_dir_cl" &&
setup_py3_env "$maintenance_dir_cl" &&
sudo chown -R "$current_user": "$maintenance_dir_cl"

sh ./light_setup.sh