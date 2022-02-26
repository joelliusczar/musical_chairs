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

empty_dir_contents "$app_path_cl" &&

cp ./templates/configs/web_config.yml "$http_config" &&

#replace the static dir place holder in the web config that's been copied
sed -i -e "s@<staticdir>@$app_path_client_cl@" "$http_config" &&
rm -f "$http_config"-e

sudo -p 'Pass rquired for copying api files: ' \
  cp -rv "$api_src"/* "$app_path_cl/" &&
setup_py3_env "$app_path_cl" &&
sudo -p 'Pass required for changing owner of copied files: ' \
  chown -R "$current_user": "$app_path_cl/" || 
show_err_and_exit 