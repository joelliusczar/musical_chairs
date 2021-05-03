#!/bin/bash

lib_path='/home/ubuntu/.local/lib/python2.7/site-packages/musical_chairs_libs'
lib_path_py3='/home/ubuntu/.local/lib/python3.8/site-packages'

if [ -e "$lib_path" ]; then
    rm -rf "$lib_path/"*
else
    mkdir -pv "$lib_path" 
fi

if [ -e "$lib_path_py3" ]; then
    rm -rf "$lib_path_py3/"*
else
    mkdir -pv "$lib_path_py3" 
fi

cp -rv ./src/common/* "$lib_path/"
cp -rv ./src/common/* "$lib_path_py3/"


if [ -e "/home/ubuntu/process" ]; then 
    rm -rf "/home/ubuntu/process/"*
else
    mkdir -pv "/home/ubuntu/process" 
fi

cp -rv ./src/maintenance/* "/home/ubuntu/process/"
cp -rv ./src/processes/* "/home/ubuntu/process/"
