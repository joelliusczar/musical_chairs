#!/bin/bash

. ./radio_common.sh

app_path=/var/www/"$app_name"


#check if personal scripts folder exists, clear out if it does,
#delete otherwise
if [ -e "$radio_home"/process ]; then 
    rm -rf "$radio_home"/process/*
else
    mkdir -pv "$radio_home"/process
fi



#check if web application folder exists, clear out if it does,
#delete otherwise
if [ -e "$app_path" ]; then
    rm -rf "$app_path/"*
else
    mkdir -pv "$app_path" 
fi

#set up the python environment, then copy 
setup_py3_env() (
    codePath="$1"
    packagePath="env/lib/python$pyMajor.$pyMinor/site-packages/"
    cd "$codePath"
    python3 -m venv "$codePath"/env
    . "$codePath"/env/bin/activate
    python3 -m pip install -r ./requirements.txt &&
    cd - &&
    mkdir "$codePath""$packagePath""$lib_name"/ &&
    cp -rv ./src/common/* "$codePath""$packagePath""$lib_name"/ 
)

setup_py3_env './src/api/' &&
cp -rv ./src/api "$app_path/" 

setup_py3_env './src/maintenance/' &&
cp -rv ./src/maintenance "$radio_home"/process

echo "$?"

#set up react then copy
npm --prefix ./src/client i &&
npm run --prefix ./src/client build &&
mkdir -pv "$app_path"/client &&
cp -rv ./src/client/build "$app_path"/client/


sh ./light_setup.sh