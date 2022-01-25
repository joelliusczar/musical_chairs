#!/bin/bash


[ -f "$HOME"/.dev_local_rc ] && . "$HOME"/.dev_local_rc

test_flag="$1"
[ "$test_flag" = "test" ] && radio_home='./test_trash' || radio_home="$HOME"/radio

lib_name='musical_chairs_libs'
app_name='musical_chairs_app'
ices_configs_dir="$radio_home"/ices_configs
pyModules_dir="$radio_home"/pyModules
build_home="$HOME"/Documents/builds
music_home="$HOME"/music/radio
radio_config_dir="$radio_home"/config
config_file="$radio_config_dir"/config.yml
db_dir="$radio_home"/db
sqlite_file="$db_dir"/songs_db

# directories that should be cleaned upon changes
# suffixed with 'cl' for 'clean'
maintenance_dir_cl="$radio_home"/maintenance
start_up_dir_cl="$radio_home"/start_up
templates_dir_cl="$maintenance_dir_cl"/templates

#python version info
pyVersion=$(python3 -V)
pyMajor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /(\d+)\.\d+/')
pyMinor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /\d+\.(\d+)/')

PACMAN_CONST='pacman'
APT_CONST='apt'
current_user=$(whoami)

set_pkg_mgr() {
	pkgMgr=''
	pkgMgrChoice=''
	if  pacman -V &>/dev/null; then
		pkgMgrChoice="$PACMAN_CONST"
		pkgMgr='yes | sudo pacman -S'
	elif apt version apt &>/dev/null; then
		pkgMgrChoice="$APT_CONST"
		pkgMgr='yes | sudo apt install'
	fi
}

not_installed() {
	echo "$1 not installed"
	exit 0
}

aws_role() {
	echo 'music_reader'
}


s3_name() {
	echo 'joelradio'
}


link_to_music_files() {
	if [ ! -e "$music_home"/radio/Soundtrack ]; then 
		if [ -n "$IS_RADIO_LOCAL_DEV" ]; then
			s3fs "$(s3_name)" "$music_home"/ 
		else
			s3fs "$(s3_name)" "$music_home"/ -o iam_role="$(aws_role)"
		fi
	fi
	res="$?"
	echo 'Music files should exist now'
	return "$res"
}

#set up the python environment, then copy 
setup_py3_env() (
	
	local codePath="$1"
	local packagePath="env/lib/python$pyMajor.$pyMinor/site-packages/"
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

