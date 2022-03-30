#!/bin/sh


[ -f "$HOME"/.dev_local_rc ] && . "$HOME"/.dev_local_rc

while [ ! -z "$1" ]; do
	case "$1" in
		test)
			test_flag='test'
			;;
		radio_home=*)
			radio_home=${1#radio_home=}
			;;
		web_root=*)
			web_root=${1#web_root=}
			;;
		*) ;;
	esac
	shift
done

if [ -n "$test_flag" ]; then
	radio_home='./test_trash'
	web_root='./test_trash'
fi

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
templates_dir_cl="$radio_home"/templates

#python environment names
py_env='mc_env'

case $(uname) in
	Linux*)
		export web_root=${web_root:-/srv}
		;;
	Darwin*)
		export web_root=${web_root:-/Library/WebServer}
		;;
	*) ;;
esac
app_path_cl="$web_root"/"$app_name"
app_path_client_cl="$app_path_cl"/client/

#local paths
api_src="./src/api"
client_src="./src/client"



PACMAN_CONST='pacman'
APT_CONST='apt-get'
HOMEBREW_CONST='homebrew'
current_user=$(whoami)

set_python_version_const() {
	#python version info
	mc-python -V 2>/dev/null || return "$?"
	pyVersion=$(mc-python -V)
	pyMajor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /(\d+)\.\d+/')
	pyMinor=$(echo "$pyVersion"| perl -ne 'print "$1\n" if /\d+\.(\d+)/')
}

set_pkg_mgr() {
	pkgMgr=''
	pkgMgrChoice=''
	case $(uname) in
	Linux*)
		if  which pacman >/dev/null 2>&1; then
			pkgMgrChoice="$PACMAN_CONST"
			pkgMgr='yes | sudo -p "Pass required for pacman install: " pacman -S'
		elif which apt-get >/dev/null 2>&1; then
			pkgMgrChoice="$APT_CONST"
			local msg='Pass required for apt-get install: '
			pkgMgr="yes | sudo -p '$msg' apt-get install: "
		fi
		;;
	Darwin*)
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
# subshell () auto switches in use python version back at the end of function
setup_py3_env() (
	set_python_version_const || return "$?"
	local dest_base="$1"
	local env_name=${2:-"$py_env"}
	local packagePath="$env_name/lib/python$pyMajor.$pyMinor/site-packages/"
	local dest="$dest_base"/"$packagePath""$lib_name"/
	mc-python -m virtualenv "$dest_base"/$env_name &&
	. "$dest_base"/$env_name/bin/activate &&
	# #python_env
	# use regular python command rather mc-python
	# because mc-python still points to the homebrew location
	python -m pip install -r "$radio_home"/requirements.txt &&
	setup_dir ./src/"$lib_name" "$dest" ||
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
	case $(uname) in
		Darwin*)
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
	case $(uname) in
		Darwin*)
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

setup_config_file() {
	cp ./templates/configs/config.yml "$config_file" &&
	sed -i -e "s@<searchbase>@$music_home/@" "$config_file" &&
	sed -i -e "s@<dbname>@$sqlite_file@" "$config_file" &&
	rm -f "$config_file"-e
}

setup_dir() {
	local src_dir="$1"
	local dest_dir="$2"
	empty_dir_contents "$dest_dir" &&
	sudo -p 'Pass required for copying files: ' \
		cp -rv "src_dir"/* "$dest_dir" &&
	sudo -p 'Pass required for changing owner of maintenance files: ' \
		chown -R "$current_user": "$dest_dir"
	return "$?"
}

setup_dir_with_py() {
	local src_dir="$1"
	local dest_dir="$2"
	local env_name="$3"
	empty_dir_contents "$dest_dir" &&
	sudo -p 'Pass required for copying files: ' \
		cp -rv "src_dir"/* "$dest_dir" &&
	setup_py3_env "$dest_dir" "$env_name" &&
	sudo -p 'Pass required for changing owner of maintenance files: ' \
		chown -R "$current_user": "$dest_dir"
	return "$?"
}

gen_pass() {
	local pass_len=${1:-16}
	LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c "$pass_len" 
}

append_trailing_slash_if_needed() {
	local str="${1%/}/"
	echo "$str"
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
