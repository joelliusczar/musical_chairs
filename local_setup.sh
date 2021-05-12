#!/bin/bash
lib_name='musical_chairs_libs'
web_app_path='src/api/'
maintenance_path='src/maintenance/'
base_path="$(dirname "$0")/"
sys_path_2_7="$HOME"/Library/Python/2.7/lib/python/site-packages/"$lib_name"


if [ -e "$sys_path_2_7" ]; then 
    rm -rf "$sys_path_2_7"/*
else
    mkdir -pv "$sys_path_2_7" 
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
    cp -rv "$base_path"/src/common/* "$codePath""$packagePath""$lib_name"/ 
)

setup_py3_env "$base_path""$web_app_path" 

setup_py3_env "$base_path""$maintenance_path"

cp -r ./src/common/* "$sys_path_2_7"/


