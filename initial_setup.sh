#!/bin/sh

. ./radio_common.sh


if ! perl -v 2>/dev/null; then
    eval "$pkgMrg" perl
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
    ices_build_dir="$build_home"/ices
    rm -rf "$ices_build_dir"
    mkdir -pv "$ices_build_dir" 
    cd "$ices_build_dir"
    git clone https://github.com/joelliusczar/ices0.git
    cd ices0
    aclocal &&
    autoreconf -fi &&
    automake --add-missing &&
    ./configure --prefix="$HOME"/.local \
        --with-python=/usr/bin/python3 \
        --with-moddir="$pyModules_dir" &&
    make &&
    make install &&
    cd "$build_home" &&
    rm -rf "$ices_build_dir"
fi

sqlite3 "$sqlite_file" ./sql_scripts/data_def_1.sql
sqlite3 "$sqlite_file" ./sql_scripts/insert_tags_1.sql
sqlite3 "$sqlite_file" ./sql_scripts/security_def_1.sql

config_file="$radio_config"/config.yml
cp ./templates/configs/config.yml "$config_file"
sed -i -e "s/<searchbase>/$HOME/" -e "s/<dbname>/$sqlite_file/" "$config_file"

link_to_music_files