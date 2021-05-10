#!/bin/bash

web_app_path='src/api'
api_env_path="$web_app_path/env"
libName='musical_chairs_libs'
default_py_path="$HOME"/Library/Python/2.7/lib/python/site-packages
default_py3_path="$HOME"/Library/Python/3.8/lib/python/site-packages

if [ -n  "$LOCAL_TEST_PATH" ]; then
    usePath="$LOCAL_TEST_PATH"
else
    usePath="$default_py_path"/"$libName"
fi

if [ -n "$LOCAL_TEST_PATH_PY_3" ]; then
    usePath_py3="$LOCAL_TEST_PATH_PY_3"
else
    usePath_py3="$default_py3_path"/"$libName"
fi

if [ -e "$usePath" ]; then 
    rm -rf "$usePath"/*
else
    mkdir -pv "$usePath" 
fi

if [ -e "$usePath_py3" ]; then 
    rm -rf "$usePath_py3"/*
else
    mkdir -pv "$usePath_py3" 
fi

proj_env_py3="$(dirname "$0")""$api_env_path"/lib/python3.8/site-packages
usePath_proj="$proj_env_py3"/"$libName"

if [ -e "$usePath_proj" ]; then 
    rm -rf "$usePath_proj"/*
else
    mkdir -pv "$usePath_proj" 
fi

cp -r ./src/common/* "$usePath"/
cp -r ./src/common/* "$usePath_py3"/
cp -r ./src/common/* "$usePath_proj"/

"$api_env_path"/bin/pip3 install -r "$web_app_path"/requirements.txt

sh ./light_setup.sh