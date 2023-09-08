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
	printenv > "$app_root"/used_env_vars
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
	if perl -e "exit 1 if index('$PATH','${app_root}/${bin_dir}') != -1"; then
		echo "Please add '${app_root}/${bin_dir}' to path"
		export PATH="$PATH":"$app_root"/"$bin_dir"
	fi
}


__export_py_env_vars__() {
	pkgMgrChoice=$(get_pkg_mgr) &&
	icecastName=$(get_icecast_name "$pkgMgrChoice") &&
	export searchBase="$app_root"/"$content_home" &&
	export dbName="$app_root"/"$sqlite_trunk_filepath" &&
	export templateDir="$app_root"/"$templates_dir_cl" &&
	export icecastConfLocation=$(get_icecast_conf "$icecastName") &&
	export stationConfigDir="$app_root"/"$ices_configs_dir" &&
	export stationModuleDir="$app_root"/"$pyModules_dir"
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
	pkgMgrChoice="$1"
	case "$pkgMgrChoice" in
    ("$PACMAN_CONST") echo 'icecast';;
    ("$APT_CONST") echo 'icecast2';;
    (*) echo 'icecast2';;
	esac
)

get_pb_api_key() (
	perl -ne 'print "$1\n" if /pb_api_key=(\w+)/' "$app_root"/keys/"$proj_name"
)

get_pb_secret() (
	perl -ne 'print "$1\n" if /pb_secret=(\w+)/' "$app_root"/keys/"$proj_name"
)

get_s3_api_key() (
	perl -ne 'print "$1\n" if /s3_api_key=(\w+)/' "$app_root"/keys/"$proj_name"
)

get_s3_secret() (
	perl -ne 'print "$1\n" if /s3_secret=(\w+)/' "$app_root"/keys/"$proj_name"
)

get_s3_secret() (
	perl -ne 'print "$1\n" if /s3_secret=(\w+)/' "$app_root"/keys/"$proj_name"
)

get_mc_auth_key() (
	perl -ne 'print "$1\n" if /mc_auth_key=(\w+)/' "$app_root"/keys/"$proj_name"
)

get_address() (
	keyFile="$app_root"/keys/"$proj_name"
	perl -ne 'print "$1\n" if /address6=root@([\w:]+)/' "$keyFile"
)

get_id_file() (
	keyFile="$app_root"/keys/"$proj_name"
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
	echo "/etc/ssl/private/${proj_name}.private.key.pem"
)

__get_remote_public_key__() (
	echo "/etc/ssl/certs/${proj_name}.public.key.pem"
)

__get_remote_intermediate_key__() (
	echo "/etc/ssl/certs/${proj_name}.intermediate.key.pem"
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
	fusermount -u "$app_root"/"$content_home"
}

link_to_music_files() {
	echo 'linking music files'
	process_global_vars "$@" &&
	if [ ! -e "$app_root"/"$content_home"/Soundtrack ]; then
		if [ -e "$HOME"/.passwd-s3fs ]; then
			s3fs "$(s3_name)" "$app_root"/"$content_home"/ \
				-o connect_timeout=10 -o retries=2 -o dbglevel=info -o curldbg
			[ -e "$app_root"/"$content_home"/Soundtrack ]
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
	packagePath="$py_env/lib/python$pyMajor.$pyMinor/site-packages/"
	echo "$env_root"/"$packagePath"
)

# set up the python environment, then copy
# subshell () auto switches in use python version back at the end of function
create_py_env_in_dir() (
	echo "setting up py libs"
	__set_env_path_var__ #ensure that we can see mc-python
	set_python_version_const || return "$?"
	env_root="$1"
	pyEnvDir="$env_root"/"$py_env"
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
	python -m pip install -r "$app_root"/"$app_trunk"/requirements.txt &&
	echo "done setting up py libs"
)

create_py_env_in_app_trunk() (
	process_global_vars "$@" &&
	sync_requirement_list &&
	create_py_env_in_dir "$app_root"/"$app_trunk" &&
	copy_dir "$lib_src" \
		"$(get_libs_dir "$app_root"/"$app_trunk")""$lib_name"
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
	dir_to_empty="$1"
	if [ -w "$dir_to_empty" ]; then
		rm -rf "$dir_to_empty"/*
	else
		sudo -p "Password required for removing files from ${dir_to_empty}: " \
			rm -rf "$dir_to_empty"/*
	fi
)

rm_contents_if_exist() (
	dir_to_empty="$1"
	if ! is_dir_empty "$dir_to_empty"; then
		sudo_rm_contents "$dir_to_empty"
	fi
)

sudo_rm_dir() (
	dir_to_empty="$1"
	if [ -w "$dir_to_empty" ]; then
		rm -rf "$dir_to_empty"
	else
		sudo -p "Password required to remove ${dir_to_empty}: " \
			rm -rf "$dir_to_empty"
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
	dir_to_make="$1"
	mkdir -pv "$dir_to_make" ||
	sudo -p "Password required for creating ${dir_to_make}: " \
		mkdir -pv "$dir_to_make"
)

unroot_dir() (
	unrooted_dir="$1"
	if [ ! -w "$unrooted_dir" ]; then
		sudo -p \
			"Password required to change owner of ${unrooted_dir} to current user: " \
			chown -R "$current_user": "$unrooted_dir"
	fi
)

empty_dir_contents() (
	dir_to_empty="$1"
	echo "emptying '${dir_to_empty}'"
	error_check_path "$dir_to_empty" &&
	if [ -e "$dir_to_empty" ]; then
		rm_contents_if_exist || return "$?"
	else
		sudo_mkdir "$dir_to_empty" || return "$?"
	fi &&
	unroot_dir "$dir_to_empty" &&
	echo "done emptying '${dir_to_empty}'"
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
	envFile="$app_root"/"$config_dir"/.env
	error_check_all_paths "$templates_src"/.env_api "$envFile" &&
	pkgMgrChoice=$(get_pkg_mgr) &&
	icecastName=$(get_icecast_name "$pkgMgrChoice") &&
	cp "$templates_src"/.env_api "$envFile" &&
	does_file_exist "$envFile" &&
	perl -pi -e "s@^(searchBase=).*\$@\1'${app_root}/${content_home}'@" \
		"$envFile" &&
	perl -pi -e "s@^(dbName=).*\$@\1'${app_root}/${sqlite_trunk_filepath}'@" \
		"$envFile" &&
	perl -pi -e "s@^(templateDir=).*\$@\1'${app_root}/${templates_dir_cl}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(stationConfigDir=).*\$@\1'${app_root}/${ices_configs_dir}'@" \
		"$envFile" &&
	perl -pi -e \
		"s@^(stationModuleDir=).*\$@\1'${app_root}/${pyModules_dir}'@" \
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
		"$app_root"/"$sqlite_trunk_filepath"  &&
	if [ ! -e "$app_root"/"$sqlite_trunk_filepath" ] || [ -n "$clean_flag" ] \
	|| [ -n "$replace_db_flag" ]; then
		cp -v "$reference_src_db" "$app_root"/"$sqlite_trunk_filepath" &&
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
			kill_process_using_port "$api_port"
		fi
	fi

	__export_py_env_vars__ &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
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

__install_py_env__() {
	sync_requirement_list &&
	create_py_env_in_app_trunk
}

install_py_env() {
	process_global_vars "$@" &&
	__install_py_env__
}

__install_py_env_if_needed__() {
	if [ ! -e "$app_root"/"$app_trunk"/"$py_env"/bin/activate ]; then
		__install_py_env__
	fi
}

print_schema_scripts() (
	process_global_vars "$@" &&
	__install_py_env_if_needed__ &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
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
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
	printf '\033c' &&
	python
)

sync_utility_scripts() (
	process_global_vars "$@" &&
	cp "$workspace_abs_path"/radio_common.sh "$app_root"/radio_common.sh
)

#copy python dependency file to the deployment directory
sync_requirement_list() (
	process_global_vars "$@" &&
	error_check_all_paths "$workspace_abs_path"/requirements.txt \
		"$app_root"/"$app_trunk"/requirements.txt "$app_root"/requirements.txt &&
	#keep a copy in the parent radio directory
	cp "$workspace_abs_path"/requirements.txt \
		"$app_root"/"$app_trunk"/requirements.txt &&
	cp "$workspace_abs_path"/requirements.txt "$app_root"/requirements.txt
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

__get_keychain_osx__() (
	echo '/Library/Keychains/System.keychain'
)

__get_debug_cert_path__() (
	echo $(get_localhost_key_dir)/"$proj_name"_localhost_debug
)

__get_local_nginx_cert_path__() (
	echo $(get_localhost_key_dir)/"$proj_name"_localhost_nginx
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
	__clean_up_invalid_cert__ "${app_name}-localhost"
	__setup_ssl_cert_local__ "${app_name}-localhost" 'localhost' \
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
				__certs_matching_name_osx__ "${app_name}-localhost" \
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
		perl -pi -e "s@<app_client_path_cl>@${web_root}/${app_client_path_cl}@" \
		"$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<server_name>@${server_name}@g" "$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<api_port>@${api_port}@" "$appConfFile"
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
	echo "$confDir"/"$app_name".conf
)

print_cert_paths() (
	process_global_vars "$@" >/dev/null &&
	confDirInclude=$(get_nginx_conf_dir_include) &&
	confDir=$(get_abs_path_from_nginx_include "$confDirInclude") 2>/dev/null
	cat "$confDir"/"$app_name".conf | perl -ne \
	'print "$1\n" if /ssl_certificate ([^;]+)/'
	cat "$confDir"/"$app_name".conf | perl -ne \
	'print "$1\n" if /ssl_certificate_key ([^;]+)/'
	cat "$confDir"/"$app_name".conf | perl -ne \
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
	update_nginx_conf "$confDir"/"$app_name".conf &&
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
	process_global_vars "$@" &&
	__set_env_path_var__ &&
	if ! mc-ices -V 2>/dev/null || ! is_ices_version_good \
	|| [ -n "$ice_branch" ]; then
		shutdown_all_stations &&
		folderPath="$app_root"/"$build_dir"/"$proj_name"/compiled_dependencies
		sh "$folderPath"/build_ices.sh "$ice_branch"
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
			echo "$templates_src"/icecast.xml
			;;
		*) ;;
	esac
)

show_icecast_log() (
	process_global_vars "$@" &&
	__export_py_env_vars__ &&
	__install_py_env_if_needed__ &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
	printf '\033c' &&
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
	for conf in "$app_root"/"$ices_configs_dir"/*.conf; do
		[ ! -s "$conf" ] && continue
		perl -pi -e "s/>\w*/>${sourcePassword}/ if /Password/" "$conf"
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
	sudo -p "restaring ${icecastName}" systemctl restart "$icecastName" &&
	echo "done setting up icecast/ices"
)


run_song_scan() (
	process_global_vars "$@"
	link_to_music_files &&
	setup_radio &&
	__export_py_env_vars__ &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&

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
	inserted = songScanner.save_paths('${app_root}/${content_home}')
	print(f"saving paths done: {inserted} inserted")
	updated = songScanner.update_metadata('${app_root}/${content_home}')
	print(f"updating songs done: {updated}")
	EOF
)

shutdown_all_stations() (
	process_global_vars "$@" &&
	#gonna assume that the environment has been setup because if
	#the environment hasn't been setup yet then no radio stations
	#are running
	if [ ! -s "$app_root"/"$app_trunk"/"$py_env"/bin/activate ]; then
		echo "python env not setup, so no stations to shut down"
		return
	fi
	__export_py_env_vars__ &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
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
	pkgMgrChoice=$(get_pkg_mgr) &&
	icecastName=$(get_icecast_name "$pkgMgrChoice") &&
	link_to_music_files &&
	setup_radio &&
	export searchBase="$app_root"/"$content_home" &&
	__export_py_env_vars__ &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
	for conf in "$app_root"/"$ices_configs_dir"/*.conf; do
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
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
	# see #python_env
	#put uvicorn in background with in a subshell so that it doesn't put
	#the whole chain in the background, and then block due to some of the
	#preceeding comands still having stdout open
	(uvicorn --app-dir "$web_root"/"$app_api_path_cl" --root-path /api/v1 \
	--host 0.0.0.0 --port "$api_port" \
	"index:app" </dev/null >api.out 2>&1 &)
	echo "done starting up api. Access at $full_url"
)


startup_nginx_for_debug() (
	process_global_vars "$@" &&
	export api_port='8032'
	setup_nginx_confs &&
	restart_nginx
)

setup_api() (
	echo "setting up api"
	process_global_vars "$@" &&
	kill_process_using_port "$api_port" &&
	sync_utility_scripts &&
	sync_requirement_list &&
	copy_dir "$templates_src" "$app_root"/"$templates_dir_cl" &&
	copy_dir "$api_src" "$web_root"/"$app_api_path_cl" &&
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
	error_check_all_paths "$client_src"  "$web_root"/"$app_client_path_cl" &&
	#in theory, this should be sourced by .bashrc
	#but sometimes there's an interactive check that ends the sourcing early
	if [ -z "$NVM_DIR" ]; then
		export NVM_DIR="$HOME"/.nvm
		[ -s "$NVM_DIR"/nvm.sh ] && \. "$NVM_DIR"/nvm.sh  # This loads nvm
	fi &&
	#check if web application folder exists, clear out if it does,
	#delete otherwise
	empty_dir_contents "$web_root"/"$app_client_path_cl" &&

	export REACT_APP_API_VERSION=v1 &&
	export REACT_APP_BASE_ADDRESS="$full_url" &&
	#set up react then copy
	#install packages
	npm --prefix "$client_src" i &&
	#build code (transpile it)
	npm run --prefix "$client_src" build &&
	#copy built code to new location
	sudo -p 'Pass required for copying client files: ' \
		cp -rv "$client_src"/build/. "$web_root"/"$app_client_path_cl" &&
	unroot_dir "$web_root"/"$app_client_path_cl" &&
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
	copy_dir "$templates_src" "$app_root"/"$templates_dir_cl" &&
	replace_db_file_if_needed2 &&
	pkgMgrChoice=$(get_pkg_mgr) &&
	icecastName=$(get_icecast_name "$pkgMgrChoice") &&
	setup_icecast_confs "$icecastName" &&
	echo "done setting up radio"
)

__create_fake_keys_file__() {
	echo "mc_auth_key=$(openssl rand -hex 32)" > "$app_root"/keys/"$proj_name"
}


#assume install_setup.sh has been run
setup_unit_test_env() (
	echo "setting up test environment"
	process_global_vars "$@" &&
	export app_root="$test_root"

	__create_fake_keys_file__
	setup_common_dirs

	copy_dir "$templates_src" "$app_root"/"$templates_dir_cl" &&
	error_check_all_paths "$reference_src_db" \
		"$app_root"/"$sqlite_trunk_filepath" &&
	sync_requirement_list
	setup_env_api_file
	pyEnvPath="$app_root"/"$app_trunk"/"$py_env"
	#redirect stderr into stdout so that missing env will also trigger redeploy
	srcChanges=$(find "$lib_src" -newer "$pyEnvPath" 2>&1)
	if [ -n "$srcChanges" ] || \
	[ "$workspace_abs_path"/requirements.txt -nt "$pyEnvPath" ]
	then
		echo "changes?"
		create_py_env_in_app_trunk
	fi
	replace_db_file_if_needed2 &&
	echo "$app_root"/"$config_dir"/.env &&
	echo "PYTHONPATH='${src_path}:${src_path}/api'" \
		>> "$app_root"/"$config_dir"/.env &&
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
	export app_root="$test_root"
	setup_unit_test_env &&
	test_src="$src_path"/tests &&
	__export_py_env_vars__ &&
	export PYTHONPATH="${src_path}:${src_path}/api" &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
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
	global_args=''
	while [ ! -z "$1" ]; do
		case "$1" in
			#build out to test_trash rather than the normal directories
			#sets app_root and web_root without having to set them explicitly
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
			(app_root=*)
				export app_root=${1#app_root=}
				global_args="${global_args} app_root='${app_root}'"
				;;
			(web_root=*)
				export web_root=${1#web_root=}
				global_args="${global_args} web_root='${web_root}'"
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
			(mc_branch=*)
				export mc_branch=${1#mc_branch=}
				global_args="${global_args} mc_branch='${mc_branch}'"
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
	export current_user=$(whoami)
	export proj_name='musical_chairs'
	export build_dir='builds'
	export content_home='music/radio'
	export bin_dir='.local/bin'
	export api_port='8033'
	#done't try to change from home
	export default_radio_repo_path="$HOME"/"$build_dir"/"$proj_name"
	export constants_set='true'
	echo "constants defined"
}

create_install_dir() {
	[ -d "$(get_repo_path)" ] ||
	mkdir -pv "$(get_repo_path)"

}

define_top_level_terms() {
	app_root=${app_root:-"$HOME"}
	export test_root="$workspace_abs_path/test_trash"


	if [ -n "$test_flag" ]; then
		app_root="$test_root"
		web_root="$test_root"
	fi

	sqlite_filename='songs_db.sqlite'
	export app_trunk="$proj_name"_dir
	export app_root="$app_root"
	export web_root="$web_root"


	export lib_name="$proj_name"_libs
	export app_name="$proj_name"_app

	echo "top level terms defined"
}

define_app_dir_paths() {
	export ices_configs_dir="$app_trunk"/ices_configs
	export pyModules_dir="$app_trunk"/pyModules

	export config_dir="$app_trunk"/config
	export db_dir="$app_trunk"/db
	export sqlite_trunk_filepath="$db_dir"/"$sqlite_filename"
	export utest_env_dir="$test_root"/utest

	# directories that should be cleaned upon changes
	# suffixed with 'cl' for 'clean'
	export templates_dir_cl="$app_trunk"/templates

	echo "app dir paths defined and created"
}

define_web_server_paths() {
	case $(uname) in
		(Linux*)
			export web_root=${web_root:-/srv}
			;;
		(Darwin*)
			export web_root=${web_root:-/Library/WebServer}
			;;
		(*) ;;
	esac

	export app_api_path_cl=api/"$app_name"
	export app_client_path_cl=client/"$app_name"

	echo "web server paths defined"
}

__get_url_base__() (
	echo "$proj_name" | tr -d _
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
	export src_path="$workspace_abs_path/src"
	export api_src="$src_path/api"
	export client_src="$src_path/client"
	export lib_src="$src_path/$lib_name"
	export templates_src="$workspace_abs_path/templates"
	export reference_src="$workspace_abs_path/reference"
	export reference_src_db="$reference_src/$sqlite_filename"
	echo "source paths defined"
}

setup_common_dirs() {
	[ -e "$app_root"/"$config_dir" ] ||
	mkdir -pv "$app_root"/"$config_dir"
	[ -e "$app_root"/"$ices_configs_dir" ] ||
	mkdir -pv "$app_root"/"$ices_configs_dir"
	[ -e "$app_root"/"$pyModules_dir" ] ||
	mkdir -pv "$app_root"/"$pyModules_dir"
	[ -e "$app_root"/"$db_dir" ] ||
	mkdir -pv "$app_root"/"$db_dir"
	[ -e "$app_root"/keys ] ||
	mkdir -pv "$app_root"/keys
}

setup_base_dirs() {

	[ -e "$app_root"/"$app_trunk" ] ||
	mkdir -pv "$app_root"/"$app_trunk"

	setup_common_dirs

	[ -e "$app_root"/"$content_home" ] ||
	mkdir -pv "$app_root"/"$content_home"


	[ -e "$web_root"/"$app_api_path_cl" ] ||
	{
		sudo -p 'Pass required for creating web server directory: ' \
			mkdir -pv "$web_root"/"$app_api_path_cl" ||
		show_err_and_exit "Could not create ${web_root}/${app_api_path_cl}"
	}
}

process_global_vars() {
	process_global_args "$@" || return
	[ -z "$globals_set" ] || return 0

	define_consts &&

	create_install_dir &&

	workspace_abs_path=$(get_repo_path) &&
	#put export on separate line so it doesn't turn a failure in the previous
	#line into a success code
	export workspace_abs_path &&

	define_top_level_terms &&

	define_app_dir_paths &&

	define_web_server_paths &&

	__define_url__ &&

	define_repo_paths &&

	#python environment names
	export py_env='mc_env' &&

	setup_base_dirs &&

	export globals_set='globals'
}

fn_ls() (
	process_global_vars "$@" >/dev/null
	perl -ne 'print "$1\n" if /^([a-zA-Z_0-9]+)\(\)/' \
		"$workspace_abs_path"/radio_common.sh | sort
)

