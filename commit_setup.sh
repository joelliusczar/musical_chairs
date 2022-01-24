#!/bin/sh

. ./radio_common.sh

sh ./radio_dir_setup.sh

echo "$?"

#set up react then copy
npm --prefix ./src/client i &&
npm run --prefix ./src/client build &&
mkdir -pv "$app_path_cl"/client &&
cp -rv ./src/client/build "$app_path_cl"/client/


sh ./light_setup.sh