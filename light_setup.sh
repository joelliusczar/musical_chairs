#!/bin/bash

if [ -e "$HOME"/start_up ]; then
    rm -rf"$HOME"/start_up/*
else
    mkdir -pv "$HOME"/start_up 
fi

cp -v ./start_up/* "$HOME"/start_up/
