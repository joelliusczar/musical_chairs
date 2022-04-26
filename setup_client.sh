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

#in theory, this should be sourced by .bashrc
#but sometimes there's an interactive check that ends the sourcing early
if [ -z "$NVM_DIR" ]; then
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
  # This loads nvm bash_completion
  [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion" 
fi

#check if web application folder exists, clear out if it does,
#delete otherwise
empty_dir_contents "$app_path_client_cl" || 
show_err_and_exit 


export REACT_APP_API_ADDRESS="$full_url"
export REACT_APP_API_VERSION=v1
#set up react then copy
#install packages
npm --prefix "$client_src" i &&
#build code (transpile it)
npm run --prefix "$client_src" build &&
#copy built code to new location
sudo -p 'Pass required for copying client files: ' \
  cp -rv "$client_src"/build/* "$app_path_client_cl" &&
sudo -p 'Pass required for changing owner of client files: ' \
 chown -R "$current_user": "$app_path_client_cl" || 
show_err_and_exit 