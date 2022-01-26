#!/bin/sh

base_path="$(dirname "$0")/"
current_path=$(pwd)
cd "$base_path"

app_name='musical_chairs_app'
app_path=/var/www/"$app_name"

"$app_path"/api/env/bin/python3 "$app_path"/api/index.py