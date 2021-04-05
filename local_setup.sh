#!/bin/bash

if [ -n  "$LOCAL_TEST_PATH" ]; then
    usePath="$LOCAL_TEST_PATH"
else
    usePath="$HOME"/Library/Python/2.7/lib/python/site-packages
fi

if [ -e "$usePath"/musical_chairs_libs ]; then 
    rm -rf "$usePath"/musical_chairs_libs/*
else
    mkdir -pv "$usePath"/musical_chairs_libs 
fi

cp -rv ./src/common/* "$usePath"/musical_chairs_libs/