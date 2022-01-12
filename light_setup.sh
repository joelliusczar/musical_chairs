#!/bin/bash


. ./radio_common.sh

if [ -e "$radio_home"/start_up ]; then
    rm -rf"$radio_home"/start_up/*
else
    mkdir -pv "$radio_home"/start_up 
fi

cp -v ./start_up/* "$radio_home"/start_up/
