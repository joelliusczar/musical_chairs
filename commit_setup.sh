#!/bin/sh

. ./radio_common.sh

app_path_cl=/srv/"$app_name"


#check if personal scripts folder exists, clear out if it does,
#delete otherwise
empty_dir_contents "$process_dir_cl"


#check if web application folder exists, clear out if it does,
#delete otherwise
empty_dir_contents "$app_path_cl"


setup_py3_env './src/api/' &&
sudo cp -rv ./src/api "$app_path_cl/" 

setup_py3_env './src/maintenance/' &&
cp -rv ./src/maintenance "$process_dir_cl"

echo "$?"

#set up react then copy
npm --prefix ./src/client i &&
npm run --prefix ./src/client build &&
mkdir -pv "$app_path_cl"/client &&
cp -rv ./src/client/build "$app_path_cl"/client/


sh ./light_setup.sh