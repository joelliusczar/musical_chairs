#!/bin/bash

lib_path='/home/ubuntu/.local/lib/python2.7/site-packages/musical_chairs_gen'

if [ -e "lib_path"]; then
    rm -rf "$lib_path/*"
else
    mkdir -pv "$lib_path" 
fi

cp -v ./common/ "$lib_path/"

