#!/bin/sh


[ -f "$HOME"/.profile ] && . "$HOME"/.profile
[ -f "$HOME"/.zprofile ] && . "$HOME"/.zprofile

to_abs_path() {
	local target_path="$1"
	if [ "$target_path" = '.' ]; then
		pwd
	elif [ "$target_path" = '..' ]; then
		dirname $(pwd)
	else
		echo $(cd $(dirname "$target_path"); pwd)
	fi
}


install_package() {
	local pkgName="$1"
	case $(uname) in
		Linux*)
			if which pacman >/dev/null 2>&1; then
				yes | sudo -p 'Pass required for pacman install: ' \
					pacman -S "$pkgName"
			elif which apt-get >/dev/null 2>&1; then
				echo "Try to install $pkgName"
				yes | sudo -p 'Pass required for apt-get install: ' \
					apt-get install "$pkgName" ||
				sudo dpkg --configure -a &&
				yes | sudo -p 'Pass required for apt-get install: ' \
					apt-get install "$pkgName"
			fi
			;;
		Darwin*)
			yes | brew install "$pkgName"
			;;
		*) 
			;;
	esac
}

set_python_version_const() {
	#python version info
	mc-python -V 2>/dev/null || return "$?"
	pyVersion=$(mc-python -V)
	pyMajor=$(echo "$pyVersion" | perl -ne 'print "$1\n" if /(\d+)\.\d+/')
	pyMinor=$(echo "$pyVersion" | perl -ne 'print "$1\n" if /\d+\.(\d+)/')
}

set_pkg_mgr() {
	pkgMgrChoice=''
	case $(uname) in
		Linux*)
			if  which pacman >/dev/null 2>&1; then
				pkgMgrChoice="$PACMAN_CONST"
			elif which apt-get >/dev/null 2>&1; then
				pkgMgrChoice="$APT_CONST"
			fi
			;;
		Darwin*)
			pkgMgrChoice="$HOMEBREW_CONST"
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

is_python_sufficient_version() {
	set_python_version_const &&
	[ "$pyMajor" -eq 3 ] && ["$pyMinor" -ge 9]
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
	#this is to make some of my newer than checks work
	touch "$dest_base"/$env_name && 
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
	cp ./templates/.env "$config_file" &&
	sed -i -e "s@^\(searchBase=\).*\$@\1'$music_home'@" "$config_file" &&
	sed -i -e "s@^\(dbName=\).*\$@\1'$sqlite_file'@" "$config_file" &&
	rm -f "$config_file"-e
}

setup_dir() {
	local src_dir="$1"
	local dest_dir="$2"
	empty_dir_contents "$dest_dir" &&
	sudo -p 'Pass required for copying files: ' \
		cp -rv "$src_dir"/* "$dest_dir" &&
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
		cp -rv "$src_dir"/* "$dest_dir" &&
	setup_py3_env "$dest_dir" "$env_name" &&
	sudo -p 'Pass required for changing owner of maintenance files: ' \
		chown -R "$current_user": "$dest_dir"
	return "$?"
}

gen_pass() {
	local pass_len=${1:-16}
	LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c "$pass_len" 
}

compare_dirs() (
	local src_dir="$1"
	local cpy_dir="$2"
	local exit_code=0
	if [ ! -e "$cpy_dir" ]; then
		echo "$cpy_dir/ is not in place" 
		return 1
	fi
	rm -f src_fifo cpy_fifo cmp_fifo
	mkfifo src_fifo cpy_fifo cmp_fifo

	src_res=$(find "$src_dir" | \
		sed "s@${src_dir%/}/\{0,1\}@@" | sort) 
	cpy_res=$(find "$cpy_dir" -not -path "$cpy_dir/$py_env/*" \
		-and -not -path "$cpy_dir/$py_env" | \
		sed "s@${cpy_dir%/}/\{0,1\}@@" | sort)

	get_file_list() {
		local supress="$1"
		echo "$src_res" > src_fifo &
		echo "$cpy_res" > cpy_fifo &
		[ -n "$supress" ] && comm "-$supress" src_fifo cpy_fifo ||
			comm src_fifo cpy_fifo
	}

	in_both=$(get_file_list 12)
	in_src=$(get_file_list 23)
	in_cpy=$(get_file_list 13)
	[ -n "$(echo "$in_cpy" | xargs)" ] && 
			{
				echo "There are items that only exist in $cpy_dir"
				exit_code=2
			}
	[ -n "$(echo "$in_src" | xargs)" ] && 
			{
				echo "There are items missing from the $cpy_dir"
				exit_code=3
			}
	if [ -n "$in_both" ]; then
		exit_code=4
		echo "$in_both" > cmp_fifo &
		while read file_name; do
			[ "${src_dir%/}/$file_name" -nt "${cpy_dir%/}/$file_name" ] &&
				echo "$file_name is outdated"
		done <cmp_fifo
	fi
	rm -f src_fifo cpy_fifo cmp_fifo
	return "$exit_code"
)

is_newer_than_files() {
	local candidate="$1"
	local dir_to_check="$2"
	find "$dir_to_check" -newer "$candidate"
}

literal_to_regex() {
	#this will handle cases as I need them and not exhaustively
	local str="$1"
	echo str | sed 's/\*/\\*/g'
}

get_nginx_value() {
	local key={$1:-'conf-path'}
	#break options into a list
	#then isolate the option we're interested in
	nginx -V 2>&1 | \
			sed 's/ /\n/g' | \ 
			sed -n "/--$key/p" | \ 
			sed 's/.*=\(.*\)/\1/'
}

get_nginx_conf_dir_include() {
	local nginx_conf=$(get_nginx_value)
	local guesses=$(cat<<-EOF
		include /etc/nginx/sites-enabled/*;
		include servers/*;
	EOF
	)
	echo "$guesses" | while read guess; do
		if grep -F "$guess" "$nginx_conf"; then
			echo "$guess"
			break
		fi
	done
}

update_nginx_conf() {
	local appConfFile="$1"
	sudo -p 'copy nginx config' \
		cp "$templates_src"/nginx_template.conf "$appConfFile" &&
	sed -i "s@<app_path_client_cl>@$app_path_client_cl@" "$appConfFile" &&
	sed -i "s@<full_url>@$full_url@" "$appConfFile" 
}

get_abs_path_from_nginx_include() {
	local confDirInclude="$1"
	local confDir=$(echo "$confDirInclude" | sed 's/include *//' | \
		sed 's@\*; *@@') 
	#test if already exists as absolute path
	if [ -d  "$confDir" ]; then
		echo "$confDir"
		return
	else
		prefix=$(get_nginx_value 'prefix')
		local absPath="$prefix"/"$confDir"
		if [ ! -d "$absPath" ]; then
			if [ -e "$absPath" ]; then 
				echo "$absPath is a file, not a directory" 1>&2
				return 1
			fi
			#Apparently nginx will look for includes with either an absolute path
			#or path relative to the prefix
			#some os'es are finicky about creating directories at the root lvl
			#even with sudo, so we're not going to even try
			#we'll just create missing dir in $prefix folder
			sudo -p "Add nginx conf dir" \
				mkdir -pv "$absPath"
			echo "$absPath"
		fi
	fi
}

get_nginx_conf_dir_abs_path() {
	local confDirInclude=$(get_nginx_conf_dir_include)
	get_abs_path_from_nginx_include "$confDirInclude"
}

enable_nginx_include() {
	local confDirInclude="$1"
	local confDir=$(echo "$confDirInclude" | sed 's/include *//' | \
		sed 's@\*; *@@') 
	local escaped_guess=$(literal_to_regex "$confDirInclude")
	#uncomment line if necessary
	sudo -p "Enable $confDirInclude" \
		sed -i "\@$escaped_guess@s/^[ \t]*#//" $(get_nginx_value) 
}

restart_nginx() {
	case $(uname) in
		Darwin*)
			nginx -s reload
			;;
		Linux*) 
			if systemctl is-active --quiet nginx; then
				sudo systemctl restart nginx
			else
				echo "nginx not started"
				return 1
			fi
			;;
		*) ;;
	esac
}

setup_nginx_confs() {
	local confDirInclude=$(get_nginx_conf_dir_include)
	#remove trailing path chars
	local confDir=$(get_abs_path_from_nginx_include "$confDirInclude") 
	enable_nginx_include "$confDirInclude"
	update_nginx_conf "$confDir"/"$app_name".conf
	sudo -p 'Remove default nginx config' \
		rm -f "$confDir"/default
	restart_nginx
}

while [ ! -z "$1" ]; do
	case "$1" in
		test)
			test_flag='test'
			;;
		testdb)
			test_db_flag='test_db'
			;;
		env=*)
			app_env=${1#env=}
			;;
		radio_home=*)
			radio_home=${1#radio_home=}
			;;
		web_root=*)
			web_root=${1#web_root=}
			;;
		setup_lvl=*)
			setup_lvl=${1#setup_lvl=}
			;;
		*) ;;
	esac
	shift
done

workspace_abs_path=$(to_abs_path $0)

test_root="$workspace_abs_path/test_trash"

if [ -n "$test_flag" ]; then
	radio_home="$test_root"
	web_root="$test_root"
fi

export radio_home=${radio_home:-"$HOME"/radio}

proj_name='musical_chairs'
lib_name="$proj_name"_libs
app_name="$proj_name"_app
url_base=$(echo "$proj_name" | tr -d _)
ices_configs_dir="$radio_home"/ices_configs
pyModules_dir="$radio_home"/pyModules
build_home="$HOME"/Documents/builds
music_home="$HOME"/music/radio
radio_config_dir="$radio_home"/config
config_file="$radio_config_dir"/.env
db_dir="$radio_home"/db
sqlite_file="$db_dir"/songs_db
bin_dir="$HOME"/.local/bin
utest_env_dir="$test_root"/utest

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

app_path_cl="$web_root"/api/"$app_name"
app_path_client_cl="$web_root"/client/"$app_name"

#local paths
src_path="$workspace_abs_path/src"
api_src="$src_path/api"
client_src="$src_path/client"
lib_src="$src_path/$lib_name"
templates_src="$workspace_abs_path/templates"
start_up_src="$workspace_abs_path/start_up"
maintenance_src="$workspace_abs_path/maintenance"

case "$app_env" in 
	local*)
		url_suffix='-local.fm:8080'
		;;
	*)
		url_suffix='.fm'
		;;
esac

full_url="http://$url_base""$url_suffix"


PACMAN_CONST='pacman'
APT_CONST='apt-get'
HOMEBREW_CONST='homebrew'
current_user=$(whoami)

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
