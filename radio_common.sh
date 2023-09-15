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

get_repo_path() (
	if [ -n "$radio_repo_path" ]; then
		echo "$radio_repo_path"
	else
		echo "$default_radio_repo_path"
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

output_env_vars() (
	export S3_ACCESS_KEY_ID=$(gen_pass)
	export S3_SECRET_ACCESS_KEY=$(gen_pass)
	printenv > "$appRoot"/used_env_vars
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
	process_global_vars &&
	__set_env_path_var__
}

__set_env_path_var__() {
	if perl -e "exit 1 if index('$PATH','${appRoot}/${binDir}') != -1"; then
		echo "Please add '${appRoot}/${binDir}' to path"
		export PATH="$PATH":"$appRoot"/"$binDir"
	fi
}


__export_py_env_vars__() {
	export searchBase="$appRoot"/"$contentHome" &&
	export dbName="$appRoot"/"$sqlite_trunk_filepath" &&
	export templateDir="$appRoot"/"$templates_dir_cl" &&
	export stationConfigDir="$appRoot"/"$ices_configs_dir" &&
	export stationModuleDir="$appRoot"/"$pyModules_dir"
	export RADIO_AUTH_SECRET_KEY=$(get_mc_auth_key)
}

print_py_env_var_guesses() (
	process_global_vars "$@" &&
	__set_env_path_var__ && #ensure that we can see mc-ices
	__export_py_env_vars__ &&
	echo "searchBase=$searchBase"
	echo "dbName=$dbName"
	echo "templateDir=$templateDir"
	echo "icecastConfLocation=$icecastConfLocation"
	echo "stationConfigDir=$stationConfigDir"
	echo "stationModuleDir=$stationModuleDir"
	echo "RADIO_AUTH_SECRET_KEY=$RADIO_AUTH_SECRET_KEY"
)

get_pkg_mgr() {
	define_consts >&2
	case $(uname) in
		(Linux*)
			if  which pacman >/dev/null 2>&1; then
				echo "$PACMAN_CONST"
				return 0
			elif which apt-get >/dev/null 2>&1; then
				echo "$APT_CONST"
				return 0
			fi
			;;
		(Darwin*)
			echo "$HOMEBREW_CONST"
			return 0
			;;
		(*)
			;;
	esac
	return 1
}

get_icecast_name() (
	_pkgMgrChoice="$1"
	case "$_pkgMgrChoice" in
    ("$PACMAN_CONST") echo 'icecast';;
    ("$APT_CONST") echo 'icecast2';;
    (*) echo 'icecast2';;
	esac
)

get_pb_api_key() (
	perl -ne 'print "$1\n" if /pb_api_key=(\w+)/' "$appRoot"/keys/"$projName"
)

get_pb_secret() (
	perl -ne 'print "$1\n" if /pb_secret=(\w+)/' "$appRoot"/keys/"$projName"
)

get_s3_api_key() (
	perl -ne 'print "$1\n" if /s3_api_key=(\w+)/' "$appRoot"/keys/"$projName"
)

get_s3_secret() (
	perl -ne 'print "$1\n" if /s3_secret=(\w+)/' "$appRoot"/keys/"$projName"
)

get_s3_secret() (
	perl -ne 'print "$1\n" if /s3_secret=(\w+)/' "$appRoot"/keys/"$projName"
)

get_mc_auth_key() (
	perl -ne 'print "$1\n" if /mc_auth_key=(\w+)/' "$appRoot"/keys/"$projName"
)

get_address() (
	keyFile="$appRoot"/keys/"$projName"
	perl -ne 'print "$1\n" if /address6=root@([\w:]+)/' "$keyFile"
)

get_id_file() (
	keyFile="$appRoot"/keys/"$projName"
	perl -ne 'print "$1\n" if /access_id_file=(.+)/' "$keyFile"
)

get_localhost_key_dir() (
	case $(uname) in
		(Darwin*)
			echo "$HOME"/.ssh
			;;
		(Linux*)
			;;
		(*) ;;
	esac
)

__get_remote_private_key__() (
	echo "/etc/ssl/private/${projName}.private.key.pem"
)

__get_remote_public_key__() (
	echo "/etc/ssl/certs/${projName}.public.key.pem"
)

__get_remote_intermediate_key__() (
	echo "/etc/ssl/certs/${projName}.intermediate.key.pem"
)

connect_sftp() (
	process_global_vars "$@" >&2 &&
	sftp -6 -i $(get_id_file) "root@[$(get_address)]"
)

get_ssl_vars() (
	process_global_vars "$@" >&2 &&
	sendJson=$(cat <<-END
	{
		"secretapikey": "$(get_pb_secret)",
		"apikey": "$(get_pb_api_key)"
	}
	END
	) &&
	curl -s --header "Content-Type: application/json" \
	--request POST \
	--data "$sendJson" \
	https://porkbun.com/api/json/v3/ssl/retrieve/$(_get_domain_name)

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
	fusermount -u "$appRoot"/"$contentHome"
}

link_to_music_files() {
	echo 'linking music files'
	process_global_vars "$@" &&
	if [ ! -e "$appRoot"/"$contentHome"/Soundtrack ]; then
		if [ -e "$HOME"/.passwd-s3fs ]; then
			s3fs "$(s3_name)" "$appRoot"/"$contentHome"/ \
				-o connect_timeout=10 -o retries=2 -o dbglevel=info -o curldbg
			[ -e "$appRoot"/"$contentHome"/Soundtrack ]
		else
			return 1
		fi
	fi &&
	echo 'music files should exist now'
}

input_match() (
	matchFor="$1"
	while read nextValue; do
		[ "$nextValue" = "$matchFor" ] && echo 't'
	done
)

str_contains() (
	haystackStr="$1"
	needleStr="$2"
	case "$haystackStr" in
		*"$needleStr"*)
			return 0
	esac
	return 1
)

array_contains() (
	searchValue="$1"
	shift
	while [ ! -z "$1" ]; do
		case $1 in
			"$searchValue")
				echo "$1"
				return 0
				;;
			*)
			;;
		esac
		shift
	done
	return 1
)

array_contains_equals() (
	searchValue="$1"
	shift
	while [ ! -z "$1" ]; do
		case $1 in
			"$searchValue"=*)
				result=${1#"$searchValue"=}
				echo "$result"
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
	[ "$experiment_name" = 'py3.8' ] && return 0
	set_python_version_const &&
	[ "$pyMajor" -eq 3 ] && [ "$pyMinor" -ge 9 ]
}

is_ices_version_good() {
	set_ices_version_const &&
	[ "$icesMajor" -ge 0 ] && [ "$icesMinor" -ge 5 ]
}

is_dir_empty() (
	target_dir="$1"
	lsRes=$(ls -A $target_dir)
	[ ! -d "$target_dir" ] || [ -z "$lsRes" ]
)

get_libs_dir() (
	__set_env_path_var__ >&2 #ensure that we can see mc-python
	set_python_version_const || return "$?"
	env_root="$1"
	packagePath="${pyEnv}/lib/python${pyMajor}.${pyMinor}/site-packages/"
	echo "$env_root"/"$packagePath"
)

# set up the python environment, then copy
# subshell () auto switches in use python version back at the end of function
create_py_env_in_dir() (
	echo "setting up py libs"
	__set_env_path_var__ #ensure that we can see mc-python
	linked_app_python_if_not_linked
	set_python_version_const || return "$?"
	env_root="$1"
	pyEnvDir="$env_root"/"$pyEnv"
	error_check_path "$pyEnvDir" &&
	if [ -n "$clean_flag" ]; then
		rm_contents_if_exist "$pyEnvDir" || return "$?"
	fi &&
	mc-python -m virtualenv "$pyEnvDir" &&
	. "$pyEnvDir"/bin/activate &&
	#this is to make some of my newer than checks work
	touch "$pyEnvDir" &&
	# #python_env
	# use regular python command rather mc-python
	# because mc-python still points to the homebrew location
	python -m pip install -r "$appRoot"/"$appTrunk"/requirements.txt &&
	echo "done setting up py libs"
)

create_py_env_in_app_trunk() (
	process_global_vars "$@" &&
	sync_requirement_list &&
	create_py_env_in_dir "$appRoot"/"$appTrunk" &&
	copy_dir "$lib_src" \
		"$(get_libs_dir "$appRoot"/"$appTrunk")""$lib_name"
)

copy_lib_to_test() (
	process_global_vars "$@" &&
	copy_dir "$lib_src" \
		"$(get_libs_dir "$utest_env_dir")"/"$lib_name"
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
	_dirEmptira="$1"
	if [ -w "$_dirEmptira" ]; then
		rm -rf "$_dirEmptira"/*
	else
		sudo -p "Password required for removing files from ${_dirEmptira}: " \
			rm -rf "$_dirEmptira"/*
	fi
)

rm_contents_if_exist() (
	_dirEmptira="$1"
	if ! is_dir_empty "$_dirEmptira"; then
		sudo_rm_contents "$_dirEmptira"
	fi
)

sudo_rm_dir() (
	_dirEmptira="$1"
	if [ -w "$_dirEmptira" ]; then
		rm -rf "$_dirEmptira"
	else
		sudo -p "Password required to remove ${_dirEmptira}: " \
			rm -rf "$_dirEmptira"
	fi
)

sudo_cp_contents() (
	from_dir="$1"
	to_dir="$2"
	if [ -r "$from_dir" ] && [ -w "$to_dir" ]; then
		cp -rv "$from_dir"/. "$to_dir"
	else
		sudo -p 'Pass required for copying files: ' \
			cp -rv "$from_dir"/. "$to_dir"
	fi
)

sudo_mkdir() (
	_dirMakera="$1"
	mkdir -pv "$_dirMakera" ||
	sudo -p "Password required for creating ${_dirMakera}: " \
		mkdir -pv "$_dirMakera"
)

unroot_dir() (
	_dirUnrootura="$1"
	if [ ! -w "$_dirUnrootura" ]; then
		prompt='Password required to change owner of'
		prompt="${prompt} ${_dirUnrootura} to current user: "
		sudo -p "$prompt" \
			chown -R "$currentUser": "$_dirUnrootura"
	fi
)

empty_dir_contents() (
	_dirEmptira="$1"
	echo "emptying '${_dirEmptira}'"
	error_check_path "$_dirEmptira" &&
	if [ -e "$_dirEmptira" ]; then
		rm_contents_if_exist || return "$?"
	else
		sudo_mkdir "$_dirEmptira" || return "$?"
	fi &&
	unroot_dir "$_dirEmptira" &&
	echo "done emptying '${_dirEmptira}'"
)

get_bin_path() (
	_pkg="$1"
	case $(uname) in
		(Darwin*)
			brew info "$_pkg" \
			| grep -A1 'has been installed as' \
			| awk 'END{ print $1 }'
			;;
		(*) which "$_pkg" ;;
	esac
)

linked_app_python_if_not_linked() {
	if ! mc-python -V 2>/dev/null; then
		if [ ! -e "$appRoot"/"$binDir" ]; then
			sudo_mkdir "$appRoot"/"$binDir" || return "$?"
		fi
		case $(uname) in
			(Darwin*)
				ln -sf $(get_bin_path python@3.9) \
					"$appRoot"/"$binDir"/mc-python
				;;
			(*)
				ln -sf $(get_bin_path python3) \
					"$appRoot"/"$binDir"/mc-python
				;;
		esac
	fi
	echo "done linking"
}

brew_is_installed() (
	_pkg="$1"
	echo "checking for $_pkg"
	case $(uname) in
		(Darwin*)
			brew info "$_pkg" >/dev/null 2>&1 &&
			! brew info "$_pkg" | grep 'Not installed' >/dev/null
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

#this may seem useless but we need it for test runner to read .env
setup_env_api_file() (
	echo 'setting up .env file'
	envFile="$appRoot"/"$config_dir"/.env
	error_check_all_paths "$templates_src"/.env_api "$envFile" &&
	_pkgMgrChoice=$(get_pkg_mgr) &&
	cp "$templates_src"/.env_api "$envFile" &&
	does_file_exist "$envFile" &&
	perl -pi -e "s@^(searchBase=).*\$@\1'${appRoot}/${contentHome}'@" \
		"$envFile" &&
	perl -pi -e "s@^(dbName=).*\$@\1'${appRoot}/${sqlite_trunk_filepath}'@" \
		"$envFile" &&
	perl -pi -e "s@^(templateDir=).*\$@\1'${appRoot}/${templates_dir_cl}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(stationConfigDir=).*\$@\1'${appRoot}/${ices_configs_dir}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(stationModuleDir=).*\$@\1'${appRoot}/${pyModules_dir}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(icecastConfLocation=).*\$@\1'${templates_src}/icecast.xml'@" \
		"$envFile" &&
	echo 'done setting up .env file'
)

copy_dir() (
	from_dir="$1"
	to_dir="$2"
	echo "copying from ${from_dir} to ${to_dir}"
	error_check_all_paths "$from_dir"/. "$to_dir" &&
	empty_dir_contents "$to_dir" &&
	sudo_cp_contents "$from_dir" "$to_dir" &&
	unroot_dir "$to_dir" &&
	echo "done copying dir from ${from_dir} to ${to_dir}"
)

replace_db_file_if_needed() (
	echo 'tentatively copying initial db'
	process_global_vars "$@" &&
	error_check_all_paths "$reference_src_db" \
		"$appRoot"/"$sqlite_trunk_filepath"  &&
	if [ ! -e "$appRoot"/"$sqlite_trunk_filepath" ] || [ -n "$clean_flag" ] \
	|| [ -n "$replace_db_flag" ]; then
		cp -v "$reference_src_db" "$appRoot"/"$sqlite_trunk_filepath" &&
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
			kill_process_using_port "$apiPort"
		fi
	fi

	__export_py_env_vars__ &&
	. "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate &&
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
	_icecastName="$1"
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

__install_py_env__() {
	sync_requirement_list &&
	create_py_env_in_app_trunk
}

install_py_env() {
	unset_globals
	process_global_vars "$@" &&
	__export_py_env_vars__ &&
	__install_py_env__ &&
	echo "done installing py env"
}

__install_py_env_if_needed__() {
	if [ ! -e "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate ]; then
		__install_py_env__
	fi
}

print_schema_scripts() (
	process_global_vars "$@" &&
	__install_py_env_if_needed__ &&
	. "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate &&
	printf '\033c' &&
	(python <<-EOF
	from musical_chairs_libs.services import EnvManager
	EnvManager.print_expected_schema()
	EOF
	)
)

start_python() (
	process_global_vars "$@" &&
	__install_py_env_if_needed__ &&
	. "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate &&
	python
)

sync_utility_scripts() (
	process_global_vars "$@" &&
	cp "$workspaceAbsPath"/radio_common.sh "$appRoot"/radio_common.sh
)

#copy python dependency file to the deployment directory
sync_requirement_list() (
	process_global_vars "$@" &&
	error_check_all_paths "$workspaceAbsPath"/requirements.txt \
		"$appRoot"/"$appTrunk"/requirements.txt "$appRoot"/requirements.txt &&
	#keep a copy in the parent radio directory
	cp "$workspaceAbsPath"/requirements.txt \
		"$appRoot"/"$appTrunk"/requirements.txt &&
	cp "$workspaceAbsPath"/requirements.txt "$appRoot"/requirements.txt
)

gen_pass() (
	pass_len=${1:-16}
	LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c "$pass_len"
)

compare_dirs() (
	src_dir="$1"
	cpy_dir="$2"
	error_check_all_paths "$src_dir" "$cpy_dir"
	exit_code=0
	if [ ! -e "$cpy_dir" ]; then
		echo "$cpy_dir/ is not in place"
		return 1
	fi
	rm -f src_fifo cpy_fifo cmp_fifo
	mkfifo src_fifo cpy_fifo cmp_fifo

	src_res=$(find "$src_dir" | \
		sed "s@${src_dir%/}/\{0,1\}@@" | sort)
	cpy_res=$(find "${cpy_dir}" -not -path "${cpy_dir}/${pyEnv}/*" \
		-and -not -path "${cpy_dir}/${pyEnv}" | \
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

__get_keychain_osx__() (
	echo '/Library/Keychains/System.keychain'
)

__get_debug_cert_path__() (
	echo $(get_localhost_key_dir)/"$projName"_localhost_debug
)

__get_local_nginx_cert_path__() (
	echo $(get_localhost_key_dir)/"$projName"_localhost_nginx
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
	| perl -ne 'print "$1\n" if m{CN=([^/]+)}'
)

__certs_matching_name_osx__() (
	commonName="$1"
	pattern='(-----BEGIN CERTIFICATE-----[^-]+-----END CERTIFICATE-----)'
	script=$(cat <<-scriptEOF
	while(\$_ =~ /$pattern/g) {
		print "\$1\0"
	}
	scriptEOF
	)
	security find-certificate -a -p -c "$commonName" \
	$(__get_keychain_osx__) | perl -0777 -ne "$script"
)

__certs_matching_name_exact__() (
	commonName="$1"
	case $(uname) in
		(Darwin*)
			__certs_matching_name_osx__ "$commonName" \
			| extract_commonName_from_cert \
			| input_match "$commonName"
			;;
		(*)
			echo "operating system not configured"
			return 0
			;;
	esac
)

__generate_local_ssl_cert_osx__() (
	commonName="$1"
	domain="$2" &&
	publicKeyFile="$3" &&
	privateKeyFile="$4" &&
	mkfifo cat_config_fifo
	{
	cat<<-OpenSSLConfig
	$(cat '/System/Library/OpenSSL/openssl.cnf')
	$(printf "[SAN]\nsubjectAltName=DNS:${domain},IP:127.0.0.1")
	OpenSSLConfig
	} > cat_config_fifo &
	openssl req -x509 -sha256 -new -nodes -newkey rsa:2048 -days 7 \
	-subj "/C=US/ST=CA/O=fake/CN=${commonName}" -reqexts SAN -extensions SAN \
	-config cat_config_fifo \
	-keyout "$privateKeyFile" -out "$publicKeyFile"
	err_code="$?"
	rm -f cat_config_fifo
	return "$err_code"
)

__install_local_cert_osx__() (
	publicKeyFile="$1" &&
	sudo security add-trusted-cert -p ssl -d -r trustRoot \
	-k $(__get_keychain_osx__) "$publicKeyFile"
)

__clean_up_invalid_cert__() (
	commonName="$1" &&
	case $(uname) in
		(Darwin*)
			__certs_matching_name_osx__ "$commonName" \
				| while IFS= read -r -d '' cert; do
					sha256Value=$(echo "$cert" | extract_sha256_from_cert) &&
					echo "$cert" | is_cert_expired &&
					sudo security delete-certificate \
						-Z "$sha256Value" -t $(__get_keychain_osx__)
				done
			;;
		(*)
			return 0
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
			__generate_local_ssl_cert_osx__ "$commonName" "$domain" \
			"$publicKeyFile" "$privateKeyFile" &&
			__install_local_cert_osx__ "$publicKeyFile" ||
			return 1
			;;
		(*)
			echo "operating system not configured"
			return 1
			;;
	esac
	return 0
)

setup_ssl_cert_local_debug() (
	process_global_vars "$@" &&
	publicKeyFile=$(__get_debug_cert_path__).public.key.pem &&
	privateKeyFile=$(__get_debug_cert_path__).private.key.pem &&
	__clean_up_invalid_cert__ "${appName}-localhost"
	__setup_ssl_cert_local__ "${appName}-localhost" 'localhost' \
		"$publicKeyFile" "$privateKeyFile" &&
	setup_react_env_debug
)

print_ssl_cert_info() (
	process_global_vars "$@" &&
	domain=$(_get_domain_name "$app_env" 'omitPort') &&
	case "$app_env" in
		(local*)
			isDebugServer=${1#is_debug_server=}
			if [ -n "$isDebugServer" ]; then
				domain="${domain}-localhost"
			fi
			case $(uname) in
			(Darwin*)
				echo "#### nginx info ####"
				__certs_matching_name_osx__ "$domain" \
					| while IFS= read -r -d '' cert; do
						sha256Value=$(echo "$cert" | extract_sha256_from_cert) &&
						echo "$cert" | openssl x509 -enddate -subject -noout
					done
				echo "#### debug server info ####"
				echo "${domain}-localhost"
				__certs_matching_name_osx__ "${appName}-localhost" \
					| while IFS= read -r -d '' cert; do
						sha256Value=$(echo "$cert" | extract_sha256_from_cert) &&
						echo "$cert" | openssl x509 -enddate -subject -noout
					done
				;;
			(*)
				echo 'Finding local certs is not setup for this OS'
				;;
		esac
			;;
		(*)
			publicKeyFile=$(__get_remote_public_key__) &&
			cat "$publicKeyFile" | openssl x509 -enddate -subject -noout
			;;
	esac
)

setup_ssl_cert_nginx() (
	process_global_vars "$@" &&
	domain=$(_get_domain_name "$app_env" 'omitPort') &&
	case "$app_env" in
		(local*)
			publicKeyFile=$(__get_local_nginx_cert_path__).public.key.pem &&
			privateKeyFile=$(__get_local_nginx_cert_path__).private.key.pem &&
			# we're leaving off the && because what would that even mean here?
			__clean_up_invalid_cert__ "$domain"
			if [ -z $(__certs_matching_name_exact__ "$domain") ]; then
				__setup_ssl_cert_local__ \
				"$domain" "$domain" "$publicKeyFile" "$privateKeyFile"
			fi
			;;
		(*)
			publicKeyFile=$(__get_remote_public_key__) &&
			privateKeyFile=$(__get_remote_private_key__) &&
			intermediateKeyFile=$(__get_remote_intermediate_key__) &&

			if [ ! -e "$publicKeyFile" ] || [ ! -e "$privateKeyFile" ] ||
			cat "$publicKeyFile" | is_cert_expired ||
			str_contains "$replace" "ssl_certs"; then
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
	envFile="$client_src"/.env.local
	echo "$envFile"
	echo 'REACT_APP_API_VERSION=v1' > "$envFile"
	echo 'REACT_APP_BASE_ADDRESS=https://localhost:8032' >> "$envFile"
	echo 'HTTPS=true' >> "$envFile"
	echo "SSL_CRT_FILE=$(__get_debug_cert_path__).public.key.pem" >> "$envFile"
	echo "SSL_KEY_FILE=$(__get_debug_cert_path__).private.key.pem" >> "$envFile"
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

__copy_and_update_nginx_template__() {
	sudo -p 'copy nginx config' \
		cp "$templates_src"/nginx_template.conf "$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<appClientPathCl>@${webRoot}/${appClientPathCl}@" \
		"$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<server_name>@${server_name}@g" "$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<apiPort>@${apiPort}@" "$appConfFile"
}

update_nginx_conf() (
	echo "updating nginx site conf"
	appConfFile="$1"
	error_check_all_paths "$templates_src" "$appConfFile" &&
	__copy_and_update_nginx_template__ &&
	case "$app_env" in
		(local*)
			publicKey=$(__get_local_nginx_cert_path__).public.key.pem &&
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
	echo "done updating nginx site conf"
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
		sites_folder_path=$(dirname $(get_nginx_value))
		echo "sites_folder_path: $sites_folder_path" >&2
		absPath="$sites_folder_path"/"$confDir"
		if [ ! -d "$absPath" ]; then
			if [ -e "$absPath" ]; then
				echo "{$absPath} is a file, not a directory" 1>&2
				return 1
			fi
			#Apparently nginx will look for includes with either an absolute path
			#or path relative to the config
			#some os'es are finicky about creating directories at the root lvl
			#even with sudo, so we're not going to even try
			#we'll just create missing dir in $sites_folder_path folder
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
	echo "enabling nginx site confs"
	confDirInclude="$1"
	escaped_guess=$(literal_to_regex "$confDirInclude")
	#uncomment line if necessary in config
	sudo -p "Enable ${confDirInclude}" \
		perl -pi -e "s/^[ \t]*#// if m@$escaped_guess@" "$(get_nginx_value)" &&
	echo "done enabling nginx site confs"
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
	echo "$confDir"/"$appName".conf
)

print_cert_paths() (
	process_global_vars "$@" >/dev/null &&
	confDirInclude=$(get_nginx_conf_dir_include) &&
	confDir=$(get_abs_path_from_nginx_include "$confDirInclude") 2>/dev/null
	cat "$confDir"/"$appName".conf | perl -ne \
	'print "$1\n" if /ssl_certificate ([^;]+)/'
	cat "$confDir"/"$appName".conf | perl -ne \
	'print "$1\n" if /ssl_certificate_key ([^;]+)/'
	cat "$confDir"/"$appName".conf | perl -ne \
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
	update_nginx_conf "$confDir"/"$appName".conf &&
	sudo -p 'Remove default nginx config' \
		rm -f "$confDir"/default &&
	restart_nginx &&
	echo 'done setting up nginx confs'
)

start_icecast_service() (
	echo 'starting icecast service'
	_icecastName="$1"
	case $(uname) in
		(Linux*)
			if ! systemctl is-active --quiet "$_icecastName"; then
				sudo -p "enabling ${_icecastName}" systemctl enable "$_icecastName"
				sudo -p "starting ${_icecastName}" systemctl start "$_icecastName"
			fi
			;;
		(*) ;;
	esac &&
	echo 'done starting icecast service'
)

install_ices() (
	process_global_vars "$@" &&
	__set_env_path_var__ &&
	if ! mc-ices -V 2>/dev/null || ! is_ices_version_good \
	|| [ -n "$ice_branch" ]; then
		shutdown_all_stations &&
		folderPath="$appRoot"/"$buildDir"/"$projName"/compiled_dependencies
		sh "$folderPath"/build_ices.sh "$ice_branch"
	fi
)

get_icecast_conf() (
	_icecastName="$1"
	case $(uname) in
		(Linux*)
			if ! systemctl status "$_icecastName" >/dev/null 2>&1; then
					echo "$_icecastName is not running at the moment"
					exit 1
			fi
				systemctl status "$_icecastName" | grep -A2 CGroup | \
					head -n2 | tail -n1 | awk '{ print $NF }'
			;;
		(Darwin*)
			#we don't have icecast on the mac anyway so we'll just return the
			#source code location
			echo "$templates_src"/icecast.xml
			;;
		*) ;;
	esac
)

show_current_py_lib_files() (
	process_global_vars "$@" >/dev/null 2>&1 &&
	set_python_version_const >/dev/null 2>&1 &&
	envDir="lib/python${pyMajor}.${pyMinor}/site-packages/${lib_name}"
	echo "$appRoot"/"$appTrunk"/"$pyEnv"/"$envDir"
)

show_icecast_log() (
	process_global_vars "$@" >/dev/null 2>&1 &&
	__export_py_env_vars__ >/dev/null 2>&1 &&
	__install_py_env_if_needed__ >/dev/null 2>&1 &&
	. "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate >/dev/null 2>&1 &&
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
	__export_py_env_vars__ >/dev/null 2>&1 &&
	__install_py_env_if_needed__ >/dev/null 2>&1 &&
	. "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate >/dev/null 2>&1 &&
	logName="$appRoot"/"$ices_configs_dir"/ices."$owner"_"$station".conf
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

	sudo -p 'Pass required for modifying icecast config: ' \
		perl -pi -e "s/>\w*/>${sourcePassword}/ if /source-password/" \
		"$icecastConfLocation" &&
	sudo -p 'Pass required for modifying icecast config: ' \
		perl -pi -e "s/>\w*/>${relayPassword}/ if /relay-password/" \
		"$icecastConfLocation" &&
	sudo -p 'Pass required for modifying icecast config: ' \
		perl -pi -e "s/>\w*/>${adminPassword}/ if /admin-password/" \
		"$icecastConfLocation" &&
	sudo -p 'Pass required for modifying icecast config: ' \
		perl -pi -e "s@^([ \t]*)<.*@\1<bind-address>::</bind-address>@" \
		-e "if /<bind-address>/" \
		"$icecastConfLocation" &&
	echo "done updating icecast config"
)

update_all_ices_confs() (
	echo "updating ices confs"
	sourcePassword="$1"
	process_global_vars "$@"
	for conf in "$appRoot"/"$ices_configs_dir"/*.conf; do
		[ ! -s "$conf" ] && continue
		perl -pi -e "s/>\w*/>${sourcePassword}/ if /Password/" "$conf"
	done &&
	echo "done updating ices confs"
)


setup_icecast_confs() (
	echo "setting up icecast/ices"
	_icecastName="$1"
	process_global_vars "$@" &&
	#need to make sure that  icecast is running so we can get the config
	#location from systemd. While icecast does have a custom config option
	#I don't feel like editing the systemd service to make it happen
	start_icecast_service "$_icecastName" &&
	icecastConfLocation=$(get_icecast_conf "$_icecastName") &&
	sourcePassword=$(gen_pass) &&
	update_icecast_conf "$icecastConfLocation" \
		"$sourcePassword" $(gen_pass) $(gen_pass) &&
	update_all_ices_confs "$sourcePassword" &&
	sudo -p "restarting ${_icecastName}" systemctl restart "$_icecastName" &&
	echo "done setting up icecast/ices"
)


run_song_scan() (
	process_global_vars "$@"
	link_to_music_files &&
	setup_radio &&
	__export_py_env_vars__ &&
	. "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate &&

	if [ -n "$shouldReplaceDb" ]; then
		sudo_rm_contents "$dbName" || return "$?"
	fi &&
	# #python_env
	python  <<-EOF
	import os
	from musical_chairs_libs.song_scanner import SongScanner
	from musical_chairs_libs.services import EnvManager
	print("Starting")
	EnvManager.setup_db_if_missing(echo = True)
	songScanner = SongScanner()
	inserted = songScanner.save_paths('${appRoot}/${contentHome}')
	print(f"saving paths done: {inserted} inserted")
	updated = songScanner.update_metadata('${appRoot}/${contentHome}')
	print(f"updating songs done: {updated}")
	EOF
)

shutdown_all_stations() (
	process_global_vars "$@" &&
	#gonna assume that the environment has been setup because if
	#the environment hasn't been setup yet then no radio stations
	#are running
	if [ ! -s "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate ]; then
		echo "python env not setup, so no stations to shut down"
		return
	fi
	__export_py_env_vars__ &&
	. "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate &&
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

startup_radio() (
	process_global_vars "$@" &&
	__set_env_path_var__ && #ensure that we can see mc-ices
	_pkgMgrChoice=$(get_pkg_mgr) &&
	link_to_music_files &&
	setup_radio &&
	export searchBase="$appRoot"/"$contentHome" &&
	__export_py_env_vars__ &&
	. "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate &&
	for conf in "$appRoot"/"$ices_configs_dir"/*.conf; do
		[ ! -s "$conf" ] && continue
		mc-ices -c "$conf"
	done
)

startup_api() (
	process_global_vars "$@" &&
	__set_env_path_var__ && #ensure that we can see mc-ices
	if ! str_contains "$skip" "setup_api"; then
		setup_api
	fi &&
	__export_py_env_vars__ &&
	. "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate &&
	# see #python_env
	#put uvicorn in background with in a subshell so that it doesn't put
	#the whole chain in the background, and then block due to some of the
	#preceeding comands still having stdout open
	(uvicorn --app-dir "$webRoot"/"$appApiPathCl" --root-path /api/v1 \
	--host 0.0.0.0 --port "$apiPort" \
	"index:app" </dev/null >api.out 2>&1 &)
	echo "done starting up api. Access at $full_url"
)


startup_nginx_for_debug() (
	process_global_vars "$@" &&
	export apiPort='8032'
	setup_nginx_confs &&
	restart_nginx
)

setup_api() (
	echo "setting up api"
	process_global_vars "$@" &&
	kill_process_using_port "$apiPort" &&
	sync_utility_scripts &&
	sync_requirement_list &&
	copy_dir "$templates_src" "$appRoot"/"$templates_dir_cl" &&
	copy_dir "$apiSrc" "$webRoot"/"$appApiPathCl" &&
	create_py_env_in_app_trunk &&
	replace_db_file_if_needed2 &&
	setup_nginx_confs &&
	echo "done setting up api"
)

create_swap_if_needed() (
		case $(uname) in
		(Linux*)
			if [ ! -e /swapfile ]; then
				sudo dd if=/dev/zero of=/swapfile bs=128M count=16 &&
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
	error_check_all_paths "$client_src"  "$webRoot"/"$appClientPathCl" &&
	#in theory, this should be sourced by .bashrc
	#but sometimes there's an interactive check that ends the sourcing early
	if [ -z "$NVM_DIR" ]; then
		export NVM_DIR="$HOME"/.nvm
		[ -s "$NVM_DIR"/nvm.sh ] && \. "$NVM_DIR"/nvm.sh  # This loads nvm
	fi &&
	#check if web application folder exists, clear out if it does,
	#delete otherwise
	empty_dir_contents "$webRoot"/"$appClientPathCl" &&

	export REACT_APP_API_VERSION=v1 &&
	export REACT_APP_BASE_ADDRESS="$full_url" &&
	#set up react then copy
	#install packages
	npm --prefix "$client_src" i &&
	#build code (transpile it)
	npm run --prefix "$client_src" build &&
	#copy built code to new location
	sudo -p 'Pass required for copying client files: ' \
		cp -rv "$client_src"/build/. "$webRoot"/"$appClientPathCl" &&
	unroot_dir "$webRoot"/"$appClientPathCl" &&
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
	echo "done starting up full web. Access at $full_url"
)

#assume install_setup.sh has been run
setup_radio() (
	echo "setting up radio"
	process_global_vars "$@" &&
	shutdown_all_stations &&
	sync_requirement_list &&
	sync_utility_scripts &&

	create_py_env_in_app_trunk &&
	copy_dir "$templates_src" "$appRoot"/"$templates_dir_cl" &&
	replace_db_file_if_needed2 &&
	_pkgMgrChoice=$(get_pkg_mgr) &&
	_icecastName=$(get_icecast_name "$_pkgMgrChoice") &&
	setup_icecast_confs "$_icecastName" &&
	echo "done setting up radio"
)

__create_fake_keys_file__() {
	echo "mc_auth_key=$(openssl rand -hex 32)" > "$appRoot"/keys/"$projName"
}


#assume install_setup.sh has been run
setup_unit_test_env() (
	echo "setting up test environment"
	process_global_vars "$@" &&
	export appRoot="$test_root"

	__create_fake_keys_file__
	setup_common_dirs

	copy_dir "$templates_src" "$appRoot"/"$templates_dir_cl" &&
	error_check_all_paths "$reference_src_db" \
		"$appRoot"/"$sqlite_trunk_filepath" &&
	sync_requirement_list
	setup_env_api_file
	pyEnvPath="$appRoot"/"$appTrunk"/"$pyEnv"
	#redirect stderr into stdout so that missing env will also trigger redeploy
	srcChanges=$(find "$lib_src" -newer "$pyEnvPath" 2>&1)
	if [ -n "$srcChanges" ] || \
	[ "$workspaceAbsPath"/requirements.txt -nt "$pyEnvPath" ]
	then
		echo "changes?"
		create_py_env_in_app_trunk
	fi
	replace_db_file_if_needed2 &&
	echo "$appRoot"/"$config_dir"/.env &&
	echo "PYTHONPATH='${srcPath}:${srcPath}/api'" \
		>> "$appRoot"/"$config_dir"/.env &&
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
	export appRoot="$test_root"
	setup_unit_test_env &&
	test_src="$srcPath"/tests &&
	__export_py_env_vars__ &&
	export PYTHONPATH="${srcPath}:${srcPath}/api" &&
	. "$appRoot"/"$appTrunk"/"$pyEnv"/bin/activate &&
	cd "$test_src"
	pytest -s "$@" &&
	echo "done running unit tests"
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

process_global_args() {
	#for if we need to pass the args to a remote script for example
	global_args=''
	while [ ! -z "$1" ]; do
		case "$1" in
			#build out to test_trash rather than the normal directories
			#sets appRoot and webRoot without having to set them explicitly
			(test)
				export test_flag='test'
				global_args="${global_args} test"
				;;
			(replace=*)
				export replace=${1#replace=}
				global_args="${global_args} replace='${replace}'"
				;;
			(replaceDb) #tells setup to replace sqlite3 db
				export replace_db_flag='true'
				global_args="${global_args} replaceDb"
				;;
			(clean) #tells setup functions to delete files/dirs before installing
				export clean_flag='clean'
				global_args="${global_args} clean"
				;;
			#activates debug_print. Also tells deploy script to use the diag branch
			(diag)
				export diag_flag='true'
				global_args="${global_args} diag"
				echo '' > diag_out_"$include_count"
				;;
			(env=*) #affects which url to use
				export app_env=${1#env=}
				global_args="${global_args} env='${app_env}'"
				;;
			(appRoot=*)
				export appRoot=${1#appRoot=}
				global_args="${global_args} appRoot='${appRoot}'"
				;;
			(webRoot=*)
				export webRoot=${1#webRoot=}
				global_args="${global_args} webRoot='${webRoot}'"
				;;
			(setup_lvl=*) #affects which setup scripst to run
				export setup_lvl=${1#setup_lvl=}
				global_args="${global_args} setup_lvl='${setup_lvl}'"
				;;
			#when I want to conditionally run with some experimental code
			(experiment_name=*)
				export experiment_name=${1#experiment_name=}
				global_args="${global_args} experiment_name='${experiment_name}'"
				;;
			(skip=*)
				export skip=${1#skip=}
				global_args="${global_args} skip='${skip}'"
				;;
			(ice_branch=*)
				export ice_branch=${1#ice_branch=}
				global_args="${global_args} ice_branch='${ice_branch}'"
				;;
			(db_pass=*)
				export db_pass=${1#db_pass=}
				global_args="${global_args} db_pass='${db_pass}'"
				;;
			(*) ;;
		esac
		shift
	done
	export global_args
}

define_consts() {
	[ -z "$constants_set" ] || return 0
	export PACMAN_CONST='pacman'
	export APT_CONST='apt-get'
	export HOMEBREW_CONST='homebrew'
	export currentUser=$(whoami)
	export projName='musical_chairs'
	export buildDir='builds'
	export contentHome='music/radio'
	export binDir='.local/bin'
	export apiPort='8033'
	#done't try to change from home
	export default_radio_repo_path="$HOME"/"$buildDir"/"$projName"
	export constants_set='true'
	echo "constants defined"
}

create_install_dir() {
	[ -d "$(get_repo_path)" ] ||
	mkdir -pv "$(get_repo_path)"

}

define_top_level_terms() {
	appRoot=${appRoot:-"$HOME"}
	export test_root="$workspaceAbsPath/test_trash"
	export appRoot_0="$appRoot"

	if [ -n "$test_flag" ]; then
		appRoot="$test_root"
		webRoot="$test_root"
	fi

	sqlite_filename='songs_db.sqlite'
	export appTrunk="$projName"_dir
	export appRoot="$appRoot"
	export webRoot="$webRoot"


	export lib_name="$projName"_libs
	export appName="$projName"_app

	echo "top level terms defined"
}

define_app_dir_paths() {
	export ices_configs_dir="$appTrunk"/ices_configs
	export pyModules_dir="$appTrunk"/pyModules

	export config_dir="$appTrunk"/config
	export db_dir="$appTrunk"/db
	export sqlite_trunk_filepath="$db_dir"/"$sqlite_filename"
	export utest_env_dir="$test_root"/utest

	# directories that should be cleaned upon changes
	# suffixed with 'cl' for 'clean'
	export templates_dir_cl="$appTrunk"/templates

	echo "app dir paths defined and created"
}

define_web_server_paths() {
	case $(uname) in
		(Linux*)
			export webRoot=${webRoot:-/srv}
			;;
		(Darwin*)
			export webRoot=${webRoot:-/Library/WebServer}
			;;
		(*) ;;
	esac

	export appApiPathCl=api/"$appName"
	export appClientPathCl=client/"$appName"

	echo "web server paths defined"
}

__get_url_base__() (
	echo "$projName" | tr -d _
)

_get_domain_name() (
	envArg="$1"
	omitPort="$2"
	url_base=$(__get_url_base__)
	case "$envArg" in
		(local*)
			if [ -n "$omitPort" ]; then
				url_suffix='-local.radio.fm'
			else
				url_suffix='-local.radio.fm:8080'
			fi
			;;
		(*)
			url_suffix='.radio.fm'
			;;
	esac
	echo "${url_base}${url_suffix}"
)

__define_url__() {
	echo "env: ${app_env}"
	export server_name=$(_get_domain_name "$app_env")
	export full_url="https://${server_name}"
	echo "url defined"
}

define_repo_paths() {
	export srcPath="$workspaceAbsPath/src"
	export apiSrc="$srcPath/api"
	export client_src="$srcPath/client"
	export lib_src="$srcPath/$lib_name"
	export templates_src="$workspaceAbsPath/templates"
	export reference_src="$workspaceAbsPath/reference"
	export reference_src_db="$reference_src/$sqlite_filename"
	echo "source paths defined"
}

setup_common_dirs() {
	[ -e "$appRoot"/"$config_dir" ] ||
	mkdir -pv "$appRoot"/"$config_dir"
	[ -e "$appRoot"/"$ices_configs_dir" ] ||
	mkdir -pv "$appRoot"/"$ices_configs_dir"
	[ -e "$appRoot"/"$pyModules_dir" ] ||
	mkdir -pv "$appRoot"/"$pyModules_dir"
	[ -e "$appRoot"/"$db_dir" ] ||
	mkdir -pv "$appRoot"/"$db_dir"
	[ -e "$appRoot"/keys ] ||
	mkdir -pv "$appRoot"/keys
}

setup_base_dirs() {

	[ -e "$appRoot"/"$appTrunk" ] ||
	mkdir -pv "$appRoot"/"$appTrunk"

	setup_common_dirs

	[ -e "$appRoot"/"$contentHome" ] ||
	mkdir -pv "$appRoot"/"$contentHome"


	[ -e "$webRoot"/"$appApiPathCl" ] ||
	{
		sudo -p 'Pass required for creating web server directory: ' \
			mkdir -pv "$webRoot"/"$appApiPathCl" ||
		show_err_and_exit "Could not create ${webRoot}/${appApiPathCl}"
	}
}

process_global_vars() {
	process_global_args "$@" || return
	[ -z "$globalsSet" ] || return 0

	define_consts &&

	create_install_dir &&

	workspaceAbsPath=$(get_repo_path) &&
	#put export on separate line so it doesn't turn a failure in the previous
	#line into a success code
	export workspaceAbsPath &&

	define_top_level_terms &&

	define_app_dir_paths &&

	define_web_server_paths &&

	__define_url__ &&

	define_repo_paths &&

	#python environment names
	export pyEnv='mc_env' &&

	setup_base_dirs &&

	export globalsSet='globals'
}

unset_globals() {
	unset APT_CONST
	unset HOMEBREW_CONST
	unset PACMAN_CONST
	unset RADIO_AUTH_SECRET_KEY
	unset REACT_APP_API_VERSION
	unset REACT_APP_BASE_ADDRESS
	unset apiPort
	unset apiSrc
	unset appApiPathCl
	unset appClientPathCl
	unset appName
	unset appRoot
	unset appRoot_0
	unset appTrunk
	unset binDir
	unset buildDir
	unset client_src
	unset config_dir
	unset constants_set
	unset contentHome
	unset currentUser
	unset dbName
	unset db_dir
	unset default_radio_repo_path
	unset full_url
	unset globalsSet
	unset icecastConfLocation
	unset ices_configs_dir
	unset lib_name
	unset lib_src
	unset projName
	unset pyModules_dir
	unset pyEnv
	unset reference_src
	unset reference_src_db
	unset searchBase
	unset server_name
	unset sqlite_trunk_filepath
	unset srcPath
	unset stationConfigDir
	unset stationModuleDir
	unset templateDir
	unset templates_dir_cl
	unset templates_src
	unset test_root
	unset utest_env_dir
	unset webRoot
}

fn_ls() (
	process_global_vars "$@" >/dev/null
	perl -ne 'print "$1\n" if /^([a-zA-Z_0-9]+)\(\)/' \
		"$workspaceAbsPath"/radio_common.sh | sort
)

test_shell() (
	#put functions to test in here so they don't pollute your shell
	install_py_env test
)