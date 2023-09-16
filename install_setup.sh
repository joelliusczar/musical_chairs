#!/bin/sh

if [ -e ./radio_common.sh ]; then
	. ./radio_common.sh
elif [ -e ../radio_common.sh]; then
	. ../radio_common.sh
elif [ -e "$HOME"/radio/radio_common.sh]; then
	. "$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

process_global_vars "$@"

output_env_vars


export pkgMgrChoice=$(get_pkg_mgr)

[ -n "$pkgMgrChoice" ] || show_err_and_exit "No package manager set"

curl -V || show_err_and_exit "curl is somehow not installed"



case $(uname) in
	(Linux*)
		if [ "$pkgMgrChoice" = "$MC_APT_CONST" ] && [ "$expName" != 'py3.8' ]; then
			sudo apt-get update
		fi
		;;
	(Darwin*)
		if ! brew --version 2>/dev/null; then
			#-f = -fail - fails quietly, i.e. no error page ...I think?
			#-s = -silent - don't show any sort of loading bar or such
			#-S = -show-error - idk
			#-L = -location - if page gets redirect, try again at new location
			/bin/bash -c "$(curl -fsSL \
				https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
		fi
		;;
	(*) ;;
esac

if ! perl -v 2>/dev/null; then
	install_package perl
fi

[ ! -e "$MC_APP_ROOT"/"$MC_BIN_DIR" ] && mkdir -pv "$MC_APP_ROOT"/"$MC_BIN_DIR"

set_env_path_var

output_env_vars


if ! mc-python -V 2>/dev/null || ! is_python_version_good; then
	pythonToLink='python3'
	case $(uname) in
		(Linux*)
			if ! python3 -V 2>/dev/null; then
				install_package python3
			fi
			if ! is_python_version_good; then
				install_package python3.9 &&
				pythonToLink='python3.9'
			fi
			;;
		(Darwin*)
			#want to install python thru homebrew bc the default version on mac
			#is below what we want
			if ! brew_is_installed python@3.9; then
				install_package python@3.9
			fi
			pythonToLink='python@3.9'
			;;
		(*) ;;
	esac &&
	ln -sf $(get_bin_path "$pythonToLink") \
		"$MC_APP_ROOT"/"$MC_BIN_DIR"/mc-python
fi || show_err_and_exit "python install failed"

mc-python -V >/dev/null 2>&1 || show_err_and_exit "mc-python not available"

if ! mc-python -m pip -V 2>/dev/null; then
	curl -o "$MC_APP_ROOT"/"$MC_BUILD_DIR"/get-pip.py \
		https://bootstrap.pypa.io/pip/get-pip.py &&
	mc-python "$MC_APP_ROOT"/"$MC_BUILD_DIR"/get-pip.py ||
	show_err_and_exit "Couldn't install pip"
fi

mc-python -m pip install --upgrade pip

if ! mc-python -m  virtualenv --version 2>/dev/null; then
	mc-python -m pip install --user virtualenv ||
	show_err_and_exit "Couldn't install virtualenv"
fi

if ! nvm --version 2>/dev/null; then
	rcScript=$(get_rc_candidate)
	touch "$rcScript" #create if doesn't exist
	[ -f "$rcScript" ] ||
	show_err_and_exit "Error: .bashrc is not a regular file"
	curl -o- \
		https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
	export NVM_DIR="$HOME"/.nvm
  [ -s "$NVM_DIR"/nvm.sh ] && \. "$NVM_DIR"/nvm.sh  # This loads nvm
fi

if ! nvm run node --version 2>/dev/null; then
	nvm install node
fi

if ! s3fs --version 2>/dev/null; then
	case $(uname) in
		(Linux*)
				install_package s3fs
			;;
	esac
fi

if [ ! -e "$HOME"/.vimrc ]; then
	touch "$HOME"/.vimrc
fi
perl -pi -e "s/set nonumber/set number/" "$HOME"/.vimrc
perl -pi -e "s/set expandtab/set noexpandtab/" "$HOME"/.vimrc
perl -pi -e "s/set tabstop=\d+/set tabstop=2/" "$HOME"/.vimrc
lineNum=$(perl -ne 'print "true" if /set number/' "$HOME"/.vimrc)
noexpandtabs=$(perl -ne 'print "true" if /set noexpandtab/' "$HOME"/.vimrc)
tabstop=$(perl -ne 'print "true" if /set tabstop=2/' "$HOME"/.vimrc)

if [ "$lineNum" != 'true'; ]; then
	echo 'set number' >> "$HOME"/.vimrc
fi
if [ "$noexpandtabs" != 'true'; ]; then
	echo 'set noexpandtab' >> "$HOME"/.vimrc
fi
if [ "$tabstop" != 'true'; ]; then
	echo 'set tabstop' >> "$HOME"/.vimrc
fi

if ! mariadb -V 2>/dev/null; then
	if [ -n "$dbPass" ]; then
		case $(uname) in
			(Linux*)
				if [ "$pkgMgrChoice" = "$MC_APT_CONST" ]; then
					install_package mariadb-server
				fi
				;;
			(Darwin*)
				install_package mariadb
				;;
			(*) ;;
		esac &&
		sudo -p 'Updating db root password' mysql -u root -e
			"REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'mysql'@'localhost'" &&
		sudo -p 'Updating db root password' mysql -u root -e \
			"SET PASSWORD FOR root@localhost = PASSWORD('${dbPass}');"
	else
		echo 'Need a password for root db account to install database'
	fi
fi

if ! sqlite3 -version 2>/dev/null; then
	install_package sqlite3
fi

if ! git --version 2>/dev/null; then
	install_package git
fi

case $(uname) in
	(Linux*)
		if [ "$pkgMgrChoice" = "$MC_PACMAN_CONST" ]; then
			if ! icecast -v 2>/dev/null; then
				yes 'no' | install_package icecast &&
				setup_icecast_confs icecast
			fi
		elif [ "$pkgMgrChoice" = "$MC_APT_CONST" ]; then
			if ! icecast2 -v 2>/dev/null; then
				install_package icecast2 &&
				setup_icecast_confs icecast2
			fi
		fi
		;;
	(*) ;;
esac

install_ices || show_err_and_exit "Couldn't install ices"

if ! nginx -v 2>/dev/null; then
	case $(uname) in
		(Darwin*)
			install_package nginx
			;;
		(Linux*)
			if [ "$pkgMgrChoice" = "$MC_APT_CONST" ]; then
				install_package nginx-full
			fi
			;;
		(*) ;;
	esac
fi

confDir=$(get_nginx_conf_dir_abs_path)
echo "Checking for ${confDir}/${MC_APP_NAME}.conf"
if [ ! -e "$confDir"/"$MC_APP_NAME".conf ]; then
	setup_nginx_confs &&
	sudo -p 'copy nginx config' \
		cp "$MC_TEMPLATES_SRC"/nginx_evil.conf "$confDir"/nginx_evil.conf
fi

sync_utility_scripts

echo "mc_auth_key=${APP_AUTH_KEY}" > "$HOME"/keys/"$MC_PROJ_NAME"
echo "pb_secret=${PB_SECRET}" >> "$HOME"/keys/"$MC_PROJ_NAME"
echo "pb_api_key=${PB_API_KEY}" >> "$HOME"/keys/"$MC_PROJ_NAME"

echo "$S3_ACCESS_KEY_ID":"$S3_SECRET_ACCESS_KEY" > "$HOME"/.passwd-s3fs
chmod 600 "$HOME"/.passwd-s3fs

output_env_vars

