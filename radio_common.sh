#!/bin/bash

[ -n "$radio_common_imported" ] && return
[ -f "$HOME"/.dev_local_rc ] && . "$HOME"/.dev_local_rc

export test_flag="$1"
[ "$test_flag" = "test" ] && export radio_home='./test_trash' || export radio_home="$HOME"/radio

export radio_common_imported='radio_common_imported'
export lib_name='musical_chairs_libs'
export app_name='musical_chairs_app'
export ices_configs_dir="$radio_home"/ices_configs
export pyModules_dir="$radio_home"/pyModules
export build_home="$HOME"/Documents/builds
export music_home="$HOME"/music
export radio_config_dir="$radio_home"/config
export config_file="$radio_config_dir"/config.yml
export db_dir="$radio_home"/db
export sqlite_file="$db_dir"/songs_db

# directories that should be cleaned upon changes
# suffixed with 'cl' for 'clean'
export process_dir_cl="$radio_home"/process
export start_up_dir_cl="$radio_home"/start_up

#python version info
export pyVersion=$(python3 -V)
export pyMajor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /(\d+)\.\d+/')
export pyMinor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /\d+\.(\d+)/')

export PACMAN_CONST='pacman'
export current_user=$(whoami)

not_installed() {
    echo "$1 not installed"
    exit 0
}

export pkgMgr=''
export pkgMgrChoice=''
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
    virtualenv -p python3  "$codePath"/env
    . "$codePath"/env/bin/activate
    python3 -m pip install -r "$codePath"/requirements.txt &&
    deactivate &&
    empty_dir_contents "$codePath""$packagePath""$lib_name"/ &&
    sudo cp -rv ./src/"$lib_name"/* "$codePath""$packagePath""$lib_name"/ &&
    sudo chown -R "$current_user": "$codePath""$packagePath""$lib_name"/
)

empty_dir_contents() {
    local dir_to_empty="$1"
    if [ -e "$dir_to_empty" ]; then 
        sudo rm -rf "$dir_to_empty"/*
    else
        sudo mkdir -pv "$dir_to_empty" &&
        sudo chown -R "$current_user": "$dir_to_empty"
    fi
}

[ ! -e "$radio_home" ] && mkdir -pv "$radio_home"
[ ! -e "$ices_configs_dir" ] && mkdir -pv "$ices_configs_dir"
[ ! -e "$build_home" ] && mkdir -pv "$build_home"
[ ! -e "$music_home" ] && mkdir -pv "$music_home"
[ ! -e "$pyModules_dir" ] && mkdir -pv "$pyModules_dir"
[ ! -e "$radio_config_dir" ] && mkdir -pv "$radio_config_dir"
[ ! -e "$db_dir" ] && mkdir -pv "$db_dir"

export -f aws_role
export -f s3_name
export -f link_to_music_files
export -f setup_py3_env
export -f empty_dir_contents