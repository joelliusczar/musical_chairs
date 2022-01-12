#!/bin/bash

. ./radio_common.sh

PACMAN_CONST='pacman'

notInstalled() {
    echo "$1 not installed"
    exit 0
}

pkgMgr=''
pkgMgrChoice=''
if  pacman -V 2>/dev/null; then
    pkgMgrChoice="$PACMAN_CONST"
    pkgMgr='yes | sudo pacman -S'
fi

if [ -z "$pkgMgr" ]; then
    echo "No package manager set"
    exit 1
fi

if ! perl -v 2>/dev/null; then
    notInstalled
    #eval "$pkgMrg" perl
fi

if perl -e "exit 1 if index('$PATH','$HOME/.local/bin') != -1"; then
    echo 'Please add "$HOME/.local/bin" to path'
    echo 'Exiting'
    exit 1
fi


if ! python3 -V 2>/dev/null; then
    eval "$pkgMgr" python3
fi

if ! pip3 -V 2>/dev/null; then
    eval "$pkgMgr" python-pip
fi

if ! npm version 2>/dev/null; then
    eval "$pkgMgr" npm
fi

if ! [ -e "$build_home" ]; then
    mkdir -pv "$build_home"
fi

if ! [ -e "$radio_home" ]; then
    mkdir -pv "$radio_home"
fi

if [ "$pkgMgrChoice" = "$PACMAN_CONST" ]; then
    if ! icecast -v 2>/dev/null; then
        eval "$pkgMgr" icecast
    fi
fi

if ! ices -V 2>/dev/null; then
    ices_dir="$build_home"/ices
    rm -rf "$ices_dir"
    mkdir -pv "$ices_dir" 
    cd "$ices_dir"
    git clone https://github.com/joelliusczar/ices0.git
    cd ices0
    aclocal 
    autoreconf -fi
    automake --add-missing
    ./configure --prefix="$HOME"/.local \
        --with-python=/usr/bin/python3 \
        --with-moddir="$radio_home"/modules
    make
    make install   
fi


cp ./templates/configs/stream_keys.yml "$radio_home"/stream_keys.yml
