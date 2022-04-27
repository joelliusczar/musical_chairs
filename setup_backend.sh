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

setup_dir_with_py "$api_src" "$web_root"/"$app_api_path_cl" || 
show_err_and_exit 

setup_nginx_confs || 
show_err_and_exit 