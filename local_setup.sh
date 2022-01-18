#!/bin/sh

. ./radio_common.sh

web_app_path='src/api/'
maintenance_path='src/maintenance/'
base_path="$(dirname "$0")/"




setup_py3_env "$base_path""$web_app_path" 

setup_py3_env "$base_path""$maintenance_path"



