#!/bin/bash


lib_name='musical_chairs_libs'
app_name='musical_chairs_app'
lib_path="$HOME"/.local/lib/python2.7/site-packages/"$lib_name"
lib_path_py3="$HOME"/.local/lib/python3.8/site-packages/"$lib_name"
app_path=/var/www/"$app_name"

#check if python2 musical_chairs_libs already exists. cleans it out if it does
# creates it otherwise 
if [ -e "$lib_path" ]; then
    rm -rf "$lib_path/"*
else
    mkdir -pv "$lib_path" 
fi

#check if python3 musical_chairs_libs already exists. cleans it out if it does
# creates it otherwise 
if [ -e "$lib_path_py3" ]; then
    rm -rf "$lib_path_py3/"*
else
    mkdir -pv "$lib_path_py3" 
fi

#copy musical_chairs_libs to the now empty directory
cp -rv ./src/common/* "$lib_path/"
cp -rv ./src/common/* "$lib_path_py3/"

#check if personal scripts folder exists, clear out if it does,
#delete otherwise
if [ -e "$HOME"/process ]; then 
    rm -rf "$HOME"/process/*
else
    mkdir -pv "$HOME"/process
fi

#copy personal scripts to the now empty directory
cp -rv ./src/maintenance/* "$HOME"/process/


#check if web application folder exists, clear out if it does,
#delete otherwise
if [ -e "$app_path" ]; then
    rm -rf "$app_path/"*
else
    mkdir -pv "$app_path" 
fi

#set up the python environment, then copy 
cd ./src/api
virtualenv env &&
./env/bin/pip3 install -r ./requirements.txt &&
cd - &&
cp -rv ./src/common/* ./src/api/env/lib/python3.8/site-packages/ &&
cp -rv ./src/api "$app_path/"

#set up react then copy
npm --prefix ./src/client i &&
npm run --prefix ./src/client build &&
mkdir -pv "$app_path"/client &&
cp -rv ./src/client/build "$app_path"/client/


