#!/bin/bash

[ -n "$radio_common_imported" ] && return

radio_common_imported='radio_common_imported'
lib_name='musical_chairs_libs'
app_name='musical_chairs_app'
radio_home="$HOME"/radio
ices_configs_dir="$radio_home"/ices_configs
pyModules_dir="$radio_home"/pyModules
build_home="$HOME"/Documents/builds
music_home="$HOME"/music
radio_config="$radio_home"/config
db_dir="$radio_home"/db
sqlite_file="$db_dir"/songs_db
pyVersion=$(python3 -V)
pyMajor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /(\d+)\.\d+/')
pyMinor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /\d+\.(\d+)/')

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

aws_role() {
    echo 'music_reader'
}

s3_name() {
    echo 'joelradio'
}


link_to_music_files() {
    if [ ! -e "$music_home"/radio/Soundtrack ]; then 
        if [ -n "$IS_RADIO_LOCAL_DEV" ]; then
            s3fs "$(s3_name)" "$music_home"/radio/ 
        else
            s3fs "$(s3_name)" "$music_home"/radio/ -o iam_role="$(aws_role)"
        fi
    fi
    res="$?"
    echo 'Music files should exist now'
    return "$res"
}

#set up the python environment, then copy 
setup_py3_env() (
    codePath="$1"
    packagePath="env/lib/python$pyMajor.$pyMinor/site-packages/"
    cd "$codePath"
    python3 -m venv "$codePath"/env
    . "$codePath"/env/bin/activate
    python3 -m pip install -r ./requirements.txt &&
    cd - &&
    mkdir "$codePath""$packagePath""$lib_name"/ &&
    cp -rv ./src/common/* "$codePath""$packagePath""$lib_name"/ 
)

[ ! -e "$radio_home" ] && mkdir -pv "$radio_home"
[ ! -e "$ices_configs_dir" ] && mkdir -pv "$ices_configs_dir"
[ ! -e "$build_home" ] && mkdir -pv "$build_home"
[ ! -e "$music_home" ] && mkdir -pv "$music_home"
[ ! -e "$pyModules_dir" ] && mkdir -pv "$pyModules_dir"
[ ! -e "$radio_config" ] && mkdir -pv "$radio_config"
[ ! -e "$db_dir" ] && mkdir -pv "$db_dir"

