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

create_db() {
    echo "creating $sqlite_file"
    sqlite3 "$sqlite_file" ".read './sql_scripts/data_def_1.sql'" &&
    sqlite3 "$sqlite_file" ".read './sql_scripts/insert_tags_1.sql'" &&
    sqlite3 "$sqlite_file" ".read './sql_scripts/security_def_1.sql'"
}

if [ -e "$sqlite_file" ]; then
    echo 'The database already exits. Do you want to start from scratch? Y to confirm'
    read db_choice
    if [ "$db_choice" = 'Y' ]; then
        rm -f "$sqlite_file"
        create_db
        db_res="$?"
    else
        echo 'Using existing db'
        db_res=1
    fi
else 
    create_db
    db_res="$?"
fi

cp ./templates/configs/config.yml "$config_file"
sed -i -e "s@<searchbase>@$HOME@" -e "s@<dbname>@$sqlite_file@" "$config_file"

link_to_music_files

#"$db_res" && sh ./commit_setup.sh 
#sh ./run_song_scan.sh
