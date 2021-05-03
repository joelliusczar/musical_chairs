#!/bin/bash

if [ -n  "$LOCAL_TEST_PATH" ]; then
    usePath="$LOCAL_TEST_PATH"
else
    usePath="$HOME"/Library/Python/2.7/lib/python/site-packages
fi

if [ -n "$LOCAL_TEST_PATH_PY_3" ]; then
    usePath_py3="$LOCAL_TEST_PATH_PY_3"
else
    usePath_py3="$HOME"/Library/Python/3.8/lib/python/site-packages
fi

if [ -e "$usePath"/musical_chairs_libs ]; then 
    rm -rf "$usePath"/musical_chairs_libs/*
else
    mkdir -pv "$usePath"/musical_chairs_libs 
fi

if [ -e "$usePath_py3"/musical_chairs_libs ]; then 
    rm -rf "$usePath_py3"/musical_chairs_libs/*
else
    mkdir -pv "$usePath_py3"/musical_chairs_libs 
fi

cp -r ./src/common/* "$usePath"/musical_chairs_libs/
cp -r ./src/common/* "$usePath_py3"/musical_chairs_libs/