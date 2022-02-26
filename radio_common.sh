#!/bin/sh


[ -f "$HOME"/.dev_local_rc ] && . "$HOME"/.dev_local_rc

while [ ! -z "$1" ]; do
	case $1 in
		test)
			test_flag='test'
			;;
		radio_home=*)
			radio_home=${1#radio_home=}
			;;
		api_setup=*)
			api_setup=${1#api_setup=}
			;;
		bar=*)
			bar=${1#bar=}
			;;
		*) ;;
	esac
	shift
done

export radio_home=${radio_home:-"$HOME"/radio}

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
bin_dir="$HOME"/.local/bin

# directories that should be cleaned upon changes
# suffixed with 'cl' for 'clean'
maintenance_dir_cl="$radio_home"/maintenance
start_up_dir_cl="$radio_home"/start_up
templates_dir_cl="$maintenance_dir_cl"/templates
case "$OSTYPE" in
	linux-gnu*)
		app_path_cl=/srv/"$app_name"
		;;
	darwin*)
		app_path_cl=/Library/WebServer/"$app_name"
		;;
	*) ;;
esac
app_path_client_cl="$app_path_cl"/client/

http_config="$app_path_cl"/web_config.yml

#local paths
api_src="./src/api"
client_src="./src/client"



PACMAN_CONST='pacman'
APT_CONST='apt-get'
HOMEBREW_CONST='homebrew'
current_user=$(whoami)

set_python_version_const() {
	#python version info
	pyVersion=$(mc-python -V)
	pyMajor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /(\d+)\.\d+/')
	pyMinor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /\d+\.(\d+)/')
}

set_pkg_mgr() {
	pkgMgr=''
	pkgMgrChoice=''
	case "$OSTYPE" in
	linux-gnu*)
		if  which pacman >/dev/null 2>&1; then
			pkgMgrChoice="$PACMAN_CONST"
			pkgMgr='yes | sudo -p "Pass required for pacman install: " pacman -S'
		elif which apt-get >/dev/null 2>&1; then
			pkgMgrChoice="$APT_CONST"
			local msg='Pass required for apt-get install: '
			pkgMgr="yes | sudo -p '$msg' apt-get install: "
		fi
		;;
	darwin*)
		pkgMgrChoice="$HOMEBREW_CONST"
		pkgMgr='yes | brew install'
		;;
	*) 
		;;
	esac
}

set_icecast_name() {
	case "$pkgMgrChoice" in
    "$PACMAN_CONST") icecast_='icecast';;
    "$APT_CONST") icecast_='icecast2';;
    *) icecast_='icecast2';;
	esac
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
	if [ ! -e "$music_home"/Soundtrack ]; then 
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
	local dest="$codePath"/"$packagePath""$lib_name"/
	mc-python -m virtualenv "$codePath"/env &&
	. "$codePath"/env/bin/activate &&
	mc-python -m pip install -r "$radio_home"/requirements.txt &&
	deactivate &&
	empty_dir_contents "$dest" &&
	sudo -p 'Password required to copy lib files: ' \
		cp -rv ./src/"$lib_name"/* "$dest" &&
	sudo -p 'Password required to change owner of copied files: ' \
		chown -R "$current_user": "$dest" ||
	return "$?"
)

empty_dir_contents() {
	local dir_to_empty="$1"
	if [ -e "$dir_to_empty" ]; then 
		sudo -p "Password required for removing old files: " \
			rm -rf "$dir_to_empty"/* ||
		return "$?"
	else
		sudo -p 'Password required for creating files: ' \
			mkdir -pv "$dir_to_empty"  ||
		return "$?"
	fi
	msg='Password required for changing owner of created files to current user: '
	sudo -p "$msg" \
		chown -R "$current_user": "$dir_to_empty" ||
	return "$?"
}

get_bin_path() {
	local pkg="$1"
	case "$OSTYPE" in
		darwin*)
			brew info "$pkg" \
			| grep -A1 'has been installed as' \
			| awk 'END{ print $1 }'
			;;
		*) which "$pkg" ;;
	esac
}

brew_is_installed() {
	local pkg="$1"
	echo "checking for $pkg"
	case "$OSTYPE" in
		darwin*)
			brew info "$pkg" >/dev/null 2>&1 &&
			! brew info "$pkg" | grep 'Not installed' >/dev/null
			;;
		*) return 0 ;;
	esac
}

show_err_and_exit() {
	local err_code="$?"
	local msg="$1"
	[ ! -z "$msg" ] && echo "$msg"
	exit "$err_code"
}


[ ! -e "$radio_home" ] && mkdir -pv "$radio_home"
[ ! -e "$ices_configs_dir" ] && mkdir -pv "$ices_configs_dir"
[ ! -e "$build_home" ] && mkdir -pv "$build_home"
[ ! -e "$music_home" ] && mkdir -pv "$music_home"
[ ! -e "$pyModules_dir" ] && mkdir -pv "$pyModules_dir"
[ ! -e "$radio_config_dir" ] && mkdir -pv "$radio_config_dir"
[ ! -e "$db_dir" ] && mkdir -pv "$db_dir"
msg='Pass required for creating web server directory: '
[ ! -e "$app_path_cl" ] && 
{ 
	sudo -p "$msg" mkdir -pv "$app_path_cl" ||
	show_err_and_exit "Could not create $app_path_cl" 
}
