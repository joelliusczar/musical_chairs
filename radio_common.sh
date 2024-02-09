#!/bin/sh

[ -f "$HOME"/.profile ] && . "$HOME"/.profile >/dev/null
[ -f "$HOME"/.zprofile ] && . "$HOME"/.zprofile
[ -f "$HOME"/.zshrc ] && . "$HOME"/.zshrc

__INCLUDE_COUNT__=${__INCLUDE_COUNT__:-0}
__INCLUDE_COUNT__=$((__INCLUDE_COUNT__ + 1))
export __INCLUDE_COUNT__

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

__is_current_dir_repo__() {
	dir="$1"
	[ -f "$dir"/radio_common.sh ] &&
	[ -f "$dir"/README.md ] &&
	[ -f "$dir"/deploy_to_server.sh ] &&
	[ -d "$dir"/.vscode ] &&
	[ -d "$dir"/compiled_dependencies ] &&
	[ -d "$dir"/src ] &&
	[ -d "$dir"/src/musical_chairs_libs ]
}

track_exit_code() {
	exitCode="$?"
	if [ -z "$fnExitCode" ]; then
		echo 'fnExitCode not set'
		exit 1
	fi
	((exit "$fnExitCode") || (exit "$exitCode"))
	fnExitCode="$?"
}

deployment_local_env_check() (
	echo 'checking environment vars before deployment'
	#possibly problems if missing
	[ -z $(__get_ices_branch__) ] &&
	echo 'environmental var __ICES_BRANCH__ not set'
	[ -z "$MC_LOCAL_REPO_PATH" ] &&
	echo 'environmental var MC_LOCAL_REPO_PATH not set'
	[ -z $(__get_db_setup_key__) ] &&
	echo 'deployment var __DB_SETUP_PASS__ not set in keys'
	[ -z $(__get_db_owner_key__) ] &&
	echo 'deployment var MC_DB_PASS_OWNER not set in keys'

	#definitely problems if missing
	[ -z "$MC_REPO_URL" ] &&
	echo 'environmental var MC_REPO_URL not set'
	fnExitCode="$?"
	track_exit_code

	#values for ssh'ing to server
	[ -z $(__get_id_file__) ] &&
	echo 'deployment var MC_SERVER_KEY_FILE not set in keys'
	track_exit_code
	[ -z $(__get_address__) ] &&
	echo 'deployment var MC_SERVER_SSH_ADDRESS not set in keys'
	track_exit_code

	#porkbun
	[ -z $(__get_pb_api_key__) ] &&
	echo 'deployment var PB_API_KEY not set in keys'
	track_exit_code
	[ -z $(__get_pb_secret__) ] &&
	echo 'deployment var PB_SECRET not set in keys'
	track_exit_code

	#for encrypting app token
	[ -z $(__get_mc_auth_key__) ] &&
	echo 'deployment var MC_AUTH_SECRET_KEY not set in keys'
	track_exit_code

	#s3
	[ -z $(__get_s3_api_key__) ] &&
	echo 'deployment var AWS_ACCESS_KEY_ID not set in keys'
	track_exit_code
	[ -z $(__get_s3_secret__) ] &&
	echo 'deployment var AWS_SECRET_ACCESS_KEY not set in keys'
	track_exit_code
	[ -z $(__get_s3_bucket_name__) ] &&
	echo 'deployment var S3_BUCKET_NAME not set in keys'
	track_exit_code
	[ -z $(__get_s3_region_name__) ] &&
	echo 'deployment var S3_REGION_NAME not set in keys'
	track_exit_code

	#db
	[ -z $(__get_api_db_user_key__) ] &&
	echo 'deployment var MC_DB_PASS_API not set in keys'
	track_exit_code
	[ -z $(__get_radio_db_user_key__) ] &&
	echo 'deployment var MC_DB_PASS_RADIO not set in keys'
	track_exit_code
	return "$fnExitCode"
)


deployment_server_env_check() (
	echo 'checking environment vars on server'
	#possibly problems if missing
	[ -z "$__ICES_BRANCH__" ] &&
	echo 'environmental var __ICES_BRANCH__ not set'
	[ -z "$MC_LOCAL_REPO_PATH" ] &&
	echo 'environmental var MC_LOCAL_REPO_PATH not set'
	[ -z "$__DB_SETUP_PASS__" ] &&
	echo 'environmental var __DB_SETUP_PASS__ not set in keys'
	[ -z "$MC_DB_PASS_OWNER" ] &&
	echo 'environmental var MC_DB_PASS_OWNER not set in keys'


	#definitely problems if missing
	[ -z "$MC_REPO_URL" ] &&
	echo 'environmental var MC_REPO_URL not set'
	fnExitCode="$?"
	track_exit_code

	#porkbun
	[ -z "$PB_API_KEY" ] &&
	echo 'environmental var PB_API_KEY not set'
	track_exit_code
	[ -z "$PB_SECRET" ] &&
	echo 'environmental var PB_SECRET not set'
	track_exit_code

	#for encrypting app token
	[ -z "$MC_AUTH_SECRET_KEY" ] &&
	echo 'environmental var MC_AUTH_SECRET_KEY not set'
	track_exit_code

	#s3
	[ -z "$AWS_ACCESS_KEY_ID" ] &&
	echo 'environmental var AWS_ACCESS_KEY_ID not set'
	track_exit_code
	[ -z "$AWS_SECRET_ACCESS_KEY" ] &&
	echo 'environmental var AWS_SECRET_ACCESS_KEY not set'
	track_exit_code
	[ -z "$S3_ACCESS_KEY_ID" ] &&
	echo 'environmental var S3_ACCESS_KEY_ID not set'
	track_exit_code
	[ -z "$S3_SECRET_ACCESS_KEY" ] &&
	echo 'environmental var S3_SECRET_ACCESS_KEY not set'
	track_exit_code
	[ -z "$S3_BUCKET_NAME" ] &&
	echo 'environmental var S3_BUCKET_NAME not set'
	track_exit_code
	[ -z "$S3_REGION_NAME" ] &&
	echo 'environmental var S3_REGION_NAME not set'
	track_exit_code

	#db
	[ -z "$MC_DB_PASS_API" ] &&
	echo 'environmental var MC_DB_PASS_API not set'
	track_exit_code
	[ -z "$MC_DB_PASS_RADIO" ] &&
	echo 'environmental var MC_DB_PASS_RADIO not set'
	track_exit_code
	return "$fnExitCode"
)



get_repo_path() (
	if [ -n "$MC_LOCAL_REPO_PATH" ]; then
		echo "$MC_LOCAL_REPO_PATH"
		return
	elif __is_current_dir_repo__ "$PWD"; then
		echo "$PWD"
		return
	else
		for guess in \
			$(find "$HOME" -maxdepth 5 -type d \
				-path "$MC_BUILD_DIR"/"$MC_PROJ_NAME"
				); 
		do
			if __is_current_dir_repo__ "$guess"; then
				echo "$guess" 
				return
			fi
		done
	fi
	#done't try to change from home
	#fallback
	echo "$HOME"/"$MC_BUILD_DIR"/"$MC_PROJ_NAME"
)

install_package() (
	pkgName="$1"
	echo "Try to install --${pkgName}--"
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

output_env_vars() (
	export AWS_ACCESS_KEY_ID=$(gen_pass)
	export AWS_SECRET_ACCESS_KEY=$(gen_pass)
	printenv > "$(__get_app_root__)"/used_env_vars
)

set_python_version_const() {
	#python version info
	if mc-python -V >/dev/null 2>&1; then
		pyVersion=$(mc-python -V)
	elif python3 -V >/dev/null 2>&1; then
		pyVersion=$(python3 -V)
	elif python -V >/dev/null 2>&1; then
		pyVersion=$(python -V)
	else
		return 1
	fi
	pyMajor=$(echo "$pyVersion" | perl -ne 'print "$1\n" if /(\d+)\.\d+/')
	pyMinor=$(echo "$pyVersion" | perl -ne 'print "$1\n" if /\d+\.(\d+)/')
}

set_ices_version_const() {
	if ! mc-ices -V >/dev/null 2>&1; then
		return 1
	fi
	icesVersion=$(mc-ices -V | grep ^ices)
	icesMajor=$(echo "$icesVersion" \
		| perl -ne 'print "$1\n" if /(\d+)\.(\d+)\.?(\d*)/')
	icesMinor=$(echo "$icesVersion" \
		| perl -ne 'print "$2\n" if /(\d+)\.(\d+)\.?(\d*)/')
	icesPatch=$(echo "$icesVersion" \
		| perl -ne 'print "$3\n" if /(\d+)\.(\d+)\.?(\d*)/')
}

set_env_vars() {
	process_global_vars "$@" &&
	__set_env_path_var__
}

__set_env_path_var__() {
	if perl -e "exit 1 if index('$PATH','$(__get_app_root__)/${MC_BIN_DIR}') != -1";
	then
		echo "Please add '$(__get_app_root__)/${MC_BIN_DIR}' to path"
		export PATH="$PATH":"$(__get_app_root__)"/"$MC_BIN_DIR"
	fi
}


print_py_env_var_guesses() (
	set_env_vars "$@" &&
	echo "MC_CONTENT_HOME=$MC_CONTENT_HOME"
	echo "MC_TEMPLATES_DIR_CL=$MC_TEMPLATES_DIR_CL"
	echo "MC_SQL_SCRIPTS_DIR_CL"="$MC_SQL_SCRIPTS_DIR_CL"
	echo "MC_ICES_CONFIGS_DIR=$MC_ICES_CONFIGS_DIR"
	echo "MC_PY_MODULE_DIR=$MC_PY_MODULE_DIR"
)

get_pkg_mgr() {
	define_consts >&2
	case $(uname) in
		(Linux*)
			if  which pacman >/dev/null 2>&1; then
				echo "$MC_PACMAN_CONST"
				return 0
			elif which apt-get >/dev/null 2>&1; then
				echo "$MC_APT_CONST"
				return 0
			fi
			;;
		(Darwin*)
			echo "$MC_HOMEBREW_CONST"
			return 0
			;;
		(*)
			;;
	esac
	return 1
}

get_icecast_name() (
	pkgMgrChoice="$1"
	case "$pkgMgrChoice" in
    ("$MC_PACMAN_CONST") echo 'icecast';;
    ("$MC_APT_CONST") echo 'icecast2';;
    (*) echo 'icecast2';;
	esac
)

__get_ices_branch__() (
	if [ -n "$__ICES_BRANCH__" ]; then
		echo "$__ICES_BRANCH__"
		return
	fi
)

__get_pb_api_key__() (
	if [ -n "$PB_API_KEY" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$PB_API_KEY"
		return
	fi
	perl -ne 'print "$1\n" if /PB_API_KEY=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
)

__get_pb_secret__() (
	if [ -n "$PB_SECRET" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$PB_SECRET"
		return
	fi
	perl -ne 'print "$1\n" if /PB_SECRET=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
)

__get_s3_api_key__() (
	if [ -n "$AWS_ACCESS_KEY_ID" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$AWS_ACCESS_KEY_ID"
		return
	fi
	perl -ne 'print "$1\n" if /AWS_ACCESS_KEY_ID=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
)

__get_s3_secret__() (
	if [ -n "$AWS_SECRET_ACCESS_KEY" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$AWS_SECRET_ACCESS_KEY"
		return
	fi
	perl -ne 'print "$1\n" if /AWS_SECRET_ACCESS_KEY=([\w\/]+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
)

__get_s3_bucket_name__() (
	if [ -n "$S3_BUCKET_NAME" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$S3_BUCKET_NAME"
		return
	fi
	perl -ne 'print "$1\n" if /S3_BUCKET_NAME=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
)

__get_s3_region_name__() (
	if [ -n "$S3_REGION_NAME" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$S3_REGION_NAME"
		return
	fi
	perl -ne 'print "$1\n" if /S3_REGION_NAME=([\w\-]+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
)

__get_mc_auth_key__() (
	if [ -n "$MC_AUTH_SECRET_KEY" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$MC_AUTH_SECRET_KEY"
		return
	fi
	perl -ne 'print "$1\n" if /MC_AUTH_SECRET_KEY=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
)

__get_address__() (
	if [ -n "$MC_SERVER_SSH_ADDRESS" ]; then
		echo "$MC_SERVER_SSH_ADDRESS"
		return
	fi
	keyFile="$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
	perl -ne 'print "$1\n" if /MC_SERVER_SSH_ADDRESS=root@([\w:]+)/' "$keyFile"
)

__get_id_file__() (
	if [ -n "$MC_SERVER_KEY_FILE" ]; then
		echo "$MC_SERVER_KEY_FILE"
		return
	fi
	keyFile="$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
	perl -ne 'print "$1\n" if /MC_SERVER_KEY_FILE=(.+)/' "$keyFile"
)

__get_db_setup_key__() (
	if [ -n "$__DB_SETUP_PASS__" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$__DB_SETUP_PASS__"
		return
	fi
	perl -ne 'print "$1\n" if /__DB_SETUP_PASS__=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
)

__get_db_owner_key__() (
	if [ -n "$MC_DB_PASS_OWNER" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$MC_DB_PASS_OWNER"
		return
	fi
	perl -ne 'print "$1\n" if /MC_DB_PASS_OWNER=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
)

__get_api_db_user_key__() (
	if [ -n "$MC_DB_PASS_API" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$MC_DB_PASS_API"
		return
	fi
	perl -ne 'print "$1\n" if /MC_DB_PASS_API=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
)

__get_radio_db_user_key__() (
	if [ -n "$MC_DB_PASS_RADIO" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$MC_DB_PASS_RADIO"
		return
	fi
	perl -ne 'print "$1\n" if /MC_DB_PASS_RADIO=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
)

get_localhost_key_dir() (
	case $(uname) in
		(Darwin*)
			echo "$HOME"/.ssh
			;;
		(Linux*)
			echo "$HOME"/.ssh
			;;
		(*) ;;
	esac
)

__get_remote_private_key__() (
	echo "/etc/ssl/private/${MC_PROJ_NAME}.private.key.pem"
)

__get_remote_public_key__() (
	echo "/etc/ssl/certs/${MC_PROJ_NAME}.public.key.pem"
)

__get_remote_intermediate_key__() (
	echo "/etc/ssl/certs/${MC_PROJ_NAME}.intermediate.key.pem"
)

get_ssl_vars() (
	process_global_vars "$@" >&2 &&
	sendJson=$(cat <<-END
	{
		"secretapikey": "$(__get_pb_secret__)",
		"apikey": "$(__get_pb_api_key__)"
	}
	END
	) &&
	curl -s --header "Content-Type: application/json" \
	--request POST \
	--data "$sendJson" \
	https://porkbun.com/api/json/v3/ssl/retrieve/$(__get_domain_name__)

)

stdin_json_extract_value() (
	jsonKey="$1"
	python3 -c \
	"import sys, json; print(json.load(sys.stdin, strict=False)['$jsonKey'])"
)

stdin_json_top_level_keys() (
	python3 -c \
	"import sys, json; print(json.load(sys.stdin, strict=False).keys())"
)

#other keys: 'intermediatecertificate', 'certificatechain'
get_ssl_private() (
	process_global_vars "$@" >&2 &&
	get_ssl_vars | stdin_json_extract_value 'privatekey'
)

get_ssl_public() (
	process_global_vars "$@" >&2 &&
	get_ssl_vars | stdin_json_extract_value 'publickey'
)

aws_role() {
	echo 'music_reader'
}

s3_name() {
	echo 'joelradio'
}

kill_s3fs() {
	process_global_vars "$@" &&
	kill -9 $(ps -e | grep s3fs | awk '{ print $1 }')
	fusermount -u "$(__get_app_root__)"/"$MC_CONTENT_HOME"
}

link_to_music_files() {
	echo 'linking music files'
	process_global_vars "$@" &&
	if [ -z  "$(ls -A "$(__get_app_root__)"/"$MC_CONTENT_HOME")" ]; then
		if [ -e "$HOME"/.passwd-s3fs ]; then
			s3fs "$(s3_name)" "$(__get_app_root__)"/"$MC_CONTENT_HOME"/ \
				-o connect_timeout=10 -o retries=2 -o dbglevel=info -o curldbg
			[ -e "$(__get_app_root__)"/"$MC_CONTENT_HOME"/Soundtrack ]
		else
			return 1
		fi
	fi &&
	echo 'music files should exist now'
}

#geared for having a bunch of values piped to it
input_match() (
	matchFor="$1"
	while read nextValue; do
		[ "$nextValue" = "$matchFor" ] && echo 't'
	done
)

enable_wordsplitting() {
	if [ -n "$ZSH_VERSION" ]; then
		setopt shwordsplit
	fi
}

disable_wordsplitting() {
	if [ -n "$ZSH_VERSION" ]; then
		unsetopt shwordsplit
	fi
}

str_contains() (
	haystackStr="$1"
	needleStr="$2"
	case "$haystackStr" in
		*"$needleStr"*)
			return 0
	esac
	return 1
)

#the array needs to be passed in unquoted.
#example
# array_contains "$findMe" $arrayOfSpaceSeparatedWords
array_contains() (
	searchValue="$1"
	shift
	while [ ! -z "$1" ]; do
		case $1 in
			"$searchValue")
				return 0
				;;
			*)
			;;
		esac
		shift
	done
	return 1
)

is_python_version_good() {
	[ "$__EXPERIMENT_NAME__" = 'py3.8' ] && return 0
	set_python_version_const &&
	[ "$pyMajor" -eq 3 ] && [ "$pyMinor" -ge 9 ]
}

is_ices_version_good() {
	set_ices_version_const &&
	[ "$icesMajor" -ge 0 ] && [ "$icesMinor" -ge 6 ] && [ "$icesPatch" -ge 1 ]
}

is_dir_empty() (
	target_dir="$1"
	lsRes=$(ls -A $target_dir)
	[ ! -d "$target_dir" ] || [ -z "$lsRes" ]
)

get_libs_dest_dir() (
	__set_env_path_var__ >&2 #ensure that we can see mc-python
	set_python_version_const || return "$?"
	env_root="$1"
	packagePath="${MC_PY_ENV}/lib/python${pyMajor}.${pyMinor}/site-packages/"
	echo "$env_root"/"$packagePath"
)


__replace_lib_files__() {
	regen_file_reference_file &&
	copy_dir "$MC_LIB_SRC" \
		"$(get_libs_dest_dir "$(__get_app_root__)"/"$MC_APP_TRUNK")""$MC_LIB_NAME"
}

replace_lib_files() (
	process_global_vars "$@" &&
	__replace_lib_files__
)

# set up the python environment, then copy
# subshell () auto switches in use python version back at the end of function
create_py_env_in_dir() (
	echo "setting up py libs"
	__set_env_path_var__ #ensure that we can see mc-python
	link_app_python_if_not_linked
	set_python_version_const || return "$?"
	env_root=${1:-"$(__get_app_root__)"/"$MC_APP_TRUNK"}
	pyEnvDir="$env_root"/"$MC_PY_ENV"
	error_check_path "$pyEnvDir" &&
	mc-python -m virtualenv "$pyEnvDir" &&
	. "$pyEnvDir"/bin/activate &&
	#this is to make some of my newer than checks work
	touch "$pyEnvDir" &&
	# #python_env
	# use regular python command rather mc-python
	# because mc-python still points to the homebrew location
	python -m pip install -r "$(__get_app_root__)"/"$MC_APP_TRUNK"/requirements.txt &&
	echo "done setting up py libs"
)

create_py_env_in_app_trunk() (
	process_global_vars "$@" &&
	sync_requirement_list &&
	create_py_env_in_dir &&
	__replace_lib_files__
)

__install_py_env__() {
	sync_requirement_list &&
	create_py_env_in_app_trunk
}

install_py_env() {
	unset_globals
	process_global_vars "$@" &&
	__install_py_env__ &&
	echo "done installing py env"
}

__install_py_env_if_needed__() {
	if [ ! -e "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate ]; then
		__install_py_env__
	else
		echo "replacing musical_chair_lib files"
		__replace_lib_files__ >/dev/null #only replace my code
	fi
}

activate_mc_env() {
	if [ -n "$VIRTUAL_ENV" ]; then
		deactivate 2>&1 1>/dev/null
	fi
	set_env_vars "$@" &&
	__install_py_env_if_needed__ &&
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate
}

start_python() (
	activate_mc_env &&
	python
)

copy_lib_to_test() (
	process_global_vars "$@" &&
	copy_dir "$MC_LIB_SRC" \
		"$(get_libs_dest_dir "$MC_UTEST_ENV_DIR")"/"$MC_LIB_NAME"
)

error_check_path() (
	target_dir="$1"
	if echo "$target_dir" | grep '\/\/'; then
		echo "segments seem to be missing in '${target_dir}'"
		return 1
	elif [ "$target_dir" = '/' ];then
		echo "segments seem to be missing in '${target_dir}'"
		return 1
	fi
)

error_check_all_paths() (
	while [ ! -z "$1" ]; do
		error_check_path "$1" || return "$?"
		shift
	done
)

sudo_rm_contents() (
	dirEmptira="$1"
	if [ -w "$dirEmptira" ]; then
		rm -rf "$dirEmptira"/*
	else
		sudo -p "Password required to remove files from ${dirEmptira}: " \
			rm -rf "$dirEmptira"/*
	fi
)

rm_contents_if_exist() (
	dirEmptira="$1"
	if ! is_dir_empty "$dirEmptira"; then
		sudo_rm_contents "$dirEmptira"
	fi
)

sudo_rm_dir() (
	dirEmptira="$1"
	if [ -w "$dirEmptira" ]; then
		rm -rf "$dirEmptira"
	else
		sudo -p "Password required to remove ${dirEmptira}: " \
			rm -rf "$dirEmptira"
	fi
)

sudo_cp_contents() (
	fromDir="$1"
	toDir="$2"
	if [ -r "$fromDir" ] && [ -w "$toDir" ]; then
		cp -rv "$fromDir"/. "$toDir"
	else
		sudo -p 'Pass required to copy files: ' \
			cp -rv "$fromDir"/. "$toDir"
	fi
)

sudo_mkdir() (
	dirMakera="$1"
	mkdir -pv "$dirMakera" ||
	sudo -p "Password required to create ${dirMakera}: " \
		mkdir -pv "$dirMakera"
)


unroot_dir() (
	dirUnrootura="$1"
	if [ ! -w "$dirUnrootura" ]; then
		prompt='Password required to change owner of'
		prompt="${prompt} ${dirUnrootura} to current user: "
		sudo -p "$prompt" \
			chown -R "$MC_CURRENT_USER": "$dirUnrootura"
	fi
)

empty_dir_contents() (
	dirEmptira="$1"
	echo "emptying '${dirEmptira}'"
	error_check_path "$dirEmptira" &&
	if [ -e "$dirEmptira" ]; then
		rm_contents_if_exist || return "$?"
	else
		sudo_mkdir "$dirEmptira" || return "$?"
	fi &&
	unroot_dir "$dirEmptira" &&
	echo "done emptying '${dirEmptira}'"
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

link_app_python_if_not_linked() {
	if ! mc-python -V 2>/dev/null; then
		if [ ! -e "$(__get_app_root__)"/"$MC_BIN_DIR" ]; then
			sudo_mkdir "$(__get_app_root__)"/"$MC_BIN_DIR" || return "$?"
		fi
		case $(uname) in
			(Darwin*)
				ln -sf $(get_bin_path python@3.9) \
					"$(__get_app_root__)"/"$MC_BIN_DIR"/mc-python
				;;
			(*)
				ln -sf $(get_bin_path python3) \
					"$(__get_app_root__)"/"$MC_BIN_DIR"/mc-python
				;;
		esac
	fi
	echo "done linking"
}

brew_is_installed() (
	pkg="$1"
	echo "checking about $pkg"
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
	errCode="$?"
	msg="$1"
	[ ! -z "$msg" ] && echo "$msg"
	exit "$errCode"
}

#needed this method because perl will still
#exit 0 even if a file doesn't exist
does_file_exist() (
	candidate="$1"
	if [ ! -e "$candidate" ]; then
		echo "${candidate} does not exist"
		return 1
	fi
)

kill_process_using_port() (
	portNum="$1"
	echo "attempting to end process using port number: ${portNum}"
	if ss -V >/dev/null 2>&1; then
		procId=$(ss -lpn "sport = :${portNum}" \
		| perl -ne 'print "$1\n" if /pid=(\d+)/')
		if [ -n "$procId" ]; then
			kill -15 "$procId"
		fi
	elif lsof -v >/dev/null 2>&1; then
		procId=$(sudo lsof -i :${portNum} | awk '{ print $2 }' | tail -n 1)
		if [ -n "$procId" ]; then
			kill -15 "$procId"
		fi
	else
		echo "Script not wired up to be able to kill process at port: ${portNum}"
	fi
	echo "Hopefully process using is done ${portNum}"
)

#test runner needs to read .env
setup_env_api_file() (
	echo 'setting up .env file'
	envFile="$(__get_app_root__)"/"$MC_CONFIG_DIR"/.env
	error_check_all_paths "$MC_TEMPLATES_SRC"/.env_api "$envFile" &&
	pkgMgrChoice=$(get_pkg_mgr) &&
	cp "$MC_TEMPLATES_SRC"/.env_api "$envFile" &&
	does_file_exist "$envFile" &&
	perl -pi -e \
		"s@^(MC_CONTENT_HOME=).*\$@\1'${MC_CONTENT_HOME}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_SQLITE_FILEPATH=).*\$@\1'${MC_SQLITE_FILEPATH}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_TEMPLATES_DIR_CL=).*\$@\1'${MC_TEMPLATES_DIR_CL}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_SQL_SCRIPTS_DIR_CL=).*\$@\1'${MC_SQL_SCRIPTS_DIR_CL}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_ICES_CONFIGS_DIR=).*\$@\1'${MC_ICES_CONFIGS_DIR}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_PY_MODULE_DIR=).*\$@\1'${MC_PY_MODULE_DIR}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(__DB_SETUP_PASS__=).*\$@\1'${__DB_SETUP_PASS__}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_DB_PASS_OWNER=).*\$@\1'${MC_DB_PASS_OWNER}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_DB_PASS_API=).*\$@\1'${MC_DB_PASS_API}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_DB_PASS_RADIO=).*\$@\1'${MC_DB_PASS_RADIO}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_TEST_ROOT=).*\$@\1'${MC_TEST_ROOT}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_RADIO_LOG_DIR_CL=).*\$@\1'${MC_RADIO_LOG_DIR_CL}'@" \
		"$envFile" &&
	echo 'done setting up .env file'
)

copy_dir() (
	fromDir="$1"
	toDir="$2"
	echo "copying from ${fromDir} to ${toDir}"
	error_check_all_paths "$fromDir"/. "$toDir" &&
	empty_dir_contents "$toDir" &&
	sudo_cp_contents "$fromDir" "$toDir" &&
	unroot_dir "$toDir" &&
	echo "done copying dir from ${fromDir} to ${toDir}"
)

replace_db_file_if_needed() (
	echo 'tentatively copying initial db'
	process_global_vars "$@" &&
	error_check_all_paths "$MC_REFERENCE_SRC_DB" \
		"$(__get_app_root__)"/"$MC_SQLITE_FILEPATH"  &&
	if [ ! -e "$(__get_app_root__)"/"$MC_SQLITE_FILEPATH" ] \
	|| [ -n "$__CLEAN_FLAG" ] \
	|| str_contains "$__REPLACE__" "sqlite_file"; then
		cp -v "$MC_REFERENCE_SRC_DB" "$(__get_app_root__)"/"$MC_SQLITE_FILEPATH" &&
		return 0
		echo 'Done copying db'
	fi
	echo 'Done copying db'
	return 1
)

replace_db_file_if_needed2() {
	replace_db_file_if_needed "$@"
	return 0
}

setup_db() (
	echo 'setting up initial db'
	process_global_vars "$@" &&
	if ! replace_db_file_if_needed; then
		if [ -n "$(pgrep 'mc-ices')" ]; then
			shutdown_all_stations
		fi
		if [ -n "$(pgrep 'uvicorn')" ]; then
			kill_process_using_port "$MC_API_PORT"
		fi
	fi

	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate &&
	python <<-EOF
	from musical_chairs_libs.tables import metadata
	from musical_chairs_libs.services import EnvManager
	envManager = EnvManager()
	conn = envManager.get_configured_db_connection()
	metadata.create_all(conn.engine)

	print('Created all tables')
	EOF

	echo 'done with db stuff'
)

start_db_service() (
	echo 'starting database service'
	icecastName="$1"
	case $(uname) in
		(Linux*)
			if ! systemctl is-active --quiet mariadb; then
				sudo -p 'enabling mariadb' 'systemctl enable mariadb'
				sudo -p 'starting mariadb' 'systemctl start mariadb'
			fi
			;;
		(Darwin*)
			status=brew services list | grep mariadb | awk '{ print $2 }'
			if [ status = 'none' ]; then
				brew services start mariadb
			fi
			;;
		(*) ;;
	esac &&
	echo 'done starting database service'
)

revoke_default_db_accounts() (
	sudo -p 'disabling mysql user' mysql -u root -e \
		"REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'mysql'@'localhost'"
)

set_db_root_initial_password() (
	if [ -n "$__DB_SETUP_PASS__" ]; then
		sudo -p 'Updating db root password' mysql -u root -e \
			"SET PASSWORD FOR root@localhost = PASSWORD('${__DB_SETUP_PASS__}');"
	else
		echo 'Need a password for root db account'
		return 1
	fi
)


setup_database() (
	echo 'initial db setup'
	process_global_vars "$@" &&
	copy_dir "$MC_SQL_SCRIPTS_SRC" "$(__get_app_root__)"/"$MC_SQL_SCRIPTS_DIR_CL" &&
	__install_py_env_if_needed__ &&
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate &&
	#going to allow an error as a valid result by redirecting error to out
	rootHash=$(mysql -srN -e \
		"SELECT password FROM mysql.user WHERE user = 'root' LIMIT 1" 2>&1
	)
	redacted=$(echo "$rootHash" | sed -e 's/\*[A-F0-9]\{40\}/<suppresed>/')
	echo "root hash: ${redacted}"
	if [ -z "$rootHash" ] || [ "$rootHash" = 'invalid' ]; then
		set_db_root_initial_password
	fi &&
	(python <<EOF
from musical_chairs_libs.services import (
	DbRootConnectionService,
	DbOwnerConnectionService
)
dbName="musical_chairs_db"
with DbRootConnectionService() as rootConnService:
	rootConnService.create_db(dbName)
	rootConnService.create_owner()
	rootConnService.create_app_users()
	rootConnService.grant_owner_roles(dbName)

with DbOwnerConnectionService(dbName, echo=True) as ownerConnService:
	ownerConnService.create_tables()
	ownerConnService.add_path_permission_index()
	ownerConnService.grant_api_roles()
	ownerConnService.grant_radio_roles()
	ownerConnService.add_next_directory_level_func()
	ownerConnService.add_normalize_opening_slash()
EOF
	)

)

teardown_database() (
	echo 'tearing down db'
	process_global_vars "$@" >/dev/null 2>&1 &&
	__install_py_env_if_needed__ >/dev/null 2>&1 &&
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate \
		>/dev/null 2>&1 &&
	(python <<EOF
from musical_chairs_libs.services import (
	DbRootConnectionService,
	DbOwnerConnectionService
)

with DbRootConnectionService() as rootConnService:
	rootConnService.drop_all_users()
	rootConnService.drop_database("musical_chairs_db")

EOF
	)
)

print_schema_scripts() (
	process_global_vars "$@" &&
	__install_py_env_if_needed__ &&
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate &&
	printf '\033c' &&
	(python <<-EOF
	from musical_chairs_libs.services import EnvManager
	EnvManager.print_expected_schema()
	EOF
	)
)

sync_utility_scripts() (
	process_global_vars "$@" &&
	cp "$(get_repo_path)"/radio_common.sh "$(__get_app_root__)"/radio_common.sh
)

#copy python dependency file to the deployment directory
sync_requirement_list() (
	process_global_vars "$@" &&
	error_check_all_paths "$(get_repo_path)"/requirements.txt \
		"$(__get_app_root__)"/"$MC_APP_TRUNK"/requirements.txt \
		"$(__get_app_root__)"/requirements.txt &&
	#keep a copy in the parent radio directory
	cp "$(get_repo_path)"/requirements.txt \
		"$(__get_app_root__)"/"$MC_APP_TRUNK"/requirements.txt &&
	cp "$(get_repo_path)"/requirements.txt "$(__get_app_root__)"/requirements.txt
)

gen_pass() (
	pass_len=${1:-16}
	LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c "$pass_len"
)

is_ssh() (
	[ -n "$SSH_CONNECTION" ]
)

run_initial_install_script() (
	process_global_vars "$@" &&
	sh $(get_repo_path)/install_setup.sh
)

compare_dirs() (
	srcDir="$1"
	cpyDir="$2"
	error_check_all_paths "$srcDir" "$cpyDir"
	exitCode=0
	if [ ! -e "$cpyDir" ]; then
		echo "$cpyDir/ is not in place"
		return 1
	fi
	srcFifo='src_fifo'
	cpyFifo='cpy_fifo'
	cmpFifo='cmp_fifo'
	rm -f "$srcFifo" "$cpyFifo" "$cmpFifo"
	mkfifo "$srcFifo" "$cpyFifo" "$cmpFifo"

	srcRes=$(find "$srcDir" | \
		sed "s@${srcDir%/}/\{0,1\}@@" | sort)
	cpyRes=$(find "${cpyDir}" -not -path "${cpyDir}/${MC_PY_ENV}/*" \
		-and -not -path "${cpyDir}/${MC_PY_ENV}" | \
		sed "s@${cpyDir%/}/\{0,1\}@@" | sort)

	get_file_list() (
		supress="$1"
		echo "$srcRes" > "$srcFifo" &
		echo "$cpyRes" > "$cpyFifo" &
		[ -n "$supress" ] && comm "-${supress}" "$srcFifo" "$cpyFifo" ||
			comm "$srcFifo" "$cpyFifo"
	)

	inBoth=$(get_file_list 12)
	inSrc=$(get_file_list 23)
	inCpy=$(get_file_list 13)
	[ -n "$(echo "${inCpy}" | xargs)" ] &&
			{
				echo "There are items that only exist in ${cpyDir}"
				exitCode=2
			}
	[ -n "$(echo "${inSrc}" | xargs)" ] &&
			{
				echo "There are items missing from the ${cpyDir}"
				exitCode=3
			}
	if [ -n "$inBoth" ]; then
		exitCode=4
		echo "$inBoth" > "$cmpFifo" &
		while read fileName; do
			[ "${srcDir%/}/${fileName}" -nt "${cpyDir%/}/${fileName}" ] &&
				echo "${fileName} is outdated"
		done <"$cmpFifo"
	fi
	rm -f "$srcFifo" "$cpyFifo" "$cmpFifo"
	return "$exitCode"
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

__get_keychain_osx__() (
	echo '/Library/Keychains/System.keychain'
)

__get_debug_cert_name__() (
	echo "$MC_PROJ_NAME"_localhost_debug
)

__get_debug_cert_path__() (
	echo $(get_localhost_key_dir)/$(__get_debug_cert_name__)
)

__get_local_nginx_cert_name__() (
	echo "$MC_PROJ_NAME"_localhost_nginx
)

__get_local_nginx_cert_path__() (
	echo $(get_localhost_key_dir)/$(__get_local_nginx_cert_name__)
)

is_cert_expired() (
	! openssl x509 -checkend 3600 -noout >/dev/null
)

extract_sha256_from_cert() (
	openssl x509 -fingerprint -sha256 \
	| perl -ne 'print "$1\n" if /SHA256 Fingerprint=([A-F0-9:]+)/' | tr -d ':'
)

extract_commonName_from_cert() (
	openssl x509 -subject \
	| perl -ne 'print "$1\n" if m{CN *= *([^/]+)}'
)


scan_pems_for_common_name() (
	commonName="$1"
	activate_mc_env &&
	python -m 'musical_chairs_libs.dev.ssl.installed_certs' "$commonName" \
		< /etc/ssl/certs/ca-certificates.crt 
)

certs_matching_name() (
	commonName="$1"
		case $(uname) in
		(Darwin*)
			security find-certificate -a -p -c "$commonName" \
				$(__get_keychain_osx__)
			;;
		(*)
			scan_pems_for_common_name "$commonName"
			;;
	esac
)

__certs_matching_name_exact__() (
	commonName="$1"
	certs_matching_name "$commonName" \
	| extract_commonName_from_cert \
	| input_match "$commonName"
)

__get_openssl_default_conf__() (
	case $(uname) in
		(Darwin*)
			echo '/System/Library/OpenSSL/openssl.cnf'
			;;
		(Linux*)
			echo '/etc/ssl/openssl.cnf'
			;;
		(*) ;;
	esac
)

__openssl_gen_cert__() (
	commonName="$1"
	domain="$2" &&
	publicKeyFile="$3" &&
	privateKeyFile="$4" &&
	mkfifo cat_config_fifo
	{
	cat<<-OpenSSLConfig
	$(cat $(__get_openssl_default_conf__))
	$(printf "[SAN]\nsubjectAltName=DNS:${domain},IP:127.0.0.1")
	OpenSSLConfig
	} > cat_config_fifo &
	openssl req -x509 -sha256 -new -nodes -newkey rsa:2048 -days 7 \
	-subj "/C=US/ST=CA/O=fake/CN=${commonName}" -reqexts SAN -extensions SAN \
	-config cat_config_fifo \
	-keyout "$privateKeyFile" -out "$publicKeyFile"
	errCode="$?"
	rm -f cat_config_fifo
	return "$errCode"
)

__install_local_cert_osx__() (
	publicKeyFile="$1" &&
	sudo security add-trusted-cert -p \
		ssl -d -r trustRoot \
		-k $(__get_keychain_osx__) "$publicKeyFile"
)

create_firefox_cert_policy_file() (
	publicKeyName="$1" &&
	pemFile=$(echo "$publicKeyName" | sed 's/.crt$/.pem/')
	content=$(cat <<END
{
	"policies": {
		"Certificates": {
			"ImportEnterpriseRoots": true,
			"Install": [
				"$publicKeyName",
				"/etc/ssl/certs/$pemFile"
			]
		}
	}
}
END
)
	sudo -p "Need password to create firefox policy file" \
		sh -c \
		"echo '$content' > '/usr/share/firefox-esr/distribution/policies.json'"
)

__set_firefox_cert_policy__() (
	publicKeyName="$1" &&
	policyFile='/usr/share/firefox-esr/distribution/policies.json'
	if firefox -v 2>/dev/null; then
		if [ -s "$policyFile" ]; then
			content=$(cat "$policyFile" \
			| get_trusted_by_firefox_json_with_added_cert "$publicKeyName")
				if (exit "$?"); then
					sudo -p "Need password to update firefox policy file" \
					sh -c \
					"echo '$content' > '$policyFile'"
				else
					create_firefox_cert_policy_file "$publicKeyName"
				fi
		else
			create_firefox_cert_policy_file "$publicKeyName"
		fi
	fi
)

#"import sys, json; print(json.load(sys.stdin, strict=False)['$jsonKey'])"
get_trusted_by_firefox_json_with_added_cert() (
	publicKeyFile="$1"
	pemFile=$(echo "$publicKeyFile" | sed 's/.crt$/.pem/')
	pyScript=$(cat <<-END
		import sys
		import json
		config = json.load(sys.stdin, strict=False)
		installed = config['policies']['Certificates']['Install']
		if not "$publicKeyFile" in installed:
		  installed.append("$publicKeyFile")
		if not "/etc/ssl/certs/$pemFile" in installed:
		  installed.append("/etc/ssl/certs/$pemFile")
		print(json.dumps(config))
	END
	)
	python3 -c "$pyScript"
)

__install_local_cert_debian__() (
	publicKeyFile="$1" &&
	sudo -p 'Password to install trusted certificate' \
		cp "$publicKeyFile" /usr/local/share/ca-certificates &&
	sudo update-ca-certificates
)

__clean_up_invalid_cert__() (
	commonName="$1" &&
	case $(uname) in
		(Darwin*)
			cert=''
			#turns out the d flag is not posix compliant :<
			certs_matching_name "$commonName" \
				| while read line; do
					cert=$(printf "%s\n%s" "$cert" "$line")
					if [ "$line" = '-----END CERTIFICATE-----' ]; then
						sha256Value=$(echo "$cert" | extract_sha256_from_cert) &&
						echo "$cert" | is_cert_expired &&
						sudo security delete-certificate \
							-Z "$sha256Value" -t $(__get_keychain_osx__)
						cert=''
					fi
				done
			;;
		(*)
				cert=''
				#turns out the d flag is not posix compliant :<
				scan_pems_for_common_name "$commonName" \
					| while read line; do
						cert=$(printf "%s\n%s" "$cert" "$line")
						if [ "$line" = '-----END CERTIFICATE-----' ]; then
							sha256Value=$(echo "$cert" | extract_sha256_from_cert) &&
							echo "$cert" | is_cert_expired && 
							{
								sudo -p \
									"Need pass to delete from /usr/local/share/ca-certificates" \
									rm /usr/local/share/ca-certificates/"$commonName"*.crt;
								sudo update-ca-certificates
							}
							cert=''
						fi
					done
			;;
	esac
	return 0
)

__setup_ssl_cert_local__() (
	commonName="$1"
	domain="$2" &&
	publicKeyFile="$3" &&
	privateKeyFile="$4" &&

	case $(uname) in
		(Darwin*)
			__openssl_gen_cert__ "$commonName" "$domain" \
				"$publicKeyFile" "$privateKeyFile" &&
			__install_local_cert_osx__ "$publicKeyFile" ||
			return 1
			;;
		(*)
			if [ -f '/etc/debian_version' ]; then
				__openssl_gen_cert__ "$commonName" "$domain" \
					"$publicKeyFile" "$privateKeyFile" &&
				__install_local_cert_debian__ "$publicKeyFile" ||
				return 1
			else
				echo "operating system not configured"
				return 1
			fi
			;;
	esac
	return 0
)

setup_ssl_cert_local_debug() (
	process_global_vars "$@" &&
	publicKeyFile=$(__get_debug_cert_path__).public.key.crt &&
	privateKeyFile=$(__get_debug_cert_path__).private.key.pem &&
	__clean_up_invalid_cert__ "${MC_APP_NAME}-localhost"
	__setup_ssl_cert_local__ "${MC_APP_NAME}-localhost" 'localhost' \
		"$publicKeyFile" "$privateKeyFile"
	publicKeyName=$(__get_debug_cert_name__).public.key.crt &&
	__set_firefox_cert_policy__ "$publicKeyName" &&
	setup_react_env_debug
)

print_ssl_cert_info() (
	process_global_vars "$@" &&
	domain=$(__get_domain_name__ "$MC_APP_ENV" 'omitPort') &&
	case "$MC_APP_ENV" in
		(local*)
			isDebugServer=${1#is_debug_server=}
			if [ -n "$isDebugServer" ]; then
				domain="${domain}-localhost"
			fi
				echo "#### nginx info ####"
				echo "$(__get_local_nginx_cert_path__).public.key.crt"
				cert=''
				certs_matching_name "$domain" \
					| while read line; do
						cert=$(printf "%s\n%s" "$cert" "$line")
						if [ "$line" = '-----END CERTIFICATE-----' ]; then
							sha256Value=$(echo "$cert" | extract_sha256_from_cert) &&
							echo "$cert" | openssl x509 -enddate -subject -noout
							cert=''
						fi
					done
				echo "#### debug server info ####"
				echo "${domain}-localhost"
				echo "$(__get_debug_cert_path__).public.key.crt"
				cert=''
				certs_matching_name "${MC_APP_NAME}-localhost" \
					| while read line; do
						cert=$(printf "%s\n%s" "$cert" "$line")
						if [ "$line" = '-----END CERTIFICATE-----' ]; then
							sha256Value=$(echo "$cert" | extract_sha256_from_cert) &&
							echo "$cert" | openssl x509 -enddate -subject -noout
							cert=''
						fi
					done
					;;
		(*)
			publicKeyFile=$(__get_remote_public_key__) &&
			cat "$publicKeyFile" | openssl x509 -enddate -subject -noout
			;;
	esac
)

add_test_url_to_hosts() (
	domain="$1"
	if [ -z "$domain" ]; then
		echo "Missing domain in adding to hosts"
		return 1
	fi
	if ! grep "$domain" /etc/hosts >/dev/null; then
		sudo -p 'password to update hosts' \
			sh -c "printf '127.0.0.1\t${domain}\n' >> /etc/hosts"
	fi
)

setup_ssl_cert_nginx() (
	process_global_vars "$@" &&
	domain=$(__get_domain_name__ "$MC_APP_ENV" 'omitPort') &&
	case "$MC_APP_ENV" in
		(local*)
			add_test_url_to_hosts "$domain"
			publicKeyFile=$(__get_local_nginx_cert_path__).public.key.crt &&
			privateKeyFile=$(__get_local_nginx_cert_path__).private.key.pem &&
			# we're leaving off the && because what would that even mean here?
			__clean_up_invalid_cert__ "$domain"
			if [ -z $(__certs_matching_name_exact__ "$domain") ]; then
				__setup_ssl_cert_local__ \
				"$domain" "$domain" "$publicKeyFile" "$privateKeyFile"
			fi
			publicKeyName=$(__get_local_nginx_cert_name__).public.key.crt &&
			__set_firefox_cert_policy__ "$publicKeyName"
			;;
		(*)
			publicKeyFile=$(__get_remote_public_key__) &&
			privateKeyFile=$(__get_remote_private_key__) &&
			intermediateKeyFile=$(__get_remote_intermediate_key__) &&

			if [ ! -e "$publicKeyFile" ] || [ ! -e "$privateKeyFile" ] ||
			cat "$publicKeyFile" | is_cert_expired ||
			str_contains "$__REPLACE__" "ssl_certs"; then
				echo "downloading new certs"
				sslVars=$(get_ssl_vars)
				echo "$sslVars" | stdin_json_extract_value 'privatekey' | \
				perl -pe 'chomp if eof' > "$privateKeyFile" &&
				echo "$sslVars" | \
				stdin_json_extract_value 'certificatechain' | \
				perl -pe 'chomp if eof' > "$publicKeyFile" &&
				echo "$sslVars" | \
				stdin_json_extract_value 'intermediatecertificate' | \
				perl -pe 'chomp if eof' > "$intermediateKeyFile"
			fi
			;;
	esac
)

setup_react_env_debug() (
	process_global_vars "$@" &&
	envFile="$MC_CLIENT_SRC"/.env.local
	echo "$envFile"
	echo 'VITE_API_VERSION=v1' > "$envFile"
	echo 'VITE_BASE_ADDRESS=https://localhost:8032' >> "$envFile"
	#VITE_SSL_PUBLIC, and SSL_KEY_FILE are used by create-react-app
	#when calling `npm start`
	echo "VITE_SSL_PUBLIC=$(__get_debug_cert_path__).public.key.crt" \
		>> "$envFile"
	echo "VITE_SSL_PRIVATE=$(__get_debug_cert_path__).private.key.pem" \
		>> "$envFile"
)

get_nginx_value() (
	key=${1:-'conf-path'}
	#break options into a list
	#then isolate the option we're interested in
	sudo -p "Need pass to get nginx values " \
		nginx -V 2>&1 | \
		sed 's/ /\n/g' | \
		sed -n "/--${key}/p" | \
		sed 's/.*=\(.*\)/\1/'
)

get_nginx_conf_dir_include() (
	nginxConf=$(get_nginx_value)
	guesses=$(cat<<-'EOF'
		include /etc/nginx/sites-enabled/*;
		include servers/*;
	EOF
	)
	#determine which one of these locations is referenced in the nginx config
	echo "$guesses" | while read guess; do
		if grep -F "$guess" "$nginxConf" >/dev/null; then
			echo "$guess"
			break
		fi
	done
)

__copy_and_update_nginx_template__() {
	sudo -p 'copy nginx config' \
		cp "$MC_TEMPLATES_SRC"/nginx_template.conf "$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e \
			"s@<MC_APP_CLIENT_PATH_CL>@$(get_web_root)/${MC_APP_CLIENT_PATH_CL}@" \
			"$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<MC_SERVER_NAME>@${MC_SERVER_NAME}@g" "$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<MC_API_PORT>@${MC_API_PORT}@" "$appConfFile"
}

update_nginx_conf() (
	echo 'updating nginx site conf'
	appConfFile="$1"
	error_check_all_paths "$MC_TEMPLATES_SRC" "$appConfFile" &&
	__copy_and_update_nginx_template__ &&
	case "$MC_APP_ENV" in
		(local*)
			publicKey=$(__get_local_nginx_cert_path__).public.key.crt &&
			privateKey=$(__get_local_nginx_cert_path__).private.key.pem &&
			sudo -p "update ${appConfFile}" \
				perl -pi -e "s/<listen>/8080 ssl/" "$appConfFile" &&
			sudo -p "update ${appConfFile}" \
				perl -pi -e "s@<ssl_public_key>@${publicKey}@" \
				"$appConfFile" &&
			sudo -p "update ${appConfFile}" \
				perl -pi -e "s@<ssl_private_key>@${privateKey}@" \
				"$appConfFile"
			;;
		(*)
			sudo -p "update ${appConfFile}" \
				perl -pi -e "s/<listen>/[::]:443 ssl/" "$appConfFile" &&

				sudo -p "update ${appConfFile}" \
				perl -pi -e \
				"s@<ssl_public_key>@$(__get_remote_public_key__)@" \
				"$appConfFile" &&
			sudo -p "update ${appConfFile}" \
				perl -pi -e \
				"s@<ssl_private_key>@$(__get_remote_private_key__)@" \
				"$appConfFile" &&
			sudo -p "update ${appConfFile}" \
				perl -pi -e \
				"s@<ssl_intermediate>@$(__get_remote_intermediate_key__)@" \
				"$appConfFile" &&
			sudo -p "update ${appConfFile}" \
				perl -pi -e \
				's/#ssl_trusted_certificate/ssl_trusted_certificate/' \
				"$appConfFile"
			;;
	esac &&
	echo 'done updating nginx site conf'
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
		sitesFolderPath=$(dirname $(get_nginx_value))
		echo "sitesFolderPath: ${sitesFolderPath}" >&2
		absPath="$sitesFolderPath"/"$confDir"
		if [ ! -d "$absPath" ]; then
			if [ -e "$absPath" ]; then
				echo "{$absPath} is a file, not a directory" 1>&2
				return 1
			fi
			#Apparently nginx will look for includes with either an absolute path
			#or path relative to the config
			#some os'es are finicky about creating directories at the root lvl
			#even with sudo, so we're not going to even try
			#we'll just create missing dir in $sitesFolderPath folder
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
	echo 'enabling nginx site confs'
	confDirInclude="$1"
	escapedGuess=$(literal_to_regex "$confDirInclude")
	#uncomment line if necessary in config
	sudo -p "Enable ${confDirInclude}" \
		perl -pi -e "s/^[ \t]*#// if m@$escapedGuess@" "$(get_nginx_value)" &&
	echo 'done enabling nginx site confs'
)

restart_nginx() (
	echo 'starting/restarting up nginx'
	case $(uname) in
		(Darwin*)
			nginx -s reload
			;;
		(Linux*)
			if systemctl is-active --quiet nginx; then
				sudo -p 'starting nginx' systemctl restart nginx
			else
				sudo -p 'enabling nginx' systemctl enable nginx
				sudo -p 'restarting nginx' systemctl start nginx
			fi
			;;
		(*) ;;
	esac &&
	echo 'Done starting/restarting up nginx'
)

print_nginx_conf_location() (
	process_global_vars "$@" >/dev/null &&
	confDirInclude=$(get_nginx_conf_dir_include) &&
	confDir=$(get_abs_path_from_nginx_include "$confDirInclude") 2>/dev/null
	echo "$confDir"/"$MC_APP_NAME".conf
)

print_cert_paths() (
	process_global_vars "$@" >/dev/null &&
	confDirInclude=$(get_nginx_conf_dir_include) &&
	confDir=$(get_abs_path_from_nginx_include "$confDirInclude") 2>/dev/null
	cat "$confDir"/"$MC_APP_NAME".conf | perl -ne \
	'print "$1\n" if /ssl_certificate ([^;]+)/'
	cat "$confDir"/"$MC_APP_NAME".conf | perl -ne \
	'print "$1\n" if /ssl_certificate_key ([^;]+)/'
	cat "$confDir"/"$MC_APP_NAME".conf | perl -ne \
	'print "$1\n" if /[^#]ssl_trusted_certificate ([^;]+)/'
)

setup_nginx_confs() (
	echo 'setting up nginx confs'
	process_global_vars "$@" &&
	confDirInclude=$(get_nginx_conf_dir_include) &&
	#remove trailing path chars
	confDir=$(get_abs_path_from_nginx_include "$confDirInclude") &&
	setup_ssl_cert_nginx &&
	enable_nginx_include "$confDirInclude" &&
	update_nginx_conf "$confDir"/"$MC_APP_NAME".conf &&
	sudo -p 'Remove default nginx config' \
		rm -f "$confDir"/default &&
	restart_nginx &&
	echo 'done setting up nginx confs'
)

start_icecast_service() (
	echo 'starting icecast service'
	icecastName="$1"
	case $(uname) in
		(Linux*)
			if ! systemctl is-active --quiet "$icecastName"; then
				sudo -p "enabling ${icecastName}" systemctl enable "$icecastName"
				sudo -p "starting ${icecastName}" systemctl start "$icecastName"
			fi
			;;
		(*) ;;
	esac &&
	echo 'done starting icecast service'
)


install_ices() (
	set_env_vars "$@" &&
	if ! mc-ices -V 2>/dev/null || ! is_ices_version_good; then
		shutdown_all_stations &&
		projDir="$(__get_app_root__)"/"$MC_BUILD_DIR"/"$MC_PROJ_NAME" &&
		folderPath="$projDir"/compiled_dependencies &&
		if [  ! -f "$folderPath"/build_ices.sh ]; then
			folderPath="$PWD"/compiled_dependencies
		fi &&
		sh "$folderPath"/build_ices.sh "$__ICES_BRANCH__"
	fi
)

get_icecast_conf() (
	icecastName="$1"
	case $(uname) in
		(Linux*)
			if ! systemctl status "$icecastName" >/dev/null 2>&1; then
					echo "$icecastName is not running at the moment"
					exit 1
			fi
				systemctl status "$icecastName" | grep -A2 CGroup | \
					head -n2 | tail -n1 | awk '{ print $NF }'
			;;
		(Darwin*)
			#we don't have icecast on the mac anyway so we'll just return the
			#source code location
			echo "$MC_TEMPLATES_SRC"/icecast.xml
			;;
		*) ;;
	esac
)

show_current_py_lib_files() (
	process_global_vars "$@" >/dev/null 2>&1 &&
	set_python_version_const >/dev/null 2>&1 &&
	envDir="lib/python${pyMajor}.${pyMinor}/site-packages/${MC_LIB_NAME}"
	echo "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/"$envDir"
)

show_web_py_files() (
	process_global_vars "$@" >/dev/null 2>&1 &&
	echo "$(get_web_root)"/"$MC_APP_API_PATH_CL"
)

show_icecast_log() (
	process_global_vars "$@" >/dev/null 2>&1 &&
	__install_py_env_if_needed__ >/dev/null 2>&1 &&
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate >/dev/null \
		2>&1 &&
	(python <<-EOF
	from musical_chairs_libs.services import ProcessService
	from musical_chairs_libs.services import EnvManager
	icecastConfLocation = ProcessService.get_icecast_conf_location()
	logdir = EnvManager.read_config_value(
		icecastConfLocation,
		"logdir"
	)
	errorlog = EnvManager.read_config_value(
		icecastConfLocation,
		"errorlog"
	)
	print(f"{logdir}/{errorlog}")
	EOF
	)
)

show_ices_station_log() (
	owner="$1"
	shift
	station="$1"
	shift
	process_global_vars "$@" >/dev/null 2>&1 &&
	__install_py_env_if_needed__ >/dev/null 2>&1 &&
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate >/dev/null \
		2>&1 &&
	logName="$(__get_app_root__)"/"$MC_ICES_CONFIGS_DIR"/ices."$owner"_"$station".conf
	(python <<-EOF
	from musical_chairs_libs.services import EnvManager
	logdir = EnvManager.read_config_value(
		"${logName}",
		"BaseDirectory"
	)
	print(f"{logdir}/ices.log")
	EOF
	)
)

update_icecast_conf() (
	echo "updating icecast config"
	icecastConfLocation="$1"
	sourcePassword="$2"
	relayPassword="$3"
	adminPassword="$4"

	sudo -p 'Pass required to modify icecast config: ' \
		perl -pi -e "s/>\w*/>${sourcePassword}/ if /source-password/" \
		"$icecastConfLocation" &&
	sudo -p 'Pass required to modify icecast config: ' \
		perl -pi -e "s/>\w*/>${relayPassword}/ if /relay-password/" \
		"$icecastConfLocation" &&
	sudo -p 'Pass required to modify icecast config: ' \
		perl -pi -e "s/>\w*/>${adminPassword}/ if /admin-password/" \
		"$icecastConfLocation" &&
	sudo -p 'Pass required to modify icecast config: ' \
		perl -pi -e "s@^([ \t]*)<.*@\1<bind-address>::</bind-address>@" \
		-e "if /<bind-address>/" \
		"$icecastConfLocation" &&
	echo "done updating icecast config"
)

__update_ices_config__() (
	conf="$1"
	sourcePassword="$2"
	perl -pi -e "s/>\w*/>${sourcePassword}/ if /Password/" "$conf"
)

update_ices_config() (
	conf="$1"
	process_global_vars "$@"
	__install_py_env_if_needed__ >/dev/null 2>&1 &&
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate >/dev/null \
		2>&1 &&
	sourcePassword=$(python <<-EOF
	from musical_chairs_libs.services import ProcessService
	from musical_chairs_libs.services import EnvManager
	icecastConfLocation = ProcessService.get_icecast_conf_location()
	sourcePassword = EnvManager.read_config_value(
		icecastConfLocation,
		"source-password"
	)

	print(sourcePassword)
	EOF
	)
	__update_ices_config__ "$conf" "$sourcePassword"
)

update_all_ices_confs() (
	echo "updating ices confs"
	sourcePassword="$1"
	process_global_vars "$@"
	for conf in "$(__get_app_root__)"/"$MC_ICES_CONFIGS_DIR"/*.conf; do
		[ ! -s "$conf" ] && continue
		__update_ices_config__ "$conf" "$sourcePassword"
	done &&
	echo "done updating ices confs"
)


setup_icecast_confs() (
	echo "setting up icecast/ices"
	icecastName="$1"
	process_global_vars "$@" &&
	#need to make sure that  icecast is running so we can get the config
	#location from systemd. While icecast does have a custom config option
	#I don't feel like editing the systemd service to make it happen
	start_icecast_service "$icecastName" &&
	icecastConfLocation=$(get_icecast_conf "$icecastName") &&
	sourcePassword=$(gen_pass) &&
	update_icecast_conf "$icecastConfLocation" \
		"$sourcePassword" $(gen_pass) $(gen_pass) &&
	update_all_ices_confs "$sourcePassword" &&
	sudo -p "restarting ${icecastName}" systemctl restart "$icecastName" &&
	echo "done setting up icecast/ices"
)


run_song_scan() (
	process_global_vars "$@"
	link_to_music_files &&
	setup_radio &&
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate &&

	if str_contains "$__REPLACE__" "sqlite_file"; then
		sudo_rm_contents "$(__get_app_root__)"/"$MC_SQLITE_FILEPATH" || return "$?"
	fi &&
	# #python_env
	python  <<-EOF
	import os
	from musical_chairs_libs.song_scanner import SongScanner
	from musical_chairs_libs.services import EnvManager
	print("Starting")
	EnvManager.setup_db_if_missing(echo = True)
	songScanner = SongScanner()
	inserted = songScanner.save_paths('$(__get_app_root__)/${MC_CONTENT_HOME}')
	print(f"saving paths done: {inserted} inserted")
	updated = songScanner.update_metadata('$(__get_app_root__)/${MC_CONTENT_HOME}')
	print(f"updating songs done: {updated}")
	EOF
)

shutdown_all_stations() (
	process_global_vars "$@" &&
	#gonna assume that the environment has been setup because if
	#the environment hasn't been setup yet then no radio stations
	#are running
	if [ ! -s "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate ]; then
		echo "python env not setup, so no stations to shut down"
		return
	fi
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate &&
	# #python_env
	{ python  <<EOF
try:
	from musical_chairs_libs.station_service import StationService
	from sqlalchemy.exc import OperationalError
	try:
		stationService = StationService()
		stationService.end_all_stations()
	except OperationalError as ex:
		print("Could not the shutdown operation."
		" Assuming that they are already down.")
except ModuleNotFoundError:
	print("Could not import something")
print("Done")
EOF
	} &&
	echo "Done ending all stations"
)

__start_station_with_pipe__() (
	conf="$1"
	port="$2"
	ownerName=$(echo "$conf" | cut -d '_' -f 1)
	stationName=$(basename $(echo "$conf" | cut -d '_' -f 2) '.conf')
	python -m musical_chairs_libs.stream \
		"$MC_DATABASE_NAME" "$stationName" "$ownerName" | \
			toot-ices -c "$conf" #\
			# >"$(__get_app_root__)"/"$MC_RADIO_LOG_DIR_CL"/"${ownerName}_${stationName}" \
			# 2>&1 &
) 

__start_station_local_file_module__() (
	conf="$1"
	mc-ices -c -B "$conf"
)

start_station() (
	conf="$1"
	set_env_vars "$@" &&
	pkgMgrChoice=$(get_pkg_mgr) &&
	activate_mc_env &&
	__start_station_with_pipe__ "$conf" 50007
)

startup_radio() (
	set_env_vars "$@" &&
	pkgMgrChoice=$(get_pkg_mgr) &&
	link_to_music_files &&
	setup_radio &&
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate &&
	for conf in "$(__get_app_root__)"/"$MC_ICES_CONFIGS_DIR"/*.conf; do
		[ ! -s "$conf" ] && continue
		__start_station_local_file_module__ "$conf"
	done
)

__get_remote_export_script__() (
	if [ -n "$1" ]; then
		exportMod='export'
	else
		exportMod=''
	fi
	output="export expName='${expName}';"
	output="${output} export AWS_ACCESS_KEY_ID='$(__get_s3_api_key__)';" &&
	output="${output} export AWS_SECRET_ACCESS_KEY='$(__get_s3_secret__)';" &&
	output="${output} export S3_ACCESS_KEY_ID='$(__get_s3_api_key__)';" &&
	output="${output} export S3_SECRET_ACCESS_KEY='$(__get_s3_secret__)';" &&
	output="${output} export PB_SECRET='$(__get_pb_secret__)';" &&
	output="${output} export PB_API_KEY='$(__get_pb_api_key__)';" &&
	output="${output} export MC_AUTH_SECRET_KEY='$(__get_mc_auth_key__)';" &&
	output="${output} export MC_DATABASE_NAME='musical_chairs_db';" &&
	output="${output} export __DB_SETUP_PASS__='$(__get_db_setup_key__)';" &&
	output="${output} export MC_DB_PASS_OWNER='$(__get_db_owner_key__)';" &&
	output="${output} export MC_DB_PASS_API='$(__get_api_db_user_key__)';" &&
	output="${output} export MC_DB_PASS_RADIO='$(__get_radio_db_user_key__)';" &&
	output="${output} export S3_BUCKET_NAME='$(__get_s3_bucket_name__)';" &&
	output="${output} export S3_REGION_NAME='$(__get_s3_region_name__)';" &&
	output="${output} export __ICES_BRANCH__='$(__get_ices_branch__)';" &&
	echo "$output"
)

startup_api() (
	set_env_vars "$@" &&
	if ! str_contains "$__SKIP__" "setup_api"; then
		setup_api
	fi &&
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate
	errCode="$?"
	# see #python_env
	#put uvicorn in background within a subshell so that it doesn't put
	#the whole chain in the background, and then block due to some of the
	#preceeding comands still having stdout open
	(uvicorn --app-dir "$(get_web_root)"/"$MC_APP_API_PATH_CL" \
	--root-path /api/v1 \
	--host 0.0.0.0 \
	--port "$MC_API_PORT" \
	"index:app" </dev/null >api.out 2>&1 &)
	(exit "$errCode") &&
	echo "Server base is $(pwd). Look there for api.out and the log file"
	echo "done starting up api. Access at ${MC_FULL_URL}" ||
	echo "failed while trying to start up api"
)


startup_nginx_for_debug() (
	process_global_vars "$@" &&
	export MC_API_PORT='8032'
	setup_nginx_confs &&
	restart_nginx
)

setup_api() (
	echo "setting up api"
	process_global_vars "$@" &&
	kill_process_using_port "$MC_API_PORT" &&
	sync_utility_scripts &&
	sync_requirement_list &&
	copy_dir "$MC_TEMPLATES_SRC" "$(__get_app_root__)"/"$MC_TEMPLATES_DIR_CL" &&
	copy_dir "$MC_API_SRC" "$(get_web_root)"/"$MC_APP_API_PATH_CL" &&
	create_py_env_in_app_trunk &&
	setup_database &&
	setup_nginx_confs &&
	echo "done setting up api"
)

create_swap_if_needed() (
		case $(uname) in
		(Linux*)
			if [ ! -e /swapfile ]; then
				sudo dd if=/dev/zero of=/swapfile bs=128M count=24 &&
				sudo chmod 600 /swapfile &&
				sudo mkswap /swapfile &&
				sudo swapon /swapfile
			fi
			;;
		(*) ;;
	esac
)

setup_client() (
	echo "setting up client"
	process_global_vars "$@" &&
	error_check_all_paths "$MC_CLIENT_SRC" \
		"$(get_web_root)"/"$MC_APP_CLIENT_PATH_CL" &&
	#in theory, this should be sourced by .bashrc
	#but sometimes there's an interactive check that ends the sourcing early
	if [ -z "$NVM_DIR" ]; then
		export NVM_DIR="$HOME"/.nvm
		[ -s "$NVM_DIR"/nvm.sh ] && \. "$NVM_DIR"/nvm.sh  # This loads nvm
	fi &&
	#check if web application folder exists, clear out if it does,
	#delete otherwise
	empty_dir_contents "$(get_web_root)"/"$MC_APP_CLIENT_PATH_CL" &&

	export VITE_API_VERSION=v1 &&
	export VITE_BASE_ADDRESS="$MC_FULL_URL" &&
	#set up react then copy
	#install packages
	npm --prefix "$MC_CLIENT_SRC" i &&
	#build code (transpile it)
	npm run --prefix "$MC_CLIENT_SRC" build &&
	#copy built code to new location
	sudo -p 'Pass required to copy client files: ' \
		cp -rv "$MC_CLIENT_SRC"/build/. \
			"$(get_web_root)"/"$MC_APP_CLIENT_PATH_CL" &&
	unroot_dir "$(get_web_root)"/"$MC_APP_CLIENT_PATH_CL" &&
	echo "done setting up client"
)

setup_full_web() (
	echo "setting up full web"
	process_global_vars "$@" &&
	setup_client &&
	setup_api &&
	echo "done setting up full web."
)

startup_full_web() (
	echo "starting up full web"
	process_global_vars "$@" &&
	setup_client &&
	startup_api &&
	echo "done starting up full web. Access at ${MC_FULL_URL}"
)

#assume install_setup.sh has been run
setup_radio() (
	echo "setting up radio"
	process_global_vars "$@" &&
	shutdown_all_stations &&
	sync_requirement_list &&
	sync_utility_scripts &&

	create_py_env_in_app_trunk &&
	copy_dir "$MC_TEMPLATES_SRC" "$(__get_app_root__)"/"$MC_TEMPLATES_DIR_CL" &&
	setup_database &&
	pkgMgrChoice=$(get_pkg_mgr) &&
	icecastName=$(get_icecast_name "$pkgMgrChoice") &&
	setup_icecast_confs "$icecastName" &&
	echo "done setting up radio"
)

__create_fake_keys_file__() {
	echo "mc_auth_key=$(openssl rand -hex 32)" \
		> "$(__get_app_root__)"/keys/"$MC_PROJ_NAME"
}

get_hash_of_file() (
	file="$1"
	pyScript=$(cat <<-END
		import sys, hashlib
		print(hashlib.md5(sys.stdin.read().encode("utf-8")).hexdigest())
	END
	)
	cat "$file" | python3 -c "$pyScript"
)

regen_file_reference_file() (
	process_global_vars "$@" &&
	outputFile="$MC_LIB_SRC"/dtos_and_utilities/file_reference.py
	printf '####### This file is generated. #######\n' > "$outputFile"
	printf '# edit regen_file_reference_file #\n' >> "$outputFile"
	printf '# in radio_common.sh and rerun\n' >> "$outputFile"
	printf 'from enum import Enum\n\n' >> "$outputFile"
	printf 'class SqlScripts(Enum):\n' >> "$outputFile"
	for script in "$MC_SQL_SCRIPTS_SRC"/*.sql; do
		enumName=$(basename "$script" '.sql' | \
			sed -e 's/[0-9]*.\(.*\)/\1/' | \
			perl -pe 'chomp if eof' | \
			tr '[:punct:][:space:]' '_' | \
			tr '[:lower:]' '[:upper:]'
		)
		fileName=$(basename "$script")
		hashValue=$(get_hash_of_file "$script")
		printf \
		"\t${enumName} = (\n\t\t\"${fileName}\",\n\t\t\"${hashValue}\"\n\t)\n" \
			>> "$outputFile"
	done
	printf '\n\t@property\n' >> "$outputFile"
	printf '\tdef file_name(self) -> str:\n' >> "$outputFile"
	printf '\t\treturn self.value[0]\n\n' >> "$outputFile"
	printf '\t@property\n' >> "$outputFile"
	printf '\tdef checksum(self) -> str:\n' >> "$outputFile"
	printf '\t\treturn self.value[1]\n' >> "$outputFile"
)

replace_sql_script() (
	process_global_vars "$@" &&
	setup_app_directories
	copy_dir "$MC_SQL_SCRIPTS_SRC" "$(__get_app_root__)"/"$MC_SQL_SCRIPTS_DIR_CL"
)

#assume install_setup.sh has been run
setup_unit_test_env() (
	echo 'setting up test environment'
	process_global_args "$@" || return

	define_global_vars &&
	define_directory_vars &&
	export __TEST_FLAG__='true'
	publicKeyFile=$(__get_debug_cert_path__).public.key.crt

	__create_fake_keys_file__
	setup_app_directories

	copy_dir "$MC_TEMPLATES_SRC" "$(__get_app_root__)"/"$MC_TEMPLATES_DIR_CL" &&
	copy_dir "$MC_SQL_SCRIPTS_SRC" \
		"$(__get_app_root__)"/"$MC_SQL_SCRIPTS_DIR_CL" &&
	error_check_all_paths "$MC_REFERENCE_SRC_DB" \
		"$(__get_app_root__)"/"$MC_SQLITE_FILEPATH" &&
	sync_requirement_list
	setup_env_api_file
	pyEnvPath="$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"
	#redirect stderr into stdout so that missing env will also trigger redeploy
	srcChanges=$(find "$MC_LIB_SRC" -newer "$pyEnvPath" 2>&1)
	if [ -n "$srcChanges" ] || \
	[ "$(get_repo_path)"/requirements.txt -nt "$pyEnvPath" ]
	then
		echo "changes?"
		create_py_env_in_app_trunk
	fi
	replace_db_file_if_needed2 &&
	echo "$(__get_app_root__)"/"$MC_CONFIG_DIR"/.env &&
	echo "PYTHONPATH='${MC_SRC_PATH}:${MC_SRC_PATH}/api'" \
		>> "$(__get_app_root__)"/"$MC_CONFIG_DIR"/.env &&
	echo "done setting up test environment"
)

setup_all() (
	echo "setting up all"
	process_global_vars "$@" &&
	setup_radio &
	setup_api &
	setup_client &&
	setup_unit_test_env &&
	echo "done setting up all"
)

#assume install_setup.sh has been run
run_unit_tests() (
	echo "running unit tests"
	process_global_vars "$@"
	export __TEST_FLAG__='true'
	setup_unit_test_env >/dev/null &&
	test_src="$MC_SRC_PATH"/tests &&
	export MC_AUTH_SECRET_KEY=$(__get_mc_auth_key__) &&
	export PYTHONPATH="${MC_SRC_PATH}:${MC_SRC_PATH}/api" &&
	. "$(__get_app_root__)"/"$MC_APP_TRUNK"/"$MC_PY_ENV"/bin/activate &&
	cd "$test_src"
	pytest -s "$@" &&
	echo "done running unit tests"
)

debug_print() (
	msg="$1"
	if [ -n "$__DIAG_FLAG__" ]; then
		echo "$msg" >> diag_out_"$__INCLUDE_COUNT__"
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

__get_app_root__() (
	if [ -n "$__TEST_FLAG__" ]; then
		echo "$MC_TEST_ROOT"
		return
	fi
	echo "$MC_APP_ROOT"
)

get_web_root() (
	if [ -n "$__TEST_FLAG__" ]; then
		echo "$MC_TEST_ROOT"
		return
	fi
	case $(uname) in
		(Linux*)
			echo "${MC_WEB_ROOT_OVERRIDE:-/srv}"
			return
			;;
		(Darwin*)
			echo "${MC_WEB_ROOT_OVERRIDE:-/Library/WebServer}"
			return
			;;
		(*) ;;
	esac
)

connect_remote() (
	process_global_vars "$@" &&
	echo "connectiong to $(__get_address__) using $(__get_id_file__)" &&
	ssh -ti $(__get_id_file__) "root@$(__get_address__)" \
		$(__get_remote_export_script__) bash -l
)

connect_sftp() (
	process_global_vars "$@" >&2 &&
	sftp -6 -i $(__get_id_file__) "root@[$(__get_address__)]"
)

process_global_args() {
	#in case need to pass the args to a remote script. example
	__GLOBAL_ARGS__=''
	while [ ! -z "$1" ]; do
		case "$1" in
			#build out to test_trash rather than the normal directories
			#sets MC_APP_ROOT and MC_WEB_ROOT_OVERRIDE 
			#without having to set them explicitly
			(test)
				export __TEST_FLAG__='true'
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} test"
				;;
			(replace=*)
				export __REPLACE__=${1#replace=}
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} replace='${__REPLACE__}'"
				;;
			(clean) #tells setup functions to delete files/dirs before installing
				export __CLEAN_FLAG='clean'
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} clean"
				;;
			#activates debug_print. Also tells deploy script to use the diag branch
			(diag)
				export __DIAG_FLAG__='true'
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} diag"
				echo '' > diag_out_"$__INCLUDE_COUNT__"
				;;
			(setuplvl=*) #affects which setup scripst to run
				export __SETUP_LVL__=${1#setuplvl=}
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} setuplvl='${__SETUP_LVL__}'"
				;;
			#when I want to conditionally run with some experimental code
			(experiment=*)
				export __EXPERIMENT_NAME__=${1#experiment=}
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} experiment='${__EXPERIMENT_NAME__}'"
				;;
			(skip=*)
				export __SKIP__=${1#skip=}
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} skip='${__SKIP__}'"
				;;
			(icebranch=*)
				export __ICES_BRANCH__=${1#icebranch=}
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} icebranch='${__ICES_BRANCH__}'"
				;;
			(dbsetuppass=*)
				export __DB_SETUP_PASS__=${1#dbsetuppass=}
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} dbsetuppass='${__DB_SETUP_PASS__}'"
				;;
			(*) ;;
		esac
		shift
	done
	export __GLOBAL_ARGS__
}

define_consts() {
	[ -z "$__CONSTANTS_SET__" ] || return 0
	export MC_PACMAN_CONST='pacman'
	export MC_APT_CONST='apt-get'
	export MC_HOMEBREW_CONST='homebrew'
	export MC_CURRENT_USER=$(whoami)
	export MC_PROJ_NAME='musical_chairs'
	export MC_BUILD_DIR='builds'
	export MC_CONTENT_HOME='music/radio'
	export MC_BIN_DIR='.local/bin'
	export MC_API_PORT='8033'
	#python environment names
	export MC_PY_ENV='mc_env'
	export __CONSTANTS_SET__='true'
	echo "constants defined"
}

create_install_directory() {
	if [ -z "$MC_LOCAL_REPO_PATH" ]; then
		echo 'MC_LOCAL_REPO_PATH is set. '
		echo 'create_install_directory may have been run out of sequence'
		exit 1
	fi
	[ -d "$MC_LOCAL_REPO_PATH" ] ||
	mkdir -pv "$MC_LOCAL_REPO_PATH"
}

define_app_root_terms() {
	export MC_APP_ROOT=${MC_APP_ROOT:-"$HOME"}

	export sqliteFilename='songs_db.sqlite'
	export MC_APP_TRUNK="$MC_PROJ_NAME"_dir


	export MC_LIB_NAME="$MC_PROJ_NAME"_libs
	export MC_APP_NAME="$MC_PROJ_NAME"_app

	echo "top level terms defined"
}

define_app_dir_paths() {
	export MC_ICES_CONFIGS_DIR="$MC_APP_TRUNK"/ices_configs
	export MC_PY_MODULE_DIR="$MC_APP_TRUNK"/pyModules

	export MC_CONFIG_DIR="$MC_APP_TRUNK"/config
	export MC_DB_DIR="$MC_APP_TRUNK"/db
	export MC_SQLITE_FILEPATH="$MC_DB_DIR"/"$sqliteFilename"
	export MC_UTEST_ENV_DIR="$MC_TEST_ROOT"/utest

	# directories that should be cleaned upon changes
	# suffixed with 'cl' for 'clean'
	export MC_TEMPLATES_DIR_CL="$MC_APP_TRUNK"/templates
	export MC_SQL_SCRIPTS_DIR_CL="$MC_APP_TRUNK"/sql_scripts
	export MC_APP_API_PATH_CL=api/"$MC_APP_NAME"
	export MC_APP_CLIENT_PATH_CL=client/"$MC_APP_NAME"
	#MC_RADIO_LOG_DIR_CL may not be relevant anymore
	export MC_RADIO_LOG_DIR_CL="$MC_APP_TRUNK"/radio_logs

	echo "app dir paths defined and created"
}

__get_url_base__() (
	echo "$MC_PROJ_NAME" | tr -d _
)

__get_domain_name__() (
	envArg="$1"
	omitPort="$2"
	urlBase=$(__get_url_base__)
	case "$envArg" in
		(local*)
			if [ -n "$omitPort" ]; then
				urlSuffix='-local.radio.fm'
			else
				urlSuffix='-local.radio.fm:8080'
			fi
			;;
		(*)
			urlSuffix='.radio.fm'
			;;
	esac
	echo "${urlBase}${urlSuffix}"
)

__define_url__() {
	echo "env: ${MC_APP_ENV}"
	export MC_SERVER_NAME=$(__get_domain_name__ "$MC_APP_ENV")
	export MC_FULL_URL="https://${MC_SERVER_NAME}"
	echo "url defined"
}

define_repo_paths() {
	export MC_SRC_PATH="$(get_repo_path)/src"
	export MC_API_SRC="$MC_SRC_PATH/api"
	export MC_CLIENT_SRC="$MC_SRC_PATH/client"
	export MC_LIB_SRC="$MC_SRC_PATH/$MC_LIB_NAME"
	export MC_TEMPLATES_SRC="$(get_repo_path)/templates"
	export MC_SQL_SCRIPTS_SRC="$(get_repo_path)/sql_scripts"
	export MC_REFERENCE_SRC="$(get_repo_path)/reference"
	export MC_REFERENCE_SRC_DB="$MC_REFERENCE_SRC/$sqliteFilename"
	export MC_TEST_ROOT="$(get_repo_path)/test_trash"
	echo "source paths defined"
}

setup_app_directories() {
	[ -e "$(__get_app_root__)"/"$MC_APP_TRUNK" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_APP_TRUNK"
	[ -e "$(__get_app_root__)"/"$MC_CONFIG_DIR" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_CONFIG_DIR"
	[ -e "$(__get_app_root__)"/"$MC_ICES_CONFIGS_DIR" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_ICES_CONFIGS_DIR"
	[ -e "$(__get_app_root__)"/"$MC_PY_MODULE_DIR" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_PY_MODULE_DIR"
	[ -e "$(__get_app_root__)"/"$MC_DB_DIR" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_DB_DIR"
	[ -e "$(__get_app_root__)"/"$MC_RADIO_LOG_DIR_CL" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_RADIO_LOG_DIR_CL"
	[ -e "$(__get_app_root__)"/keys ] ||
	mkdir -pv "$(__get_app_root__)"/keys
	[ -e "$(__get_app_root__)"/"$MC_BUILD_DIR" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_BUILD_DIR"
	[ -e "$(__get_app_root__)"/"$MC_CONTENT_HOME" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_CONTENT_HOME"
}

setup_base_dirs() {

	setup_app_directories

	[ -e "$(get_web_root)"/"$MC_APP_API_PATH_CL" ] ||
	{
		sudo -p 'Pass required to create web server directory: ' \
			mkdir -pv "$(get_web_root)"/"$MC_APP_API_PATH_CL" ||
		show_err_and_exit "Could not create $(get_web_root)/${MC_APP_API_PATH_CL}"
	}
}

define_global_vars() {
	define_consts &&
	define_app_root_terms &&
	define_app_dir_paths &&
	__define_url__
}

define_directory_vars() {
	[ -z "$__DIRECTORY_VARS_SET__" ] || return 0
	export MC_LOCAL_REPO_PATH=$(get_repo_path) &&
	define_repo_paths
	export __DIRECTORY_VARS_SET__='true'
}


process_global_vars() {
	process_global_args "$@" || return
	[ -z "$__GLOBALS_SET__" ] || return 0

	define_global_vars &&
	define_directory_vars &&
	setup_base_dirs &&

	export __GLOBALS_SET__='globals'
}


unset_globals() {
	enable_wordsplitting
	exceptions=$(tr '\n' ' '<<-'EOF'
		MC_APP_ENV
		MC_AUTH_SECRET_KEY
		MC_DB_PASS_API
		MC_DB_PASS_OWNER
		MC_DB_PASS_RADIO
		MC_LOCAL_REPO_PATH
		MC_REPO_URL
		MC_SERVER_KEY_FILE
		MC_SERVER_SSH_ADDRESS
		__DB_SETUP_PASS__
	EOF
	)
	cat "$(get_repo_path)"/radio_common.sh | grep export \
		| sed -n -e 's/^\t*export \([a-zA-Z0-9_]\{1,\}\)=.*/\1/p' | sort -u \
		| while read constant; do
				#exceptions is unquoted on purpose
				if array_contains "$constant" $exceptions; then
					echo "leaving $constant"
					continue
				fi
				case "$constant" in
					(MC_*)
						echo "unsetting ${constant}"
						unset "$constant"
						;;
					(__*)
						echo "unsetting ${constant}"
						unset "$constant"
						;;
					(*)
						;;
					esac
			done
	disable_wordsplitting
}

fn_ls() (
	process_global_vars "$@" >/dev/null
	perl -ne 'print "$1\n" if /^([a-zA-Z_0-9]+)\(\)/' \
		"$(get_repo_path)"/radio_common.sh | sort
)
