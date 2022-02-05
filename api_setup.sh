#!/bin/sh

. ./radio_common.sh

app_path_cl=/srv/"$app_name"

#check if web application folder exists, clear out if it does,
#delete otherwise
empty_dir_contents "$app_path_cl"


sudo cp -rv ./src/api/* "$app_path_cl/" &&
setup_py3_env "$app_path_cl" &&
sudo chown -R "$current_user": "$app_path_cl/"


#set up react then copy
npm --prefix ./src/client i &&
npm run --prefix ./src/client build &&
sudo mkdir -pv "$app_path_cl"/client &&
sudo cp -rv ./src/client/build "$app_path_cl"/client/