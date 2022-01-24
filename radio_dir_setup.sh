#!/bin/sh

. ./radio_common.sh

cp ./templates/configs/config.yml "$config_file"
sed -i -e "s@<searchbase>@$music_home/@" -e "s@<dbname>@$sqlite_file@" "$config_file"

app_path_cl=/srv/"$app_name"


#check if personal scripts folder exists, clear out if it does,
#delete otherwise
empty_dir_contents "$maintenance_dir_cl"


#check if web application folder exists, clear out if it does,
#delete otherwise
empty_dir_contents "$app_path_cl"


setup_py3_env './src/api/' &&
sudo cp -rv ./src/api "$app_path_cl/" &&
sudo chown -R "$current_user": "$app_path_cl/"

echo 'creating maintenance dir'
setup_py3_env './src/maintenance/' &&
sudo cp -rv ./src/maintenance "$maintenance_dir_cl" &&
sudo chown -R "$current_user": "$maintenance_dir_cl"