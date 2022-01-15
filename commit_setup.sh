#!/bin/sh

. ./radio_common.sh

app_path=/srv/"$app_name"


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