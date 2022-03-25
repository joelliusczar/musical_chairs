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

export config_file
. "$app_path_cl"/env/bin/activate &&
# see #python_env
uvicorn --app-dir "$app_path_cl" --host 0.0.0.0 --port 8032 "index:app" &
