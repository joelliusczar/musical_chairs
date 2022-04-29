#!/bin/sh


[ -f "$HOME"/.profile ] && . "$HOME"/.profile
[ -f "$HOME"/.zprofile ] && . "$HOME"/.zprofile
[ -f "$HOME"/.zshrc ] && . "$HOME"/.zshrc

include_count=${include_count:-0}
include_count=$((include_count + 1))
export include_count

to_abs_path() (
	target_path="$1"
	if [ "$target_path" = '.' ]; then
		pwd
	elif [ "$target_path" = '..' ]; then
		dirname $(pwd)
	else
		echo $(cd $(dirname "$target_path"); pwd)
	fi
)


install_package() (
	pkgName="$1"
	echo "Try to install --$pkgName--"
	case $(uname) in
		(Linux*)
			if which pacman >/dev/null 2>&1; then
				yes | sudo -p 'Pass required for pacman install: ' \
					pacman -S "$pkgName"
			elif which apt-get >/dev/null 2>&1; then
				 sudo -p 'Pass required for apt-get install: ' \
					DEBIAN_FRONTEND=noninteractive apt-get -y install "$pkgName" 
			fi
			;;
		(Darwin*)
			yes | brew install "$pkgName"
			;;
		(*) 
			;;
	esac
)

set_python_version_const() {
	#python version info
	mc-python -V 2>/dev/null || return "$?"
	pyVersion=$(mc-python -V)
	pyMajor=$(echo "$pyVersion" | perl -ne 'print "$1\n" if /(\d+)\.\d+/')
	pyMinor=$(echo "$pyVersion" | perl -ne 'print "$1\n" if /\d+\.(\d+)/')
}

set_env_path_var() {
	if perl -e "exit 1 if index('$PATH','${app_root}/${bin_dir}') != -1"; then
		echo "Please add '${app_root}/${bin_dir}' to path"
		export PATH="$PATH":"$app_root"/"$bin_dir"
	fi
}

get_pkg_mgr() {
	case $(uname) in
		(Linux*)
			if  which pacman >/dev/null 2>&1; then
				echo "$PACMAN_CONST"
			elif which apt-get >/dev/null 2>&1; then
				echo "$APT_CONST"
			fi
			;;
		(Darwin*)
			echo "$HOMEBREW_CONST"
			;;
		(*) 
			;;
	esac
	return 1
}

get_icecast_name() (
	pkgMgrChoice="$1"
	case "$pkgMgrChoice" in
    ("$PACMAN_CONST") echo 'icecast';;
    ("$APT_CONST") echo 'icecast2';;
    (*) echo 'icecast2';;
	esac
)

aws_role() {
	echo 'music_reader'
}

s3_name() {
	echo 'joelradio'
}

link_to_music_files() {
	if [ ! -e "$app_root"/"$content_home"/Soundtrack ]; then 
		if [ -n "$IS_RADIO_LOCAL_DEV" ]; then
			s3fs "$(s3_name)" "$app_root"/"$content_home"/ 
		else
			s3fs "$(s3_name)" "$app_root"/"$content_home"/ -o iam_role="$(aws_role)"
		fi
	fi
	res="$?"
	echo 'Music files should exist now'
	return "$res"
}

is_python_sufficient_version() {
	[ "$exp_name" == 'py3.8' ] && return
	set_python_version_const &&
	[ "$pyMajor" -eq 3 ] && [ "$pyMinor" -ge 9 ]
}

#set up the python environment, then copy 
# subshell () auto switches in use python version back at the end of function
setup_py3_env() (
	set_python_version_const || return "$?"
	set_env_path_var #ensure that we can see mc-python
	dest_base="$1"
	env_name=${2:-"$py_env"}
	packagePath="$env_name/lib/python$pyMajor.$pyMinor/site-packages/"
	dest="$dest_base"/"$packagePath""$lib_name"/
	mc-python -m virtualenv "$dest_base"/$env_name &&
	. "$dest_base"/$env_name/bin/activate &&
	#this is to make some of my newer than checks work
	touch "$dest_base"/$env_name && 
	# #python_env
	# use regular python command rather mc-python
	# because mc-python still points to the homebrew location
	python -m pip install -r "$app_trunk"/requirements.txt &&
	setup_dir ./src/"$lib_name" "$dest" ||
	return "$?"
)

empty_dir_contents() (
	dir_to_empty="$1"
	echo "Emptying ${dir_to_empty}"
	if [ -e "$dir_to_empty" ]; then 
		sudo -p "Password required for removing old files: " \
			rm -rf "$dir_to_empty"/* || return "$?"
	else
		sudo -p 'Password required for creating files: ' \
			mkdir -pv "$dir_to_empty" || return "$?"
	fi 
	msg='Password required for changing owner of created files to current user: '
	sudo -p "$msg" \
		chown -R "$current_user": "$dir_to_empty" 
)

get_bin_path() (
	pkg="$1"
	case $(uname) in
		(Darwin*)
			brew info "$pkg" \
			| grep -A1 'has been installed as' \
			| awk 'END{ print $1 }'
			;;
		(*) which "$pkg" ;;
	esac
)

brew_is_installed() (
	pkg="$1"
	echo "checking for $pkg"
	case $(uname) in
		(Darwin*)
			brew info "$pkg" >/dev/null 2>&1 &&
			! brew info "$pkg" | grep 'Not installed' >/dev/null
			;;
		(*) return 0 ;;
	esac
)

#this needs to command group and not a subshell 
#else it will basically do nothing
show_err_and_exit() {
	err_code="$?"
	msg="$1"
	[ ! -z "$msg" ] && echo "$msg"
	exit "$err_code"
}

does_file_exist() (
	candidate="$1"
	if [ ! -e "$candidate" ]; then
		echo "${candidate} does not exist"
		return 1
	fi
)

#this may seem useless but we need it for test runner to read .env
setup_env_api_file() (
	envFile="$app_root"/"$env_api_file"
	cp "$templates_src"/.env_api "$envFile" &&
	does_file_exist "$envFile" &&
	perl -pi -e "s@^(searchBase=).*\$@\1'${app_root}/${content_home}'@" \
		"$envFile" &&
	does_file_exist "$envFile" &&
	perl -pi -e "s@^(dbName=).*\$@\1'${app_root}/${sqlite_file}'@" "$envFile" 
)

setup_dir() (
	src_dir="$1"
	dest_dir="$2"
	empty_dir_contents "$dest_dir" &&
	sudo -p 'Pass required for copying files: ' \
		cp -rv "$src_dir"/. "$dest_dir" &&
	sudo -p 'Pass required for changing owner of maintenance files: ' \
		chown -R "$current_user": "$dest_dir"
	return "$?"
)

setup_dir_with_py() (
	src_dir="$1"
	dest_dir="$2"
	env_name="$3"
	empty_dir_contents "$dest_dir" &&
	sudo -p 'Pass required for copying files: ' \
		cp -rv "$src_dir"/. "$dest_dir" &&
	setup_py3_env "$dest_dir" "$env_name" &&
	sudo -p 'Pass required for changing owner of maintenance files: ' \
		chown -R "$current_user": "$dest_dir"
)

gen_pass() (
	pass_len=${1:-16}
	LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c "$pass_len" 
)

compare_dirs() (
	src_dir="$1"
	cpy_dir="$2"
	exit_code=0
	if [ ! -e "$cpy_dir" ]; then
		echo "$cpy_dir/ is not in place" 
		return 1
	fi
	rm -f src_fifo cpy_fifo cmp_fifo
	mkfifo src_fifo cpy_fifo cmp_fifo

	src_res=$(find "$src_dir" | \
		sed "s@${src_dir%/}/\{0,1\}@@" | sort) 
	cpy_res=$(find "${cpy_dir}" -not -path "${cpy_dir}/${py_env}/*" \
		-and -not -path "${cpy_dir}/${py_env}" | \
		sed "s@${cpy_dir%/}/\{0,1\}@@" | sort)

	get_file_list() (
		supress="$1"
		echo "$src_res" > src_fifo &
		echo "$cpy_res" > cpy_fifo &
		[ -n "$supress" ] && comm "-${supress}" src_fifo cpy_fifo ||
			comm src_fifo cpy_fifo
	)

	in_both=$(get_file_list 12)
	in_src=$(get_file_list 23)
	in_cpy=$(get_file_list 13)
	[ -n "$(echo "${in_cpy}" | xargs)" ] && 
			{
				echo "There are items that only exist in ${cpy_dir}"
				exit_code=2
			}
	[ -n "$(echo "${in_src}" | xargs)" ] && 
			{
				echo "There are items missing from the ${cpy_dir}"
				exit_code=3
			}
	if [ -n "$in_both" ]; then
		exit_code=4
		echo "$in_both" > cmp_fifo &
		while read file_name; do
			[ "${src_dir%/}/${file_name}" -nt "${cpy_dir%/}/${file_name}" ] &&
				echo "${file_name} is outdated"
		done <cmp_fifo
	fi
	rm -f src_fifo cpy_fifo cmp_fifo
	return "$exit_code"
)

is_newer_than_files() (
	candidate="$1"
	dir_to_check="$2"
	find "$dir_to_check" -newer "$candidate"
)

literal_to_regex() (
	#this will handle cases as I need them and not exhaustively
	str="$1"
	echo "$str" | sed 's/\*/\\*/g'
)

get_nginx_value() (
	key=${1:-'conf-path'}
	#break options into a list
	#then isolate the option we're interested in
	nginx -V 2>&1 | \
		sed 's/ /\n/g' | \
		sed -n "/--${key}/p" | \
		sed 's/.*=\(.*\)/\1/'
)

get_nginx_conf_dir_include() (
	nginx_conf=$(get_nginx_value)
	guesses=$(cat<<-'EOF'
		include /etc/nginx/sites-enabled/*;
		include servers/*;
	EOF
	)
	echo "$guesses" | while read guess; do
		if grep -F "$guess" "$nginx_conf" >/dev/null; then
			echo "$guess"
			break
		fi
	done
)

update_nginx_conf() (
	appConfFile="$1"
	sudo -p 'copy nginx config' \
		cp "$templates_src"/nginx_template.conf "$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<app_client_path_cl>@${web_root}/${app_client_path_cl}@" \
		"$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<full_url>@${full_url}@" "$appConfFile" 
)

get_abs_path_from_nginx_include() (
	confDirInclude="$1"
	confDir=$(echo "$confDirInclude" | sed 's/include *//' | \
		sed 's@/\*; *@@') 
	#test if already exists as absolute path
	if [ -d  "$confDir" ]; then
		echo "$confDir"
		return
	else
		prefix=$(get_nginx_value 'prefix')
		absPath="$prefix"/"$confDir"
		if [ ! -d "$absPath" ]; then
			if [ -e "$absPath" ]; then 
				echo "{$absPath} is a file, not a directory" 1>&2
				return 1
			fi
			debug_print "Hello?"
			#Apparently nginx will look for includes with either an absolute path
			#or path relative to the prefix
			#some os'es are finicky about creating directories at the root lvl
			#even with sudo, so we're not going to even try
			#we'll just create missing dir in $prefix folder
			sudo -p "Add nginx conf dir" \
				mkdir -pv "$absPath"
		fi
		echo "$absPath"
	fi
)

get_nginx_conf_dir_abs_path() (
	confDirInclude=$(get_nginx_conf_dir_include)
	get_abs_path_from_nginx_include "$confDirInclude"
)

enable_nginx_include() (
	confDirInclude="$1"
	escaped_guess=$(literal_to_regex "$confDirInclude")
	#uncomment line if necessary in config
	sudo -p "Enable ${confDirInclude}" \
		perl -pi -e "s/^[ \t]*#// if m@$escaped_guess@" "$(get_nginx_value)"
)

restart_nginx() (
	case $(uname) in
		(Darwin*)
			nginx -s reload
			;;
		(Linux*) 
			if systemctl is-active --quiet nginx; then
				sudo systemctl restart nginx
			else
				echo "nginx not started"
				return 1
			fi
			;;
		(*) ;;
	esac
)

setup_nginx_confs() (
	confDirInclude=$(get_nginx_conf_dir_include)
	#remove trailing path chars
	confDir=$(get_abs_path_from_nginx_include "$confDirInclude") 
	enable_nginx_include "$confDirInclude"
	update_nginx_conf "$confDir"/"$app_name".conf
	sudo -p 'Remove default nginx config' \
		rm -f "$confDir"/default
	restart_nginx
)

debug_print() (
	msg="$1"
	if [ -n "$diag_flag" ]; then
		echo "$msg" >> diag_out_"$include_count"
	fi
)

get_rc_candidate() {
	case $(uname) in
		(Linux*)
			echo "$HOME"/.bashrc
			;;
		(Darwin*)
			echo "$HOME"/.zshrc
			;;
		(*) ;;
	esac
}

while [ ! -z "$1" ]; do
	case "$1" in
		#build out to test_trash rather than the normal directories
		#sets app_root and web_root without having to set them explicitly
		(test)
			export test_flag='test'
			;;
		(copyDb) #tells setup to replace sqlite3 db
			export copy_db_flag='test_db'
			;;
		#activates debug_print. Also tells deploy script to use the diag branch
		(diag) 
			export diag_flag='diag'
			echo '' > diag_out_"$include_count"
			;;
		(env=*) #affects which url to use
			app_env=${1#env=}
			;;
		(app_root=*)
			app_root=${1#app_root=}
			;;
		(web_root=*)
			web_root=${1#web_root=}
			;;
		(setup_lvl=*) #affects which setup scripst to run
			export setup_lvl=${1#setup_lvl=}
			;;
		#when I want to conditionally run with some experimental code
		(experiment=*) 
			export exp_name=${1#experiment=}
			;;
		(*) ;;
	esac
	shift
done

workspace_abs_path=$(to_abs_path $0)

app_root=${app_root:-"$HOME"}
test_root="$workspace_abs_path/test_trash"


if [ -n "$test_flag" ]; then
	app_root="$test_root"
	web_root="$test_root"
fi

proj_name='musical_chairs'
db_name='songs_db'
app_trunk="$app_root/$proj_name"
export app_root="$app_root"
export web_root="$web_root"
export app_trunk="$app_trunk"

lib_name="$proj_name"_libs
app_name="$proj_name"_app
url_base=$(echo "$proj_name" | tr -d _)
ices_configs_dir="$proj_name"/ices_configs
pyModules_dir="$proj_name"/pyModules
build_dir='Documents/builds'
content_home='music/radio'
config_dir="$proj_name"/config
env_api_file="$config_dir"/.env
db_dir="$proj_name"/db
sqlite_file="$db_dir"/"$db_name"
bin_dir='.local/bin'
utest_env_dir="$test_root"/utest

# directories that should be cleaned upon changes
# suffixed with 'cl' for 'clean'
maintenance_dir_cl="$proj_name"/maintenance
start_up_dir_cl="$proj_name"/start_up
templates_dir_cl="$proj_name"/templates

#python environment names
py_env='mc_env'

case $(uname) in
	(Linux*)
		export web_root=${web_root:-/srv}
		;;
	(Darwin*)
		export web_root=${web_root:-/Library/WebServer}
		;;
	(*) ;;
esac

app_api_path_cl=api/"$app_name"
app_client_path_cl=client/"$app_name"

#local paths
src_path="$workspace_abs_path/src"
api_src="$src_path/api"
client_src="$src_path/client"
lib_src="$src_path/$lib_name"
templates_src="$workspace_abs_path/templates"
start_up_src="$workspace_abs_path/start_up"
maintenance_src="$workspace_abs_path/maintenance"
reference_src="$workspace_abs_path/reference"
reference_src_db="$reference_src/$db_name"

case "$app_env" in 
	(local*)
		url_suffix='-local.radio,fm:8080'
		;;
	(*)
		url_suffix='.radio.fm'
		;;
esac

full_url="http://$url_base""$url_suffix"


PACMAN_CONST='pacman'
APT_CONST='apt-get'
HOMEBREW_CONST='homebrew'
current_user=$(whoami)

[ -e "$app_trunk" ] || 
mkdir -pv "$app_trunk"
[ -e "$app_root"/"$ices_configs_dir" ] || 
mkdir -pv "$app_root"/"$ices_configs_dir"
[ -e "$app_root"/"$build_dir" ] || 
mkdir -pv "$app_root"/"$build_dir"
[ -e "$app_root"/"$content_home" ] || 
mkdir -pv "$app_root"/"$content_home"
[ -e "$app_root"/"$pyModules_dir" ] || 
mkdir -pv "$app_root"/"$pyModules_dir"
[ -e "$app_root"/"$config_dir" ] || 
mkdir -pv "$app_root"/"$config_dir"
[ -e "$app_root"/"$db_dir" ] || 
mkdir -pv "$app_root"/"$db_dir"
msg='Pass required for creating web server directory: '
[ -e "$web_root"/"$app_api_path_cl" ] ||
{ 
	sudo -p "$msg" mkdir -pv "$web_root"/"$app_api_path_cl" ||
	show_err_and_exit "Could not create ${web_root}/${app_api_path_cl}" 
}
