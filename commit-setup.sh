#!/bin/bash

lib_path='/home/ubuntu/.local/lib/python2.7/site-packages/musical_chairs_libs'

if [ -e "lib_path" ]; then
    rm -rf "$lib_path/"*
else
    mkdir -pv "$lib_path" 
fi

cp -rv ./src/common/* "$lib_path/"

if [ -e /usr/local/etc/modules ]; then
    sudo rm -rf /usr/local/etc/modules/*
else
    sudo mkdir -pv /usr/local/etc/modules
fi

sudo cp -rv ./src/play/* /usr/local/etc/modules/

