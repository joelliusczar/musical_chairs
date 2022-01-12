#!/bin/bash

. ./radio_common.sh

web_app_path='src/api/'
maintenance_path='src/maintenance/'
base_path="$(dirname "$0")/"



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


setup_py3_env "$base_path""$web_app_path" 

setup_py3_env "$base_path""$maintenance_path"



