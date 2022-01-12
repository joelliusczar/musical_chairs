#!/bin/bash

lib_name='musical_chairs_libs'
app_name='musical_chairs_app'
radio_home="$HOME"/radio
build_home="$HOME"/Documents/builds
music_home="$HOME"/music
pyVersion=$(python3 -V)
pyMajor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /(\d+)\.\d+/')
pyMinor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /\d+\.(\d+)/')