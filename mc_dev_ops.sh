#!/bin/sh

[ -f "$HOME"/.profile ] && . "$HOME"/.profile >/dev/null
[ -f "$HOME"/.zprofile ] && . "$HOME"/.zprofile
[ -f "$HOME"/.zshrc ] && . "$HOME"/.zshrc

__INCLUDE_COUNT__=${__INCLUDE_COUNT__:-0}
__INCLUDE_COUNT__=$((__INCLUDE_COUNT__ + 1))
export __INCLUDE_COUNT__


install_package() (
	pkgName="$1"
	echo "Try to install --${pkgName}--"
	case $(uname) in #()
		(Linux*)
			if which pacman >/dev/null 2>&1; then
				yes | sudo -p 'Pass required for pacman install: ' \
					pacman -S "$pkgName"
			elif which apt-get >/dev/null 2>&1; then
				sudo -p 'Pass required for apt-get install: ' \
					DEBIAN_FRONTEND=noninteractive apt-get -y install "$pkgName"
			fi
			;; #()
		(Darwin*)
			yes | brew install "$pkgName"
			;; #()
		(*)
			;;
	esac
)


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
	case "$haystackStr" in #()
		(*"$needleStr"*)
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
		case $1 in #()
			("$searchValue")
				return 0
				;; #()
			(*)
			;;
		esac
		shift
	done
	return 1
)


is_dir_empty() (
	targetDir="$1"
	lsRes=$(ls -A $targetDir)
	[ ! -d "$targetDir" ] || [ -z "$lsRes" ]
)


error_check_path() (
	targetDir="$1"
	if echo "$targetDir" | grep '\/\/'; then
		echo "segments seem to be missing in '${targetDir}'"
		return 1
	elif [ "$targetDir" = '/' ];then
		echo "segments seem to be missing in '${targetDir}'"
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


empty_dir_contents() (
	dirEmptira="$1"
	echo "emptying '${dirEmptira}'"
	error_check_path "$dirEmptira" &&
	if [ -e "$dirEmptira" ]; then
		rm_contents_if_exist || return "$?"
	else
		sudo_mkdir "$dirEmptira" || return "$?"
	fi &&
	echo "done emptying '${dirEmptira}'"
)


get_bin_path() (
	pkg="$1"
	case $(uname) in #()
		(Darwin*)
			brew info "$pkg" \
			| grep -A1 'has been installed as' \
			| awk 'END{ print $1 }'
			;; #()
		(*) which "$pkg" ;;
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


show_err_and_return() {
	errCode="$?"
	msg="$1"
	[ ! -z "$msg" ] && echo "$msg"
	return "$errCode"
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


unroot_dir() (
	dirUnrootura="$1"
	if [ ! -w "$dirUnrootura" ]; then
		prompt='Password required to change owner of'
		prompt="${prompt} ${dirUnrootura} to current user: "
		sudo -p "$prompt" \
			chown -R "$MC_CURRENT_USER": "$dirUnrootura"
	fi
)


gen_pass() (
	pass_len=${1:-16}
	LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c "$pass_len"
)


is_ssh() (
	[ -n "$SSH_CONNECTION" ]
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


set_env_vars() {
	process_global_vars "$@" &&
	__set_env_path_var__
}


get_localhost_ssh_dir() (
	case $(uname) in #()
		(Darwin*)
			echo "$HOME"/.ssh
			;; #()
		(Linux*)
			echo "$HOME"/.ssh
			;; #()
		(*) ;;
	esac
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


is_python_version_good() {
	[ "$__EXPERIMENT_NAME__" = 'py3.8' ] && return 0
	set_python_version_const &&
	[ "$pyMajor" -eq 3 ] && [ "$pyMinor" -ge 9 ]
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


get_icecast_name() (
	pkgMgrChoice="$1"
	case "$pkgMgrChoice" in #()
    ("$MC_PACMAN_CONST") echo 'icecast';; #()
    ("$MC_APT_CONST") echo 'icecast2';; #()
    (*) echo 'icecast2';;
	esac
)


is_ices_version_good() {
	set_ices_version_const &&
	[ "$icesMajor" -ge 0 ] && [ "$icesMinor" -ge 6 ] && [ "$icesPatch" -ge 1 ]
}

install_ices_unchecked() (
	set_env_vars "$@" &&
	shutdown_all_stations &&
	sh "$(get_repo_path)"/compiled_dependencies/build_ices.sh "$__ICES_BRANCH__"
)


install_ices() (
	set_env_vars "$@" &&
	if ! mc-ices -V 2>/dev/null || ! is_ices_version_good; then
		install_ices_unchecked
	fi
)


start_icecast_service() (
	echo 'starting icecast service'
	icecastName="$1"
	case $(uname) in #()
		(Linux*)
			if ! systemctl is-active --quiet "$icecastName"; then
				sudo -p "enabling ${icecastName}" systemctl enable "$icecastName"
				sudo -p "starting ${icecastName}" systemctl start "$icecastName"
			fi
			;; #()
		(*) ;;
	esac &&
	echo 'done starting icecast service'
)


get_icecast_conf() (
	icecastName="$1"
	case $(uname) in #()
		(Linux*)
			if ! systemctl status "$icecastName" >/dev/null 2>&1; then
					echo "$icecastName is not running at the moment"
					exit 1
			fi
				systemctl status "$icecastName" | grep -A2 CGroup | \
					head -n2 | tail -n1 | awk '{ print $NF }'
			;; #()
		(Darwin*)
			#we don't have icecast on the mac anyway so we'll just return the
			#source code location
			echo "$MC_TEMPLATES_SRC"/icecast.xml
			;; #()
		(*) ;;
	esac
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


show_icecast_log() (
	process_global_vars "$@" >/dev/null 2>&1 &&
	__install_py_env_if_needed__ >/dev/null 2>&1 &&
	. "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate >/dev/null \
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
	. "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate >/dev/null \
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


__update_ices_config__() (
	conf="$1"
	sourcePassword="$2"
	perl -pi -e "s/>\w*/>${sourcePassword}/ if /Password/" "$conf"
)


update_ices_config() (
	conf="$1"
	process_global_vars "$@"
	__install_py_env_if_needed__ >/dev/null 2>&1 &&
	. "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate >/dev/null \
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


__is_current_dir_repo__() {
	dir="$1"
	[ -f "$dir"/dev_ops.sh ] &&
	[ -f "$dir"/README.md ] &&
	[ -f "$dir"/deploy_to_server.sh ] &&
	[ -d "$dir"/.vscode ] &&
	[ -d "$dir"/src ] &&
	[ -d "$dir"/src/musical_chairs ]
}


get_pkg_mgr() {
	define_consts >&2
	case $(uname) in #()
		(Linux*)
			if  which pacman >/dev/null 2>&1; then
				echo "$MC_PACMAN"
				return 0
			elif which apt-get >/dev/null 2>&1; then
				echo "$MC_APT_CONST"
				return 0
			fi
			;; #()
		(Darwin*)
			echo "$MC_HOMEBREW"
			return 0
			;; #()
		(*)
			;;
	esac
	return 1
}


brew_is_installed() (
	pkg="$1"
	echo "checking about $pkg"
	case $(uname) in #()
		(Darwin*)
			brew info "$pkg" >/dev/null 2>&1 &&
			! brew info "$pkg" | grep 'Not installed' >/dev/null
			;; #()
		(*) return 0 ;;
	esac
)


track_exit_code() {
	exitCode="$?"
	if [ -z "$fnExitCode" ]; then
		fnExitCode="$exitCode"
	fi
	((exit "$fnExitCode") && (exit "$exitCode"))
	fnExitCode="$?"
	return "$exitCode"
}


__deployment_env_check_recommended__() {
	#possibly problems if missing

	[ -n "$(__get_ices_branch__)" ] ||
	echo 'environmental var __ICES_BRANCH__ not set'
	# reading MC_LOCAL_REPO_DIR from env vars
	# instead of keys because I don't want to accidenly
	# replace what is on server.
	# Server needs its own MC_LOCAL_REPO_DIR
	[ -n "$MC_LOCAL_REPO_DIR" ] ||
	echo 'environmental var MC_LOCAL_REPO_DIR not set'
	[ -n "$(__get_db_setup_key__)" ] ||
	echo 'deployment var __DB_SETUP_PASS__ not set in keys'
	[ -n "$(__get_db_owner_key__)" ] ||
	echo 'deployment var MC_DB_PASS_OWNER not set in keys'
}


__deployment_env_check_required__() {
	#definitely problems if missing
	keyFile="$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
	echo "key file: ${keyFile}"
	if [ ! -s "$keyFile" ]; then
		echo "key file not setup. ${keyFile}"
		return 1
	fi
	[ -n "$MC_REPO_URL" ] ||
	echo 'environmental var MC_REPO_URL not set'
	fnExitCode="$?"

	track_exit_code
	[ -n "$(__get_domain_name__)" ]
	track_exit_code ||
	echo 'top level domain for app has not been set. Check __get_domain_name__'

	#values for ssh'ing to server
	[ -n "$(__get_id_file__)" ]
	track_exit_code ||
	echo 'deployment var MC_SERVER_KEY_FILE not set in keys'
	[ -n "$(__get_address__)" ]
	track_exit_code ||
	echo 'deployment var MC_SERVER_SSH_ADDRESS not set in keys'

	#porkbun
	[ -n "$(__get_pb_api_key__)" ]
	track_exit_code ||
	echo 'deployment var PB_API_KEY not set in keys'
	[ -n "$(__get_pb_secret__)" ]
	track_exit_code ||
	echo 'deployment var PB_SECRET not set in keys'

	#for encrypting app token
	[ -n "$(__get_api_auth_key__)" ]
	track_exit_code ||
	echo 'deployment var MC_AUTH_SECRET_KEY not set in keys'
	[ -n "$(__get_namespace_uuid__)" ]
	track_exit_code ||
	echo 'deployment var MC_NAMESPACE_UUID not set in keys'

	#s3
	[ -n "$(__get_s3_api_key__)" ]
	track_exit_code ||
	echo 'deployment var AWS_ACCESS_KEY_ID not set in keys'
	[ -n "$(__get_s3_secret__)" ]
	track_exit_code ||
	echo 'deployment var AWS_SECRET_ACCESS_KEY not set in keys'
	[ -n "$(__get_s3_bucket_name__)" ]
	track_exit_code ||
	echo 'deployment var S3_BUCKET_NAME not set in keys'
	[ -n "$(__get_s3_region_name__)" ]
	track_exit_code ||
	echo 'deployment var S3_REGION_NAME not set in keys'
	[ -n "$(__get_s3_endpoint__)" ]
	track_exit_code ||
	echo 'deployment var AWS_ENDPOINT_URL not set in keys'

	#db
	[ -n "$(__get_api_db_user_key__)" ]
	track_exit_code ||
	echo 'deployment var MC_DB_PASS_API not set in keys'
	[ -n "$(__get_radio_db_user_key__)" ]
	track_exit_code ||
	echo 'deployment var MC_DB_PASS_RADIO not set in keys'
	return "$fnExitCode"
}


deployment_env_check() (
	echo 'checking environment vars before deployment'
	define_consts >&2
	__deployment_env_check_recommended__
	__deployment_env_check_required__
)


__server_env_check_recommended__() {
	#possibly problems if missing
	[ -n "$__ICES_BRANCH__" ] ||
	echo 'environmental var __ICES_BRANCH__ not set'
	[ -n "$__DB_SETUP_PASS__" ] ||
	echo 'environmental var __DB_SETUP_PASS__ not set in keys'
	[ -n "$MC_DB_PASS_OWNER" ] ||
	echo 'environmental var MC_DB_PASS_OWNER not set in keys'
}


__server_env_check_required__() {
	#definitely problems if missing
	[ -n "$MC_REPO_URL" ]
	fnExitCode="$?"
	track_exit_code ||
	echo 'environmental var MC_REPO_URL not set'
	[ -n "$MC_LOCAL_REPO_DIR" ] ||
	echo 'environmental var MC_LOCAL_REPO_DIR not set'

	#__get_domain_name__ is not based on env variables,
	#but we want to ensure it's building okay
	[ -n "$(__get_domain_name__)" ]
	track_exit_code ||
	echo 'top level domain for app has not been set. Check __get_domain_name__'

	#porkbun
	[ -n "$PB_API_KEY" ]
	track_exit_code ||
	echo 'environmental var PB_API_KEY not set'
	[ -n "$PB_SECRET" ]
	track_exit_code ||
	echo 'environmental var PB_SECRET not set'

	#for encrypting app token
	[ -n "$MC_AUTH_SECRET_KEY" ]
	track_exit_code ||
	echo 'environmental var MC_AUTH_SECRET_KEY not set'
	[ -n "$MC_NAMESPACE_UUID" ]
	track_exit_code ||
	echo 'environmental var MC_NAMESPACE_UUID not set in keys'

	#s3
	[ -n "$AWS_ACCESS_KEY_ID" ]
	track_exit_code ||
	echo 'environmental var AWS_ACCESS_KEY_ID not set'
	[ -n "$AWS_SECRET_ACCESS_KEY" ]
	track_exit_code ||
	echo 'environmental var AWS_SECRET_ACCESS_KEY not set'
	[ -n "$S3_BUCKET_NAME" ]
	track_exit_code ||
	echo 'environmental var S3_BUCKET_NAME not set'
	[ -n "$S3_REGION_NAME" ]
	track_exit_code ||
	echo 'environmental var S3_REGION_NAME not set'
	[ -n "$AWS_ENDPOINT_URL" ]
	track_exit_code ||
	echo 'environmental var AWS_ENDPOINT_URL not set'

	#db
	[ -n "$MC_DB_PASS_API" ]
	track_exit_code ||
	echo 'environmental var MC_DB_PASS_API not set'
	[ -n "$MC_DB_PASS_RADIO" ]
	track_exit_code ||
	echo 'environmental var MC_DB_PASS_RADIO not set'
	return "$fnExitCode"
}

server_env_check() (
	echo 'checking environment vars on server'
	define_consts >&2
	__server_env_check_recommended__
	__server_env_check_required__
)


__dev_env_check_recommended__() {
	#possibly problems if missing
	[ -n "$MC_REPO_URL" ] ||
	echo 'environmental var MC_REPO_URL not set'
	[ -n "$__DB_SETUP_PASS__" ] ||
	echo 'environmental var __DB_SETUP_PASS__ not set in keys'
	[ -n "$MC_DB_PASS_OWNER" ] ||
	echo 'environmental var MC_DB_PASS_OWNER not set in keys'
}


__dev_env_check_required__() {
	#definitely problems if missing
	[ -n "$MC_LOCAL_REPO_DIR" ]
	fnExitCode="$?"
	track_exit_code ||
	echo 'environmental var MC_LOCAL_REPO_DIR not set'

	[ -n "$(__get_domain_name__)" ]
	track_exit_code ||
	echo 'top level domain for app has not been set. Check __get_domain_name__'

	[ -n "$MC_ENV" ]
	track_exit_code ||
	echo 'environmental var MC_ENV not set'
	#db
	[ -n "$MC_DB_PASS_API" ]
	track_exit_code ||
	echo 'environmental var MC_DB_PASS_API not set'

		#s3
	[ -n "$(__get_s3_api_key__)" ]
	track_exit_code ||
	echo 'environmental var AWS_ACCESS_KEY_ID not set in keys'
	[ -n "$(__get_s3_secret__)" ]
	track_exit_code ||
	echo 'environmental var AWS_SECRET_ACCESS_KEY not set in keys'
	[ -n "$(__get_s3_bucket_name__)" ]
	track_exit_code ||
	echo 'environmental var S3_BUCKET_NAME not set in keys'
	[ -n "$(__get_s3_region_name__)" ]
	track_exit_code ||
	echo 'environmental var S3_REGION_NAME not set in keys'
	[ -n "$(__get_s3_endpoint__)" ]
	track_exit_code ||
	echo 'environmental var AWS_ENDPOINT_URL not set in keys'

	#for encrypting app token
	[ -n "$MC_AUTH_SECRET_KEY" ]
	track_exit_code ||
	echo 'environmental var MC_AUTH_SECRET_KEY not set'
	[ -n "$MC_NAMESPACE_UUID" ]
	track_exit_code ||
	echo 'environmental var MC_NAMESPACE_UUID not set in keys'

	return "$fnExitCode"
}


dev_env_check() (
	echo 'checking environment vars on local dev environment'
	define_consts >&2
	__dev_env_check_recommended__
	__dev_env_check_required__
)


get_repo_path() (
	if [ -n "$MC_LOCAL_REPO_DIR" ]; then
		echo "$MC_LOCAL_REPO_DIR"
		return
	elif __is_current_dir_repo__ "$PWD"; then
		echo "$PWD"
		return
	else
		for guess in \
			$(find "$HOME" -maxdepth 5 -type d \
				-path "$MC_BUILD_DIR"/"$MC_PROJ_NAME_SNAKE"
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
	echo "$HOME"/"$MC_BUILD_DIR"/"$MC_PROJ_NAME_SNAKE"
)


__set_env_path_var__() {
	if perl -e "exit 1 if index('$PATH','$(__get_app_root__)/${MC_BIN_DIR}') != -1";
	then
		echo "Please add '$(__get_app_root__)/${MC_BIN_DIR}' to path"
		export PATH="$PATH":"$(__get_app_root__)"/"$MC_BIN_DIR"
	fi
}


__get_ices_branch__() (
	if [ -n "$__ICES_BRANCH__" ]; then
		echo "$__ICES_BRANCH__"
		return
	fi
)


__get_pb_api_key__() (
	if [ -n "$PB_API_KEY" ] && [ "$MC_ENV" != 'local' ]; then
		echo "$PB_API_KEY"
		return
	fi
	perl -ne 'print "$1\n" if /PB_API_KEY=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_pb_secret__() (
	if [ -n "$PB_SECRET" ] && [ "$MC_ENV" != 'local' ]; then
		echo "$PB_SECRET"
		return
	fi
	perl -ne 'print "$1\n" if /PB_SECRET=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_s3_api_key__() (
	if [ -n "$AWS_ACCESS_KEY_ID" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$AWS_ACCESS_KEY_ID"
		return
	fi
	perl -ne 'print "$1\n" if /AWS_ACCESS_KEY_ID=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_s3_secret__() (
	if [ -n "$AWS_SECRET_ACCESS_KEY" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$AWS_SECRET_ACCESS_KEY"
		return
	fi
	perl -ne 'print "$1\n" if /AWS_SECRET_ACCESS_KEY=([\w\/\+]+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_s3_bucket_name__() (
	if [ -n "$S3_BUCKET_NAME" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$S3_BUCKET_NAME"
		return
	fi
	perl -ne 'print "$1\n" if /S3_BUCKET_NAME=([\w\-]+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_s3_region_name__() (
	if [ -n "$S3_REGION_NAME" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$S3_REGION_NAME"
		return
	fi
	perl -ne 'print "$1\n" if /S3_REGION_NAME=([\w\-]+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_s3_endpoint__() (
	if [ -n "$AWS_ENDPOINT_URL" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$AWS_ENDPOINT_URL"
		return
	fi
	perl -ne 'print "$1\n" if /AWS_ENDPOINT_URL=(.+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_api_auth_key__() (
	if [ -n "$MC_AUTH_SECRET_KEY" ] && [ "$MC_ENV" != 'local' ]; then
		echo "$MC_AUTH_SECRET_KEY"
		return
	fi
	perl -ne 'print "$1\n" if /MC_AUTH_SECRET_KEY=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_namespace_uuid__() (
	if [ -n "$MC_NAMESPACE_UUID" ] && [ "$MC_ENV" != 'local' ]; then
		echo "$MC_NAMESPACE_UUID"
		return
	fi
	perl -ne 'print "$1\n" if /MC_NAMESPACE_UUID=([\w\-]+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_address__() (
	if [ -n "$MC_SERVER_SSH_ADDRESS" ]; then
		echo "$MC_SERVER_SSH_ADDRESS"
		return
	fi
	keyFile="$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
	perl -ne 'print "$1\n" if /MC_SERVER_SSH_ADDRESS=root@([\w:]+)/' "$keyFile"
)


__get_id_file__() (
	if [ -n "$MC_SERVER_KEY_FILE" ]; then
		echo "$MC_SERVER_KEY_FILE"
		return
	fi
	keyFile="$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
	perl -ne 'print "$1\n" if /MC_SERVER_KEY_FILE=(.+)/' "$keyFile"
)

__get_db_setup_key__() (
	if [ -n "$__DB_SETUP_PASS__" ] && [ "$MC_ENV" != 'local' ]; then
		echo "$__DB_SETUP_PASS__"
		return
	fi
	perl -ne 'print "$1\n" if /__DB_SETUP_PASS__=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_db_owner_key__() (
	if [ -n "$MC_DB_PASS_OWNER" ] && [ "$MC_ENV" != 'local' ]; then
		echo "$MC_DB_PASS_OWNER"
		return
	fi
	perl -ne 'print "$1\n" if /MC_DB_PASS_OWNER=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)

__get_api_db_user_key__() (
	if [ -n "$MC_DB_PASS_API" ] && [ "$MC_ENV" != 'local' ]; then
		echo "$MC_DB_PASS_API"
		return
	fi
	perl -ne 'print "$1\n" if /MC_DB_PASS_API=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_radio_db_user_key__() (
	if [ -n "$MC_DB_PASS_RADIO" ] && [ "$MC_APP_ENV" != 'local' ]; then
		echo "$MC_DB_PASS_RADIO"
		return
	fi
	perl -ne 'print "$1\n" if /MC_DB_PASS_RADIO=(\w+)/' \
		"$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
)


__get_remote_private_key__() (
	echo "/etc/ssl/private/${MC_PROJ_NAME_SNAKE}.private.key.pem"
)


__get_remote_public_key__() (
	echo "/etc/ssl/certs/${MC_PROJ_NAME_SNAKE}.public.key.pem"
)


__get_remote_intermediate_key__() (
	echo "/etc/ssl/certs/${MC_PROJ_NAME_SNAKE}.intermediate.key.pem"
)


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
	env_root=${1:-"$(__get_app_root__)"/"$MC_TRUNK"}
	pyEnvDir="$env_root"/"$MC_PY_ENV"
	error_check_path "$pyEnvDir" &&
	mc-python -m virtualenv "$pyEnvDir" &&
	. "$pyEnvDir"/bin/activate &&
	#this is to make some of my newer than checks work
	touch "$pyEnvDir" &&
	# #python_env
	# use regular python command rather mc-python
	# because mc-python still points to the homebrew location
	python -m pip install -r "$(__get_app_root__)"/"$MC_TRUNK"/requirements.txt &&
	echo "done setting up py libs"
)


create_py_env_in_app_trunk() (
	process_global_vars "$@" &&
	sync_requirement_list &&
	create_py_env_in_dir &&
	__replace_lib_files__
)


get_libs_dest_dir() (
	__set_env_path_var__ >&2 #ensure that we can see mc-python
	set_python_version_const || return "$?"
	envRoot="$1"
	packagePath="${MC_PY_ENV}/lib/python${pyMajor}.${pyMinor}/site-packages/"
	echo "$envRoot"/"$packagePath"
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


__replace_lib_files__() {
	envRoot="$(__get_app_root__)"/"$MC_TRUNK"
	regen_file_reference_file &&
	copy_dir "$MC_LIB_SRC" \
		"$(get_libs_dest_dir "$envRoot")""$MC_LIB"
	copy_dir "$MC_DEV_OPS_LIB_SRC" \
		"$(get_libs_dest_dir "$envRoot")""$MC_DEV_OPS_LIB"
}


__install_py_env_if_needed__() {
	if [ ! -e "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate ]; then
		__install_py_env__
	else
		echo "replacing musical_chairs files"
		__replace_lib_files__ >/dev/null #only replace my code
	fi
}


activate_mc_env() {
	if [ -n "$VIRTUAL_ENV" ]; then
		deactivate 2>&1 1>/dev/null
	fi
	set_env_vars "$@" &&
	__install_py_env_if_needed__ &&
	. "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate
}


start_python() (
	activate_mc_env &&
	python
)


link_app_python_if_not_linked() {
	if ! mc-python -V 2>/dev/null; then
		if [ ! -e "$(__get_app_root__)"/"$MC_BIN_DIR" ]; then
			sudo_mkdir "$(__get_app_root__)"/"$MC_BIN_DIR" || return "$?"
		fi
		case $(uname) in #()
			(Darwin*)
				ln -sf $(get_bin_path python@3.9) \
					"$(__get_app_root__)"/"$MC_BIN_DIR"/mc-python
				;; #()
			(*)
				ln -sf $(get_bin_path python3) \
					"$(__get_app_root__)"/"$MC_BIN_DIR"/mc-python
				;;
		esac
	fi
	echo "done linking"
}


copy_lib_to_test() (
	process_global_vars "$@" &&
	copy_dir "$MC_LIB_SRC" \
		"$(get_libs_dest_dir "$MC_UTEST_ENV_DIR")"/"$MC_LIB"
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
		"s@^(MC_CONTENT_DIR=).*\$@\1'${MC_CONTENT_DIR}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_TEMPLATES_DEST=).*\$@\1'${MC_TEMPLATES_DEST}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(MC_SQL_SCRIPTS_DEST=).*\$@\1'${MC_SQL_SCRIPTS_DEST}'@" \
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
	perl -pi -e \
		"s@^(MC_NAMESPACE_UUID=).*\$@\1'${MC_NAMESPACE_UUID}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(AWS_ACCESS_KEY_ID=).*\$@\1'${AWS_ACCESS_KEY_ID}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(AWS_SECRET_ACCESS_KEY=).*\$@\1'${AWS_SECRET_ACCESS_KEY}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(S3_BUCKET_NAME=).*\$@\1'${S3_BUCKET_NAME}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(S3_REGION_NAME=).*\$@\1'${S3_REGION_NAME}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(AWS_ENDPOINT_URL=).*\$@\1'${AWS_ENDPOINT_URL}'@" \
		"$envFile" &&
	echo 'done setting up .env file'
)


start_db_service() (
	echo 'starting database service'
	case $(uname) in #()
		(Linux*)
			if ! systemctl is-active --quiet mariadb; then
				sudo -p 'enabling mariadb' 'systemctl enable mariadb'
				sudo -p 'starting mariadb' 'systemctl start mariadb'
			fi
			;; #()
		(Darwin*)
			status=brew services list | grep mariadb | awk '{ print $2 }'
			if [ status = 'none' ]; then
				brew services start mariadb
			fi
			;; #()
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
	__replace_sql_script__ &&
	__install_py_env_if_needed__ &&
	. "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate &&
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
	setup_database
)
dbName="musical_chairs_db"
setup_database(dbName)

EOF
	)
echo 'done with initial db setup'
)


teardown_database() (
	echo 'tearing down db'
	process_global_vars "$@" >/dev/null 2>&1 &&
	__install_py_env_if_needed__ >/dev/null 2>&1 &&
	. "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate \
		>/dev/null 2>&1 &&
	(python <<EOF
from musical_chairs_libs.services import (
	DbRootConnectionService,
	DbOwnerConnectionService
)

with DbRootConnectionService() as rootConnService:
	rootConnService.drop_all_users()
	rootConnService.drop_database("musical chairs_db")

EOF
	)
	echo "Done tearing down db"
)

sync_utility_scripts() (
	process_global_vars "$@" &&
	cp "$(get_repo_path)"/mc_dev_ops.sh "$(__get_app_root__)"/mc_dev_ops.sh
)


#copy python dependency file to the deployment directory
sync_requirement_list() (
	process_global_vars "$@" &&
	error_check_all_paths "$(get_repo_path)"/requirements.txt \
		"$(__get_app_root__)"/"$MC_TRUNK"/requirements.txt \
		"$(__get_app_root__)"/requirements.txt &&
	#keep a copy in the parent radio directory
	cp "$(get_repo_path)"/requirements.txt \
		"$(__get_app_root__)"/"$MC_TRUNK"/requirements.txt &&
	cp "$(get_repo_path)"/requirements.txt "$(__get_app_root__)"/requirements.txt
)


run_initial_install() (
	process_global_vars "$@" &&
	__setup_api_dir__
	sh $(get_repo_path)/install.sh
)


__get_debug_cert_name__() (
	echo "$MC_PROJ_NAME_SNAKE"_localhost_debug
)


__get_debug_cert_path__() (
	echo $(get_localhost_ssh_dir)/$(__get_debug_cert_name__)
)


__get_local_nginx_cert_name__() (
	echo "$MC_PROJ_NAME_SNAKE"_localhost_nginx
)


__get_local_nginx_cert_path__() (
	echo $(get_localhost_ssh_dir)/$(__get_local_nginx_cert_name__)
)


is_cert_expired() (
	! openssl x509 -checkend 3600 -noout >/dev/null
)


extract_sha256_from_cert() (
	openssl x509 -fingerprint -sha256 \
	| perl -ne 'print "$1\n" if /(?:SHA|sha)256 Fingerprint=([A-F0-9:]+)/' \
	| tr -d ':'
)


extract_commonName_from_cert() (
	openssl x509 -subject \
	| perl -ne 'print "$1\n" if m{CN *= *([^/]+)}'
)


scan_pems_for_common_name() (
	commonName="$1"
	activate_mc_env &&
	python -m 'musical_chairs_dev_ops.installed_certs' "$commonName" \
		< /etc/ssl/certs/ca-certificates.crt
)


certs_matching_name() (
	commonName="$1"
		case $(uname) in #()
		(Darwin*)
			security find-certificate -a -p -c "$commonName" \
				$(__get_keychain_osx__)
			;; #()
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
	case $(uname) in #()
		(Darwin*)
			echo '/System/Library/OpenSSL/openssl.cnf'
			;; #()
		(Linux*)
			echo '/etc/ssl/openssl.cnf'
			;; #()
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
	certName="$2" &&
	echo "Clean up certs for ${commonName} if needed"
	case $(uname) in #()
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
							-Z "$sha256Value" -t $(__get_keychain_osx__) ||
						echo "Failed to delete for sha256: ${sha256Value}"
						cert=''
					fi
				done
			;; #()
		(*)
				cert=''
				#turns out the d flag is not posix compliant :<
				scan_pems_for_common_name "$commonName" \
					| while read line; do
						cert=$(printf "%s\n%s" "$cert" "$line")
						if [ "$line" = '-----END CERTIFICATE-----' ]; then
							echo "$cert" | is_cert_expired &&
							{
								certDir='/usr/local/share/ca-certificates'
								if [ -z "$certName" ]; then
									certName="$commonName"
								fi
								sudo -p \
									"Need pass to delete from ${certDir}" \
									rm "$certDir"/"$certName"*.crt;
								sudo update-ca-certificates
							}
							cert=''
						fi
					done
			;;
	esac
	echo 'Done cleaning up certs'
	return 0
)


__setup_ssl_cert_local__() (
	commonName="$1"
	domain="$2" &&
	publicKeyFile="$3" &&
	privateKeyFile="$4" &&

	case $(uname) in #()
		(Darwin*)
			__openssl_gen_cert__ "$commonName" "$domain" \
				"$publicKeyFile" "$privateKeyFile" &&
			__install_local_cert_osx__ "$publicKeyFile" ||
			return 1
			;; #()
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
	__clean_up_invalid_cert__ "${MC_APP}-localhost"
	__setup_ssl_cert_local__ "${MC_APP}-localhost" 'localhost' \
		"$publicKeyFile" "$privateKeyFile"
	publicKeyName=$(__get_debug_cert_name__).public.key.crt &&
	__set_firefox_cert_policy__ "$publicKeyName" &&
	setup_react_env_debug
)


print_ssl_cert_info() (
	process_global_vars "$@" &&
	domain=$(__get_domain_name__ "$MC_ENV" 'omitPort') &&
	echo "$domain"
	case "$MC_ENV" in #()
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
				certs_matching_name "${MC_APP}-localhost" \
					| while read line; do
						cert=$(printf "%s\n%s" "$cert" "$line")
						if [ "$line" = '-----END CERTIFICATE-----' ]; then
							sha256Value=$(echo "$cert" | extract_sha256_from_cert) &&
							echo "$cert" | openssl x509 -enddate -subject -noout
							cert=''
						fi
					done
			;; #()
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
	domain=$(__get_domain_name__ "$MC_ENV" 'omitPort') &&
	echo "setting up certs for ${domain}"
	case "$MC_ENV" in #()
		(local*)
			add_test_url_to_hosts "$domain"
			publicKeyFile=$(__get_local_nginx_cert_path__).public.key.crt &&
			privateKeyFile=$(__get_local_nginx_cert_path__).private.key.pem &&

			# we\'re leaving off the && because what would that even mean here?
			__clean_up_invalid_cert__ "$domain" $(__get_local_nginx_cert_name__)
			if [ -z $(__certs_matching_name_exact__ "$domain") ]; then
				echo 'setting up new certs'
				__setup_ssl_cert_local__ \
				"$domain" "$domain" "$publicKeyFile" "$privateKeyFile"
			fi
			publicKeyName=$(__get_local_nginx_cert_name__).public.key.crt &&
			__set_firefox_cert_policy__ "$publicKeyName"
			;; #()
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
	echo "Done setting up certificates for ${domain}"
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
		sed 's/.*=\(.*\)/\1/' ||
		show_err_and_return "."
)


get_nginx_conf_dir_include() (
	nginxConf=$(get_nginx_value) &&
	guesses=$(cat<<-'EOF'
		include /etc/nginx/sites-enabled/*;
		include servers/*;
	EOF
	) &&
	#determine which one of these locations is referenced in the nginx config
	echo "$guesses" | while read guess; do
		if grep -F "$guess" "$nginxConf" >/dev/null; then
			echo "$guess"
			break
		fi
	done ||
	echo "failed while searching for nginx config"
)


__copy_and_update_nginx_template__() {
	sudo -p 'copy nginx config' \
		cp "$MC_TEMPLATES_SRC"/nginx_template.conf "$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e \
			"s@<MC_CLIENT_DEST>@$(get_web_root)/${MC_CLIENT_DEST}@" \
			"$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<MC_SERVER_NAME>@${MC_SERVER_NAME}@g" "$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<MC_API_PORT>@${MC_API_PORT}@" "$appConfFile"
}


__set_local_nginx_app_conf__() {
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
}


__set_deployed_nginx_app_conf__() {
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
}


update_nginx_conf() (
	echo 'updating nginx site conf'
	appConfFile="$1"
	error_check_all_paths "$MC_TEMPLATES_SRC" "$appConfFile" &&
	__copy_and_update_nginx_template__ &&
	case "$MC_ENV" in #()
		(local*)
			__set_local_nginx_app_conf__
			;; #()
		(*)
			__set_deployed_nginx_app_conf__
			;;
	esac &&
	echo 'done updating nginx site conf'
)


get_abs_path_from_nginx_include() (
	confDirInclude="$1"
	confDir=$(echo "$confDirInclude" | sed 's/include *//' | \
		sed 's@/\*; *@@')
	#test if already exists as absolute path
	if [ -d "$confDir" ]; then
		echo "$confDir"
		return
	else
		configPath=$(get_nginx_value) ||
		show_err_and_return "Had issues pulling nginx config path"
		sitesFolderPath=$(dirname "$configPath")
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
	configPath=$(get_nginx_value) &&
	#uncomment line if necessary in config
	sudo -p "Enable ${confDirInclude}" \
		perl -pi -e "s/^[ \t]*#// if m@$escapedGuess@" "$configPath" &&
	echo 'done enabling nginx site confs' ||
	echo 'failed to enable nginx site confs'
)


restart_nginx() (
	echo 'starting/restarting up nginx'
	case $(uname) in #()
		(Darwin*)
			nginx -s reload
			;; #()
		(Linux*)
			if systemctl is-active --quiet nginx; then
				sudo -p 'starting nginx. Need pass:' systemctl restart nginx
			else
				sudo -p 'enabling nginx. Need pass:' systemctl enable nginx
				sudo -p 'restarting nginx. Need pass:' systemctl start nginx
			fi
			;; #()
		(*) ;;
	esac &&
	echo 'Done starting/restarting up nginx'
)


refresh_certs() (
	setup_ssl_cert_nginx &&
	restart_nginx
)


print_nginx_conf_location() (
	process_global_vars "$@" >/dev/null &&
	confDirInclude=$(get_nginx_conf_dir_include) &&
	confDir=$(get_abs_path_from_nginx_include "$confDirInclude") 2>/dev/null
	echo "$confDir"/"$MC_APP".conf
)


print_cert_paths() (
	process_global_vars "$@" >/dev/null &&
	confDirInclude=$(get_nginx_conf_dir_include) &&
	confDir=$(get_abs_path_from_nginx_include "$confDirInclude") 2>/dev/null
	cat "$confDir"/"$MC_APP".conf | perl -ne \
	'print "$1\n" if /ssl_certificate ([^;]+)/'
	cat "$confDir"/"$MC_APP".conf | perl -ne \
	'print "$1\n" if /ssl_certificate_key ([^;]+)/'
	cat "$confDir"/"$MC_APP".conf | perl -ne \
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
	update_nginx_conf "$confDir"/"$MC_APP".conf &&
	sudo -p 'Remove default nginx config' \
		rm -f "$confDir"/default &&
	restart_nginx &&
	echo "done setting up nginx confs at ${confDir}"
)


show_current_py_lib_files() (
	process_global_vars "$@" >/dev/null 2>&1 &&
	set_python_version_const >/dev/null 2>&1 &&
	envDir="lib/python${pyMajor}.${pyMinor}/site-packages/${MC_LIB}"
	echo "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/"$envDir"
)


show_web_py_files() (
	process_global_vars "$@" >/dev/null 2>&1 &&
	echo "$(get_web_root)"/"$MC_API_DEST"
)


__get_remote_export_script__() (
	if [ -n "$1" ]; then
		exportMod='export'
	else
		exportMod=''
	fi
	output="export expName='${expName}';"
	output="${output} export PB_SECRET='$(__get_pb_secret__)';" &&
	output="${output} export PB_API_KEY='$(__get_pb_api_key__)';" &&
	output="${output} export MC_AUTH_SECRET_KEY='$(__get_api_auth_key__)';" &&
	output="${output} export MC_NAMESPACE_UUID='$(__get_namespace_uuid__)';" &&
	output="${output} export MC_DATABASE_NAME='musical chairs_db';" &&
	output="${output} export __DB_SETUP_PASS__='$(__get_db_setup_key__)';" &&
	output="${output} export MC_DB_PASS_OWNER='$(__get_db_owner_key__)';" &&
	output="${output} export MC_DB_PASS_API='$(__get_api_db_user_key__)';" &&
	output="${output} export AWS_ACCESS_KEY_ID='$(__get_s3_api_key__)';" &&
	output="${output} export AWS_SECRET_ACCESS_KEY='$(__get_s3_secret__)';" &&
	output="${output} export S3_ACCESS_KEY_ID='$(__get_s3_api_key__)';" &&
	output="${output} export S3_SECRET_ACCESS_KEY='$(__get_s3_secret__)';" &&
	output="${output} export MC_DB_PASS_RADIO='$(__get_radio_db_user_key__)';" &&
	output="${output} export S3_BUCKET_NAME='$(__get_s3_bucket_name__)';" &&
	output="${output} export S3_REGION_NAME='$(__get_s3_region_name__)';" &&
	output="${output} export AWS_ENDPOINT_URL='$(__get_s3_endpoint__)';" &&
	output="${output} export __ICES_BRANCH__='$(__get_ices_branch__)';"
	echo "$output"
)


startup_api() (
	set_env_vars "$@" &&
	if ! str_contains "$__SKIP__" "setup_api"; then
		setup_api
	fi &&
	. "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate
	errCode="$?"
	# see #python_env
	#put uvicorn in background within a subshell so that it doesn't put
	#the whole chain in the background, and then block due to some of the
	#preceeding comands still having stdout open
	(uvicorn --app-dir "$(get_web_root)"/"$MC_API_DEST" \
	--root-path /api/v1 \
	--host 0.0.0.0 \
	--port "$MC_API_PORT" \
	"index:app" </dev/null >api.out 2>&1 &)
	(exit "$errCode") &&
	echo "Server base is $(pwd). Look there for api.out and the log file"
	echo "done starting up api. Access at ${MC_FULL_URL}" ||
	echo "failed while trying to start up api"
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

shutdown_all_stations() (
	process_global_vars "$@" &&
	#gonna assume that the environment has been setup because if
	#the environment hasn't been setup yet then no radio stations
	#are running
	if [ ! -s "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate ]; then
		echo "python env not setup, so no stations to shut down"
		return
	fi
	. "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate &&
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
	__setup_api_dir__ &&
	sync_requirement_list &&
	copy_dir "$MC_TEMPLATES_SRC" "$(__get_app_root__)"/"$MC_TEMPLATES_DEST" &&
	copy_dir "$MC_API_SRC" "$(get_web_root)"/"$MC_API_DEST" &&
	create_py_env_in_app_trunk &&
	setup_database &&
	setup_nginx_confs &&
	echo "done setting up api"
)


#assume install_setup.sh has been run
setup_radio() (
	echo "setting up radio"
	process_global_vars "$@" &&
	shutdown_all_stations &&
	sync_requirement_list &&
	sync_utility_scripts &&
	sync_station_module &&

	create_py_env_in_app_trunk &&
	copy_dir "$MC_TEMPLATES_SRC" "$(__get_app_root__)"/"$MC_TEMPLATES_DEST" &&
	setup_database &&
	regen_station_configs &&
	pkgMgrChoice=$(get_pkg_mgr) &&
	icecastName=$(get_icecast_name "$pkgMgrChoice") &&
	setup_icecast_confs "$icecastName" &&
	echo "done setting up radio"
)

sync_station_module() (
	process_global_vars "$@" &&
	cp "$(__get_app_root__)"/"$MC_TEMPLATES_DEST"/socket_template.py\
		 "$MC_PY_MODULE_DIR"/station.py
)

regen_station_configs() (
	process_global_vars "$@" &&
	__install_py_env_if_needed__ &&
	. "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate &&
	(python <<EOF
from musical_chairs_libs.services import (
	StationService,
	EnvManager,
	TemplateService
)

envManager = EnvManager()
conn = envManager.get_configured_api_connection("musical_chairs_db")
try:
	stationService = StationService(conn)
	templateService = TemplateService()
	stations = list(stationService.get_stations())
	for station in stations:
		templateService.create_station_files(
			0,
			station.name,
			station.displayname,
			station.owner.username
		)

finally:
	conn.close()

EOF
	)

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


create_swap_if_needed() (
		case $(uname) in #()
		(Linux*)
			if [ ! -e /swapfile ]; then
				sudo dd if=/dev/zero of=/swapfile bs=128M count=24 &&
				sudo chmod 600 /swapfile &&
				sudo mkswap /swapfile &&
				sudo swapon /swapfile
			fi
			;; #()
		(*) ;;
	esac
)


setup_client() (
	echo "setting up client"
	process_global_vars "$@" &&
	error_check_all_paths "$MC_CLIENT_SRC" \
		"$(get_web_root)"/"$MC_CLIENT_DEST" &&
	#in theory, this should be sourced by .bashrc
	#but sometimes there's an interactive check that ends the sourcing early
	if [ -z "$NVM_DIR" ]; then
		export NVM_DIR="$HOME"/.nvm
		[ -s "$NVM_DIR"/nvm.sh ] && \. "$NVM_DIR"/nvm.sh  # This loads nvm
	fi &&
	#check if web application folder exists, clear out if it does,
	#delete otherwise
	empty_dir_contents "$(get_web_root)"/"$MC_CLIENT_DEST" &&

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
			"$(get_web_root)"/"$MC_CLIENT_DEST" &&
	unroot_dir "$(get_web_root)"/"$MC_CLIENT_DEST" &&
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


__create_fake_keys_file__() {
	echo "mc_auth_key=$(openssl rand -hex 32)" \
		> "$(__get_app_root__)"/keys/"$MC_PROJ_NAME_SNAKE"
}


get_hash_of_file() (
	file="$1"
	pyScript=$(cat <<-END
		import sys, hashlib
		print(hashlib.sha256(sys.stdin.read().encode("utf-8")).hexdigest())
	END
	)
	cat "$file" | python3 -c "$pyScript"
)


regen_file_reference_file() (
	process_global_vars "$@" &&
	outputFile="$MC_LIB_SRC"/dtos_and_utilities/file_reference.py
	printf '####### This file is generated. #######\n' > "$outputFile"
	printf '# edit regen_file_reference_file #\n' >> "$outputFile"
	printf '# in mc_dev_ops.sh and rerun\n' >> "$outputFile"
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

__replace_sql_script__() {
	copy_dir "$MC_SQL_SCRIPTS_SRC" "$(__get_app_root__)"/"$MC_SQL_SCRIPTS_DEST"
}


replace_sql_script() (
	process_global_vars "$@" &&
	setup_app_directories
	__replace_sql_script__
)


#assume install_setup.sh has been run
setup_unit_test_env() (
	echo 'setting up test environment'
	process_global_args "$@" || return

	define_consts &&
	define_directory_vars &&
	export __TEST_FLAG__='true'
	publicKeyFile=$(__get_debug_cert_path__).public.key.crt

	setup_app_directories
	__create_fake_keys_file__

	copy_dir "$MC_TEMPLATES_SRC" "$(__get_app_root__)"/"$MC_TEMPLATES_DEST" &&
	__replace_sql_script__ &&
	sync_requirement_list
	setup_env_api_file
	pyEnvPath="$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"
	#redirect stderr into stdout so that missing env will also trigger redeploy
	srcChanges=$(find "$MC_LIB_SRC" -newer "$pyEnvPath" 2>&1)
	if [ -n "$srcChanges" ] || \
	[ "$(get_repo_path)"/requirements.txt -nt "$pyEnvPath" ]
	then
		echo "changes?"
		create_py_env_in_app_trunk
	fi
	echo "$(__get_app_root__)"/"$MC_CONFIG_DIR"/.env &&
	echo "PYTHONPATH='${MC_SRC}:${MC_SRC}/api'" \
		>> "$(__get_app_root__)"/"$MC_CONFIG_DIR"/.env &&
	echo "done setting up test environment"
)


#assume install_setup.sh has been run
run_unit_tests() (
	echo "running unit tests"
	process_global_vars "$@"f
	export __TEST_FLAG__='true'
	setup_unit_test_env >/dev/null &&
	test_src="$MC_SRC"/tests &&
	export MC_AUTH_SECRET_KEY=$(__get_api_auth_key__) &&
	export PYTHONPATH="${MC_SRC}:${MC_SRC}/api" &&
	. "$(__get_app_root__)"/"$MC_TRUNK"/"$MC_PY_ENV"/bin/activate &&
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
	case $(uname) in #()
		(Linux*)
			echo "$HOME"/.bashrc
			;; #()
		(Darwin*)
			echo "$HOME"/.zshrc
			;; #()
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
	case $(uname) in #()
		(Linux*)
			echo "${MC_WEB_ROOT_OVERRIDE:-/srv}"
			return
			;; #()
		(Darwin*)
			echo "${MC_WEB_ROOT_OVERRIDE:-/Library/WebServer}"
			return
			;; #()
		(*) ;;
	esac
)

#call set_env_vars after connecting
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


print_exported_env_vars() (
	process_global_vars "$@" &&
	echo "App root: $(__get_app_root__)"
	__get_remote_export_script__ "$@"
)



process_global_args() {
	#in case need to pass the args to a remote script. example
	__GLOBAL_ARGS__=''
	while [ ! -z "$1" ]; do
		case "$1" in #()
			#build out to test_trash rather than the normal directories
			#sets MC_APP_ROOT and MC_WEB_ROOT_OVERRIDE
			#without having to set them explicitly
			(test)
				export __TEST_FLAG__='true'
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} test"
				;; #()
			(replace=*)
				export __REPLACE__=${1#replace=}
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} replace='${__REPLACE__}'"
				;; #()
			(clean) #tells setup functions to delete files/dirs before installing
				export __CLEAN_FLAG='clean'
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} clean"
				;; #()
			#activates debug_print. Also tells deploy script to use the diag branch
			(diag)
				export __DIAG_FLAG__='true'
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} diag"
				echo '' > diag_out_"$__INCLUDE_COUNT__"
				;; #()
			(setuplvl=*) #affects which setup scripst to run
				export __SETUP_LVL__=${1#setuplvl=}
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} setuplvl='${__SETUP_LVL__}'"
				;; #()
			#when I want to conditionally run with some experimental code
			(experiment=*)
				export __EXPERIMENT_NAME__=${1#experiment=}
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} experiment='${__EXPERIMENT_NAME__}'"
				;; #()
			(skip=*)
				export __SKIP__=${1#skip=}
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} skip='${__SKIP__}'"
				;; #()
			(dbsetuppass=*)
				export __DB_SETUP_PASS__=${1#dbsetuppass=}
				__GLOBAL_ARGS__="${__GLOBAL_ARGS__} dbsetuppass='${__DB_SETUP_PASS__}'"
				;; #()
			(*) ;;
		esac
		shift
	done
	export __GLOBAL_ARGS__
}


define_consts() {
	[ -z "$__MC_CONSTANTS_SET__" ] || return 0
	export MC_PACMAN='pacman'
	export MC_APT_CONST='apt-get'
	export MC_HOMEBREW='homebrew'
	export MC_CURRENT_USER=$(whoami)
	export MC_PROJ_NAME_0='musical chairs'
	export MC_PROJ_NAME_SNAKE='musical_chairs'
	export MC_BUILD_DIR='builds'
	export MC_CONTENT_DIR='music/radio'
	export MC_BIN_DIR='.local/bin'
	export MC_API_PORT='8033'
	#python environment names
	export MC_PY_ENV='mc_env'

	export MC_APP_ROOT=${MC_APP_ROOT:-"$HOME"}
	export MC_TRUNK="$MC_PROJ_NAME_SNAKE"
	export MC_LIB="$MC_PROJ_NAME_SNAKE"_libs
	export MC_DEV_OPS_LIB="$MC_PROJ_NAME_SNAKE"_dev_ops
	export MC_APP="$MC_PROJ_NAME_SNAKE"

	export MC_ICES_CONFIGS_DIR="$MC_TRUNK"/ices_configs
	export MC_PY_MODULE_DIR="$MC_TRUNK"/pyModules
	#MC_RADIO_LOG_DIR_CL may not be relevant anymore
	export MC_RADIO_LOG_DIR_CL="$MC_TRUNK"/radio_logs

	export MC_CONFIG_DIR="$MC_TRUNK"/config
	export MC_DB_DIR="$MC_TRUNK"/db
	export MC_UTEST_ENV_DIR="$MC_TEST_ROOT"/utest

	# directories that should be cleaned upon changes
	# suffixed with DEST
	export MC_TEMPLATES_DEST="$MC_TRUNK"/templates
	export MC_SQL_SCRIPTS_DEST="$MC_TRUNK"/sql_scripts
	export MC_API_DEST=api/"$MC_APP"
	export MC_CLIENT_DEST=client/"$MC_APP"


	export MC_SERVER_NAME=$(__get_domain_name__ "$MC_ENV")
	export MC_FULL_URL="https://${MC_SERVER_NAME}"

	export __MC_CONSTANTS_SET__='true'
	echo "constants defined"
}


create_install_directory() {
	if [ -z "$MC_LOCAL_REPO_DIR" ]; then
		echo 'MC_LOCAL_REPO_DIR is not set. '
		echo 'create_install_directory may have been run out of sequence'
		exit 1
	fi
	[ -d "$MC_LOCAL_REPO_DIR" ] ||
	mkdir -pv "$MC_LOCAL_REPO_DIR"
}

__get_url_base__() (
	echo 'musicalchairs'
)


__get_domain_name__() (
	envArg="$1"
	omitPort="$2"
	urlBase=$(__get_url_base__)
	tld='radio.fm'
	if [ -z "$tld" ]; then
		echo "tld has not been setup for this app yet" >&2
		echo ""
	fi
	case "$envArg" in #()
		(local*)
			if [ -n "$omitPort" ]; then
				urlSuffix="-local.${tld}"
			else
				urlSuffix="-local.${tld}:8080"
			fi
			;; #()
		(*)
			urlSuffix=".${tld}"
			;;
	esac
	echo "${urlBase}${urlSuffix}"
)


setup_app_directories() {
	[ -e "$(__get_app_root__)"/"$MC_TRUNK" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_TRUNK"
	[ -e "$(__get_app_root__)"/"$MC_CONFIG_DIR" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_CONFIG_DIR"
	[ -e "$(__get_app_root__)"/"$MC_DB_DIR" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_DB_DIR"
	[ -e "$(__get_app_root__)"/keys ] ||
	mkdir -pv "$(__get_app_root__)"/keys
	[ -e "$(__get_app_root__)"/"$MC_BUILD_DIR" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_BUILD_DIR"
	[ -e "$(__get_app_root__)"/"$MC_CONTENT_DIR" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_CONTENT_DIR"
	[ -e "$(__get_app_root__)"/"$MC_ICES_CONFIGS_DIR" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_ICES_CONFIGS_DIR"
	[ -e "$(__get_app_root__)"/"$MC_PY_MODULE_DIR" ] ||
	mkdir -pv "$(__get_app_root__)"/"$MC_PY_MODULE_DIR"
}


__setup_api_dir__() {
	if [ !  -e "$(get_web_root)"/"$MC_API_DEST" ]; then
		sudo -p 'Pass required to create web server directory: ' \
			mkdir -pv "$(get_web_root)"/"$MC_API_DEST" ||
		show_err_and_return "Could not create $(get_web_root)/${MC_API_DEST}"
	fi
}


define_directory_vars() {
	[ -z "$__DIRECTORY_VARS_SET__" ] || return 0
	export MC_LOCAL_REPO_DIR=$(get_repo_path) &&
	define_repo_paths
	export __DIRECTORY_VARS_SET__='true'
}


define_repo_paths() {
	export MC_SRC="$(get_repo_path)/src"
	export MC_API_SRC="$MC_SRC/api"
	export MC_CLIENT_SRC="$MC_SRC/client"
	export MC_LIB_SRC="$MC_SRC/$MC_LIB"
	export MC_DEV_OPS_LIB_SRC="$(get_repo_path)/$MC_DEV_OPS_LIB"
	export MC_TEMPLATES_SRC="$(get_repo_path)/templates"
	export MC_SQL_SCRIPTS_SRC="$(get_repo_path)/sql_scripts"
	export MC_REFERENCE_SRC="$(get_repo_path)/reference"
	export MC_TEST_ROOT="$(get_repo_path)/test_trash"
	echo "source paths defined"
}

process_global_vars() {
	process_global_args "$@" || return
	[ -z "$__GLOBALS_SET__" ] || return 0

	define_consts &&
	define_directory_vars &&
	setup_app_directories &&

	export __GLOBALS_SET__='globals'
}


unset_globals() {
	enable_wordsplitting
	exceptions=$(tr '\n' ' '<<-'EOF'
		MC_ENV
		MC_AUTH_SECRET_KEY
		MC_NAMESPACE_UUID
		MC_DB_PASS_API
		MC_DB_PASS_OWNER
		MC_LOCAL_REPO_DIR
		MC_REPO_URL
		MC_SERVER_KEY_FILE
		MC_SERVER_SSH_ADDRESS
		__DB_SETUP_PASS__
	EOF
	)
	cat "$(get_repo_path)"/mc_dev_ops.sh | grep export \
		| sed -n -e 's/^\t*export \([a-zA-Z0-9_]\{1,\}\)=.*/\1/p' | sort -u \
		| while read constant; do
				#exceptions is unquoted on purpose
				if array_contains "$constant" $exceptions; then
					echo "leaving $constant"
					continue
				fi
				case "$constant" in #()
					(MC_*)
						echo "unsetting ${constant}"
						unset "$constant"
						;; #()
					(__*)
						echo "unsetting ${constant}"
						unset "$constant"
						;; #()
					(*)
						;;
					esac
			done
	disable_wordsplitting
}


fn_ls() (
	process_global_vars "$@" >/dev/null
	perl -ne 'print "$1\n" if /^([a-zA-Z_0-9]+)\(\)/' \
		"$(get_repo_path)"/mc_dev_ops.sh | sort
)
