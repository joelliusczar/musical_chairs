#!/bin/sh
echo "top of install script"
if [ -e ./mc_dev_ops.sh ]; then
	. ./mc_dev_ops.sh
elif [ -e ../mc_dev_ops.sh ]; then
	. ../mc_dev_ops.sh
else
  echo "mc_dev_ops.sh not found"
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
			#-s = -silent - don\'t show any sort of loading bar or such
			#-S = -show-error - idk
			#-L = -location - if page gets redirect, try again at new location
			/bin/bash -c "$(curl -fsSL \
				https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
		fi
		;;
	(*) ;;
esac

echo '##### perl #####'
if ! perl -v 2>/dev/null; then
	install_package perl
fi

[ ! -e "$(__get_app_root__)"/"$MC_BIN_DIR" ] &&
	mkdir -pv "$(__get_app_root__)"/"$MC_BIN_DIR"

set_env_vars || {
	#not using show_err_and_exit at this point because its existence is suspect
	echo "set_env_path_var error"
	exit 1
}

output_env_vars

echo '##### python #####'
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
		"$(__get_app_root__)"/"$MC_BIN_DIR"/mc-python
fi || show_err_and_exit "python install failed"

mc-python -V >/dev/null 2>&1 || show_err_and_exit "mc-python not available"

echo '##### python pip #####'
if ! mc-python -m pip -V 2>/dev/null; then
	if [ "$pkgMgrChoice" = "$MC_APT_CONST" ]; then
		install_package python3-pip
	else
		curl -o "$(__get_app_root__)"/"$MC_BUILD_DIR"/get-pip.py \
			https://bootstrap.pypa.io/pip/get-pip.py &&
		mc-python "$(__get_app_root__)"/"$MC_BUILD_DIR"/get-pip.py 
	fi ||
	show_err_and_exit "Couldn't install pip"
fi

if [ "$pkgMgrChoice" != "$MC_APT_CONST" ]; then
	mc-python -m pip install --upgrade pip
fi

echo '##### pythpn virtualenv #####'
if ! mc-python -m  virtualenv --version 2>/dev/null; then
	if [ "$pkgMgrChoice" = "$MC_APT_CONST" ]; then
		install_package virtualenv
	else
		mc-python -m pip install --user virtualenv
	fi ||
	show_err_and_exit "Couldn't install virtualenv"
fi

echo '##### nvm #####'
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

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

echo '##### node #####'
if ! nvm run node --version 2>/dev/null; then
	nvm install node
fi

echo '##### mariadb #####'
if ! mariadb -V 2>/dev/null; then
	if [ -n "$MC_DB_PASS_SETUP" ]; then
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
		sudo -p 'Updating db root password' mysql -u root -e \
			"REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'mysql'@'localhost'" &&
		sudo -p 'Updating db root password' mysql -u root -e \
			"SET PASSWORD FOR root@localhost = PASSWORD('${MC_DB_PASS_SETUP}');"
	else
		show_err_and_exit 'Need a password for root db account to install database'
	fi
fi

echo '##### sqlite3 #####'
if ! sqlite3 -version 2>/dev/null; then
	install_package sqlite3
fi

echo '##### git #####'
if ! git --version 2>/dev/null; then
	install_package git
fi

echo '##### icecast #####'
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

echo '##### ices #####'
install_ices || show_err_and_exit "Couldn't install ices"

echo '##### openssl #####'
case $(uname) in
	(Linux*)
		if [ "$pkgMgrChoice" = "$MC_APT_CONST" ]; then
			if ! openssl version 2>/dev/null; then
				install_package openssl
			fi
		fi
		;;
	(*) ;;
esac

echo '##### ca certificates #####'
case $(uname) in
	(Linux*)
		if [ "$pkgMgrChoice" = "$MC_APT_CONST" ]; then
			if ! dpkg -s ca-certificates 2>/dev/null; then
				install_package ca-certificates
			fi
		fi
		;;
	(*) ;;
esac

echo '##### nginx #####'
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

echo '##### ngnix additional setup #####'
confDir=$(get_nginx_conf_dir_abs_path)
echo "Checking for ${confDir}/${MC_APP_NAME}.conf"
if [ ! -e "$confDir"/"$MC_APP_NAME".conf ]; then
	setup_nginx_confs &&
	sudo -p 'copy nginx config' \
		cp "$MC_TEMPLATES_SRC"/nginx_evil.conf "$confDir"/nginx_evil.conf
fi

echo '##### leftovers #####'
sync_utility_scripts

if [ ! -e "$HOME"/keys/"$MC_PROJ_NAME" ]; then
	echo "MC_AUTH_SECRET_KEY=${APP_AUTH_KEY}" > "$HOME"/keys/"$MC_PROJ_NAME"
	echo "PB_SECRET=${PB_SECRET}" >> "$HOME"/keys/"$MC_PROJ_NAME"
	echo "PB_API_KEY=${PB_API_KEY}" >> "$HOME"/keys/"$MC_PROJ_NAME"
fi


output_env_vars

