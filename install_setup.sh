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


printenv > "$app_root"/used_env_vars

export pkgMgrChoice=$(get_pkg_mgr)

[ -n "$pkgMgrChoice" ] || show_err_and_exit "No package manager set"

curl -V || show_err_and_exit "curl is somehow not installed"


case $(uname) in
	(Linux*) 
		if [ "$pkgMgrChoice" = "$APT_CONST" ] && [ "$exp_name" != 'py3.8' ]; then
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

[ ! -e "$app_root"/"$bin_dir" ] && mkdir -pv "$app_root"/"$bin_dir"

set_env_path_var

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
			if ! brew_is_installed python3; then 
				install_package python3
			fi
			;;
		(*) ;;
	esac &&
	ln -sf $(get_bin_path "$pythonToLink") "$app_root"/"$bin_dir"/mc-python
fi || show_err_and_exit "python install failed"

mc-python -V 2>/dev/null || show_err_and_exit "mc-python not available"

if ! mc-python -m pip -V 2>/dev/null; then
	mc-python -c "$(curl -fsSL https://bootstrap.pypa.io/pip/get-pip.py)" ||
	show_err_and_exit "Couldn't install pip"
fi

mc-python -m pip install --upgrade pip

if ! mc-python -m  virtualenv --version 2>/dev/null; then
	mc-python -m pip install --user virtualenv ||
	show_err_and_exit "Couldn't install virtualenv"
fi

if ! nvm --version 2>/dev/null; then
	rc_script=$(get_rc_candidate)
	touch "$rc_script" #create if doesn't exist
	[ -f "$rc_script" ] || 
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

if ! sqlite3 -version 2>/dev/null; then
	install_package sqlite3
fi

if ! git --version 2>/dev/null; then
	install_package git
fi


if [ ! -e "$app_root"/"$app_trunk" ]; then
	mkdir -pv "$app_root"/"$app_trunk"
fi

case $(uname) in
	(Linux*)
		if [ "$pkgMgrChoice" = "$PACMAN_CONST" ]; then
			if ! icecast -v 2>/dev/null; then
				yes 'no' | install_package icecast &&
				setup_icecast_confs icecast
			fi
		elif [ "$pkgMgrChoice" = "$APT_CONST" ]; then
			if ! icecast2 -v 2>/dev/null; then
				install_package icecast2 &&
				setup_icecast_confs icecast2
			fi
		fi
		;;
	(*) ;;
esac

if ! mc-ices -V 2>/dev/null; then
	sh ./compiled_dependencies/build_ices.sh ||
	show_err_and_exit "Couldn't install ices"
fi

if ! nginx -v 2>/dev/null; then
	case $(uname) in
		(Darwin*)
			install_package nginx 
			;;
		(Linux*) 
			if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
				install_package nginx-full
			fi
			;;
		(*) ;;
	esac
fi

confDir=$(get_nginx_conf_dir_abs_path)
echo "Checking for ${confDir}/${app_name}.conf"
if [ ! -e "$confDir"/"$app_name".conf ]; then
	setup_nginx_confs &&
	sudo -p 'copy nginx config' \
		cp "$templates_src"/nginx_evil.conf "$confDir"/nginx_evil.conf
fi

cp ./radio_common.sh "$app_root"/radio_common.sh
