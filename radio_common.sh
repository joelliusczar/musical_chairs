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

set_env_path_var() {
	if perl -e "exit 1 if index('$PATH','${app_root}/${bin_dir}') != -1"; then
		echo "Please add '${app_root}/${bin_dir}' to path"
		export PATH="$PATH":"$app_root"/"$bin_dir"
	fi
}

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

is_python_version_good() {
	[ "$exp_name" = 'py3.8' ] && return 0
	set_python_version_const &&
	[ "$pyMajor" -eq 3 ] && [ "$pyMinor" -ge 9 ]
}

is_ices_version_good() {
	set_ices_version_const &&
	[ "$icesMajor" -ge 0 ] && [ "$icesMinor" -ge 5 ]
}

is_dir_empty() (
	target_dir="$1"
	[ ! -d "$target_dir" ] || [ -z "$(ls -A ${target_dir})" ]
)

# set up the python environment, then copy
# subshell () auto switches in use python version back at the end of function
create_py_env_in() (
	echo "setting up py libs"
	set_python_version_const || return "$?"
	set_env_path_var #ensure that we can see mc-python
	dest_base="$1"
	env_name=${2:-"$py_env"}
	packagePath="$env_name/lib/python$pyMajor.$pyMinor/site-packages/"
	dest="$dest_base"/"$packagePath""$lib_name"/
	error_check_path "$dest_base"/"$env_name" &&
	mc-python -m virtualenv "$dest_base"/"$env_name" &&
	. "$dest_base"/$env_name/bin/activate &&
	#this is to make some of my newer than checks work
	touch "$dest_base"/$env_name &&
	# #python_env
	# use regular python command rather mc-python
	# because mc-python still points to the homebrew location
	python -m pip install -r "$app_root"/"$app_trunk"/requirements.txt &&
	setup_dir "$lib_src" "$dest" &&
	echo "done setting up py libs"
)

error_check_path() (
	target_dir="$1"
	if echo "$target_dir" | grep '\/\/'; then
		echo "segments seem to be missing in ${target_dir}"
		return 1
	elif [ "$target_dir" = '/' ];then
		echo "segments seem to be missing in ${target_dir}"
		return 1
	fi
)

empty_dir_contents() (
	dir_to_empty="$1"
	echo "emptying ${dir_to_empty}"
	error_check_path "$dir_to_empty" &&
	if [ -e "$dir_to_empty" ]; then
		if ! is_dir_empty "$dir_to_empty"; then
			sudo -p "Password required for removing files from ${dir_to_empty}: " \
				rm -rf "$dir_to_empty"/* || return "$?"
		fi
	else
		sudo -p "Password required for creating ${dir_to_empty}: " \
			mkdir -pv "$dir_to_empty" || return "$?"
	fi &&
	sudo -p \
		"Password required to change owner of ${dir_to_empty} to current user: " \
		chown -R "$current_user": "$dir_to_empty" &&
	echo "done emptying ${dir_to_empty}"
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
		procId=$(ss -lpn 'sport = :8032' | perl -ne 'print "$1\n" if /pid=(\d+)/')
		if [ -n "$procId" ]; then
			kill -15 "$procId"
		fi
	elif lsof -v >/dev/null 2>&1; then
		procId=$(sudo lsof -i :8032 | awk '{ print $2 }' | tail -n 1)
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
	error_check_path "$templates_src"/.env_api &&
	error_check_path "$envFile" &&
	cp "$templates_src"/.env_api "$envFile" &&
	does_file_exist "$envFile" &&
	perl -pi -e "s@^(searchBase=).*\$@\1'${app_root}/${content_home}'@" \
		"$envFile" &&
	does_file_exist "$envFile" &&
	perl -pi -e "s@^(dbName=).*\$@\1'${app_root}/${sqlite_file}'@" "$envFile" &&
	echo 'done setting up .env file'
)

setup_dir() (
	from_dir="$1"
	to_dir="$2"
	echo "setting up dir from ${from_dir} to ${to_dir}"
	error_check_path "$from_dir"/. &&
	error_check_path "$to_dir" &&
	empty_dir_contents "$to_dir" &&
	sudo -p 'Pass required for copying files: ' \
		cp -rv "$from_dir"/. "$to_dir" &&
	sudo -p 'Pass required for changing owner of maintenance files: ' \
		chown -R "$current_user": "$to_dir" &&
	echo "done setting up dir from ${from_dir} to ${to_dir}"
)

setup_db() (
	echo 'tentatively copying initial db'
	process_global_vars "$@" &&
	error_check_path "$reference_src_db" &&
	error_check_path "$app_root"/"$sqlite_file" &&
	if [ ! -e "$app_root"/"$sqlite_file" ]; then
		cp -v "$reference_src_db" "$app_root"/"$sqlite_file"
	else
		if [ -n "$(pgrep 'mc-ices')" ]; then
			shutdown_all_stations
		fi
		if [ -n "$(pgrep 'uvicorn')" ]; then
			kill_process_using_port "$api_port"
		fi
	fi

	export dbName="$app_root"/"$sqlite_file" &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
	python <<-EOF
	from musical_chairs_libs.tables import metadata
	from musical_chairs_libs.env_manager import EnvManager
	envManager = EnvManager()
	conn = envManager.get_configured_db_connection()
	metadata.create_all(conn.engine)

	print('Created all tables')
	EOF

	echo 'done with db stuff'
)

print_schema_scripts() (
	process_global_vars "$@" &&
	sync_requirement_list &&
	create_py_env_in "$app_root"/"$app_trunk" &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
	printf '\033c' &&
	(python <<-EOF
	from musical_chairs_libs.env_manager import EnvManager
	EnvManager.print_expected_schema()
	EOF
	)
)

sync_utility_scripts() (
	process_global_vars "$@" &&
	cp "$workspace_abs_path"/radio_common.sh "$app_root"/radio_common.sh
)

sync_requirement_list() (
	process_global_vars "$@" &&
	error_check_path "$workspace_abs_path"/requirements.txt &&
	error_check_path "$app_root"/"$app_trunk"/requirements.txt &&
	error_check_path "$app_root"/requirements.txt &&
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
	error_check_path "$src_dir"
	error_check_path "$cpy_dir"
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
	echo "updating nginx site conf"
	appConfFile="$1"
	error_check_path "$templates_src" &&
	error_check_path "$appConfFile" &&
	sudo -p 'copy nginx config' \
		cp "$templates_src"/nginx_template.conf "$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<app_client_path_cl>@${web_root}/${app_client_path_cl}@" \
		"$appConfFile" &&
	sudo -p "update ${appConfFile}" \
		perl -pi -e "s@<server_name>@${server_name}@" "$appConfFile" &&
	case "$app_env" in
		(local*)
			sudo -p "update ${appConfFile}" \
				perl -pi -e "s/<listen>/8080/" "$appConfFile"
			;;
		(*)
			sudo -p "update ${appConfFile}" \
				perl -pi -e "s/<listen>/[::]:80/" "$appConfFile"
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

setup_nginx_confs() (
	echo 'setting up nginx confs'
	process_global_vars "$@" &&
	confDirInclude=$(get_nginx_conf_dir_include) &&
	#remove trailing path chars
	confDir=$(get_abs_path_from_nginx_include "$confDirInclude") &&
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

get_icecast_conf() (
	icecastName="$1"
	case $(uname) in
		Linux*)
			if ! systemctl status "$icecastName" >/dev/null 2>&1; then
					echo "$icecastName is not running at the moment"
					exit 1
			fi
				systemctl status "$icecastName" | grep -A2 CGroup | \
					head -n2 | tail -n1 | awk '{ print $NF }'
			;;
		*) ;;
	esac
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

get_icecast_source_password() (
	icecastConfLocation="$1"
	sudo -S -p 'Pass required to read icecast config: ' \
		grep '<source-password>' "$icecastConfLocation" \
		| perl -ne 'print "$1\n" if />(\w+)/'
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

create_ices_config() (
	echo 'creating ices config'
	internalName="$1"
	publicName="$2"
	sourcePassword="$3"
	process_global_vars "$@" &&
	station_conf="$app_root"/"$ices_configs_dir"/ices."$internalName".conf
	error_check_path "$app_root"/"$templates_dir_cl"/ices.conf &&
	error_check_path "$station_conf" &&
	cp "$app_root"/"$templates_dir_cl"/ices.conf "$station_conf" &&
	perl -pi -e "s/icecast_password/$sourcePassword/ if /<Password>/" \
		"$station_conf" &&
	perl -pi -e "s/internal_station_name/$internalName/ if /<Module>/" \
		"$station_conf" &&
	perl -pi -e "s/public_station_name/$publicName/ if /<Name>/" \
		"$station_conf" &&
	perl -pi -e "s/internal_station_name/$internalName/ if /<Mountpoint>/" \
		"$station_conf" &&
	echo 'done creating ices config'
)

create_ices_py_module() (
	echo 'creating ices module'
	internalName="$1"
	process_global_vars "$@" &&
	station_module="$app_root"/"$pyModules_dir"/"$internalName".py &&
	error_check_path "$app_root"/"$templates_dir_cl"/template.py &&
	error_check_path "$station_module" &&
	cp "$app_root"/"$templates_dir_cl"/template.py "$station_module" &&
	perl -pi -e "s/<internal_station_name>/$internalName/" "$station_module" &&
	echo 'done creating ices module'
)

save_station_to_db() (
	internalName="$1"
	publicName="$2"
	# #python_env
	python <<EOF
	from musical_chairs_libs.station_service import StationService
	stationService = StationService()
	if stationService.add_station('${internalName}','${publicName}'):
		print('${internalName} added')
	else:
		print('${internalName} may already exist')
EOF
)

add_tags_to_station() (
	internalName="$1"
	while true; do
		read tagname
		[ -z "$tagname" ] && break
		# #python_env
		python <<EOF
			from musical_chairs_libs.station_service import StationService
			stationService = StationService()
			if stationService.assign_tag_to_station('${internalName}','${tagname}'):
				print('tag ${tagname} assigned to ${internalName}')
EOF

	done
)

create_new_station() (
	echo 'creating new station'
	process_global_vars "$@" &&
	setup_radio &&
	pkgMgrChoice=$(get_pkg_mgr) &&
	icecastName=$(get_icecast_name "$pkgMgrChoice") &&
	icecastConfLocation=$(get_icecast_conf "$icecastName") &&
	sourcePassword=$(get_icecast_source_password "$icecastConfLocation") &&
	echo 'Enter radio station public name or description:' &&
	read publicName &&

	echo 'Enter radio station internal name:' &&
	read internalName &&

	echo "public: $publicName" &&
	echo "internal: $internalName" &&

	create_ices_config "$internalName" "$publicName" "$sourcePassword" &&
	create_ices_py_module "$internalName" &&
	echo "skip_option: ${skip_option}"
	if [ "$skip_option" = 'save_station' ]; then
		echo "Not saving to db"
		return
	fi &&
	echo "Saving to db"
	export dbName="$app_root"/"$sqlite_file"
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
	save_station_to_db "$internalName" "$publicName" &&
	add_tags_to_station "$internalName" &&
	echo 'done creating new station'
)

run_song_scan() (
	process_global_vars "$@"
	link_to_music_files &&
	setup_radio &&
	export dbName="$app_root"/"$sqlite_file" &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
	# #python_env
	python  <<-EOF
	import os
	from musical_chairs_libs.song_scanner import SongScanner
	from musical_chairs_libs.env_manager import EnvManager
	print("Starting")
	shouldReplaceDb = os.environ.get("replace_db_flag", False) and True
	print(f"About to replace db? {shouldReplaceDb}")
	EnvManager.setup_db_if_missing(shouldReplaceDb, echo = True)
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
	export dbName="$app_root"/"$sqlite_file" &&
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
	set_env_path_var && #ensure that we can see mc-ices
	link_to_music_files &&
	setup_radio &&
	export searchBase="$app_root"/"$content_home" &&
	export dbName="$app_root"/"$sqlite_file" &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
	for conf in "$app_root"/"$ices_configs_dir"/*.conf; do
		[ ! -s "$conf" ] && continue
		mc-ices -c "$conf"
	done
)

startup_api() (
	process_global_vars "$@" &&
	setup_api &&
	export dbName="$app_root"/"$sqlite_file" &&
	. "$app_root"/"$app_trunk"/"$py_env"/bin/activate &&
	# see #python_env
	#put uvicorn in background with in a subshell so that it doesn't put
	#the whole chain in the background, and then block due to some of the
	#preceeding comands still having stdout open
	(uvicorn --app-dir "$web_root"/"$app_api_path_cl" --root-path /api/v1 \
	--host 0.0.0.0 --port "$api_port" "index:app" </dev/null >api.out 2>&1 &)
	echo "Done with api"
)

setup_api() (
	echo "setting up api"
	process_global_vars "$@" &&
	kill_process_using_port "$api_port" &&
	sync_requirement_list &&
	setup_dir "$api_src" "$web_root"/"$app_api_path_cl"
	create_py_env_in "$app_root"/"$app_trunk" &&
	setup_db &&
	setup_nginx_confs &&
	echo "done setting up api"
)

setup_client() (
	echo "setting up client"
	process_global_vars "$@" &&
	error_check_path "$client_src" &&
	error_check_path "$web_root"/"$app_client_path_cl" &&
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
	export REACT_APP_API_ADDRESS="$full_url"/api/"$REACT_APP_API_VERSION" &&
	#set up react then copy
	#install packages
	npm --prefix "$client_src" i &&
	#build code (transpile it)
	npm run --prefix "$client_src" build &&
	#copy built code to new location
	sudo -p 'Pass required for copying client files: ' \
		cp -rv "$client_src"/build/. "$web_root"/"$app_client_path_cl" &&
	sudo -p 'Pass required for changing owner of client files: ' \
		chown -R "$current_user": "$web_root"/"$app_client_path_cl" &&
	echo "done setting up client"
)

setup_full_web() (
	echo "setting up full web"
	process_global_vars "$@" &&
	setup_client &&
	setup_api &&
	echo "done setting up full web"
)

startup_full_web() (
	echo "starting up full web"
	process_global_vars "$@" &&
	setup_client &&
	setup_api &&
	echo "done starting up full web"
)

#assume install_setup.sh has been run
setup_radio() (
	echo "setting up radio"
	process_global_vars "$@" &&
	shutdown_all_stations &&
	sync_requirement_list &&

	create_py_env_in "$app_root"/"$app_trunk" &&

	setup_dir "$templates_src" "$app_root"/"$templates_dir_cl" &&
	setup_db &&
	pkgMgrChoice=$(get_pkg_mgr) &&
	icecastName=$(get_icecast_name "$pkgMgrChoice") &&
	setup_icecast_confs "$icecastName" &&
	echo "done setting up radio"
)

#assume install_setup.sh has been run
setup_unit_test_env() (
	echo "setting up test environment"
	process_global_vars "$@" &&
	export app_root="$test_root"
	[ -e "$app_root"/"$config_dir" ] ||
	mkdir -pv "$app_root"/"$config_dir" &&
	[ -e "$app_root"/"$db_dir" ] ||
	mkdir -pv "$app_root"/"$db_dir" &&
	error_check_path "$reference_src_db" &&
	error_check_path "$app_root"/"$sqlite_file" &&
	sync_requirement_list
	setup_env_api_file
	#redirect stderr into stdout missing env will also trigger redeploy
	srcChanges=$(find "$lib_src" -newer \
		"$utest_env_dir"/"$py_env" 2>&1)
	if [ -n "$srcChanges" ] || \
	[ "$app_root"/"$app_trunk"/requirements.txt -nt "$utest_env_dir"/"$py_env" ]
	then
		echo "changes?"
		create_py_env_in "$utest_env_dir"
	fi &&
	setup_db &&
	echo "PYTHONPATH='${src_path}:${src_path}/api'" \
		>> "$app_root"/"$config_dir"/.env &&

	cp -v "$reference_src_db" "$app_root"/"$sqlite_file" &&
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
	setup_unit_test_env &&

	test_src="$src_path"/tests &&

	export PYTHONPATH="${src_path}:${src_path}/api" &&
	export dbName="$test_root"/"$sqlite_file" &&
	export searchBase="$test_root"/"$content_home" &&

	. "$utest_env_dir"/"$py_env"/bin/activate &&
	pytest -s "$test_src" #leaving off the && for now
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
	while [ ! -z "$1" ]; do
		case "$1" in
			#build out to test_trash rather than the normal directories
			#sets app_root and web_root without having to set them explicitly
			(test)
				export test_flag='test'
				;;
			(replaceDb) #tells setup to replace sqlite3 db
				export replace_db_flag='true'
				;;
			#activates debug_print. Also tells deploy script to use the diag branch
			(diag)
				export diag_flag='true'
				echo '' > diag_out_"$include_count"
				;;
			(env=*) #affects which url to use
				export app_env=${1#env=}
				;;
			(app_root=*)
				export app_root=${1#app_root=}
				;;
			(web_root=*)
				export web_root=${1#web_root=}
				;;
			(setup_lvl=*) #affects which setup scripst to run
				export setup_lvl=${1#setup_lvl=}
				;;
			#when I want to conditionally run with some experimental code
			(experiment=*)
				export exp_name=${1#experiment=}
				;;
			(skip=*)
				export skip_option=${1#skip=}
				;;
			(*) ;;
		esac
		shift
	done
}

define_consts() {
	export PACMAN_CONST='pacman'
	export APT_CONST='apt-get'
	export HOMEBREW_CONST='homebrew'
	export current_user=$(whoami)
	export proj_name='musical_chairs'
	export build_dir='builds'
	export content_home='music/radio'
	export bin_dir='.local/bin'
	export api_port='8032'
	#done't try to change from home
	export default_radio_repo_path="$HOME"/"$build_dir"/"$proj_name"
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

	db_name='songs_db'
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
	export sqlite_file="$db_dir"/"$db_name"
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

define_url() {
	url_base=$(echo "$proj_name" | tr -d _)
	echo "env: ${app_env}"
	case "$app_env" in
		(local*)
			url_suffix='-local.radio.fm:8080'
			;;
		(*)
			url_suffix='.radio.fm'
			;;
	esac
	export server_name="${url_base}${url_suffix}"
	export full_url="http://${server_name}"
	echo "url defined"
}

define_repo_paths() {
	export src_path="$workspace_abs_path/src"
	export api_src="$src_path/api"
	export client_src="$src_path/client"
	export lib_src="$src_path/$lib_name"
	export templates_src="$workspace_abs_path/templates"
	export reference_src="$workspace_abs_path/reference"
	export reference_src_db="$reference_src/$db_name"
	echo "source paths defined"
}

setup_base_dirs() {

	[ -e "$app_root"/"$app_trunk" ] ||
	mkdir -pv "$app_root"/"$app_trunk"

	[ -e "$app_root"/"$ices_configs_dir" ] ||
	mkdir -pv "$app_root"/"$ices_configs_dir"
	[ -e "$app_root"/"$pyModules_dir" ] ||
	mkdir -pv "$app_root"/"$pyModules_dir"
	[ -e "$app_root"/"$content_home" ] ||
	mkdir -pv "$app_root"/"$content_home"
	[ -e "$app_root"/"$config_dir" ] ||
	mkdir -pv "$app_root"/"$config_dir"
	[ -e "$app_root"/"$db_dir" ] ||
	mkdir -pv "$app_root"/"$db_dir"

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

	define_url &&

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

