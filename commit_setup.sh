#!/bin/bash


lib_name='musical_chairs_libs'
app_name='musical_chairs_app'
lib_path="$HOME"/.local/lib/python2.7/site-packages/"$lib_name"
app_path=/var/www/"$app_name"

#check if python2 musical_chairs_libs already exists. cleans it out if it does
# creates it otherwise 
if [ -e "$lib_path" ]; then
    rm -rf "$lib_path/"*
else
    mkdir -pv "$lib_path" 
fi


#copy musical_chairs_libs to the now empty directory
cp -rv ./src/common/* "$lib_path/"

#check if personal scripts folder exists, clear out if it does,
#delete otherwise
if [ -e "$HOME"/process ]; then 
    rm -rf "$HOME"/process/*
else
    mkdir -pv "$HOME"/process
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
    packagePath='env/lib/python3.8/site-packages/'
    cd "$codePath"
    virtualenv env &&
    ./env/bin/pip3 install -r ./requirements.txt &&
    cd - &&
    mkdir "$codePath""$packagePath""$lib_name"/ &&
    cp -rv ./src/common/* "$codePath""$packagePath""$lib_name"/ 
)

setup_py3_env './src/api/' &&
cp -rv ./src/api "$app_path/" 

setup_py3_env './src/maintenance/' &&
cp -rv ./src/maintenance "$HOME"/process

echo "$?"

#set up react then copy
npm --prefix ./src/client i &&
npm run --prefix ./src/client build &&
mkdir -pv "$app_path"/client &&
cp -rv ./src/client/build "$app_path"/client/


sh ./light_setup.sh