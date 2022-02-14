#!/bin/sh

if [ -e ./radio_common.sh ]; then
. ./radio_common.sh
elif [ -e ../radio_common.sh]; then
. ../radio_common.sh
elif [ -e "$HOME"/radio/radio_common.sh]; then
. "$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

#check if web application folder exists, clear out if it does,
#delete otherwise
empty_dir_contents "$app_path_client_cl"


#set up react then copy

#install packages
npm --prefix "$client_src" i &&
#build code (transpile it)
npm run --prefix "$client_src" build &&
#copy built code to new location
sudo cp -rv "$client_src"/build "$app_path_client_cl"
sudo chown -R "$current_user": "$app_path_client_cl"