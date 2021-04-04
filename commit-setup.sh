#!/bin/bash

lib_path='/home/ubuntu/.local/lib/python2.7/site-packages/musical_chairs_libs'

if [ -e "lib_path" ]; then
    rm -rf "$lib_path/"*
else
    mkdir -pv "$lib_path" 
fi

cp -rv ./src/common/* "$lib_path/"

sudo find ~ -type f \( -name '*.pyc' -o -name '*.py' \) -exec rm {} \;

sudo cp -rv ./src/play/* ~/