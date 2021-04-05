#!/bin/bash

lib_path='/home/ubuntu/.local/lib/python2.7/site-packages/musical_chairs_libs'

if [ -e "lib_path" ]; then
    rm -rf "$lib_path/"*
else
    mkdir -pv "$lib_path" 
fi

cp -rv ./src/common/* "$lib_path/"


if [ -e "/home/ubuntu/process" ]; then 
    rm -rf "/home/ubuntu/process/"*
else
    mkdir -pv "/home/ubuntu/process" 
fi

cp -rv ./src/processes/* "/home/ubuntu/process/"
