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


pkgMgrChoice=$(get_pkg_mgr)

[ -n "$pkgMgrChoice " ] || show_err_and_exit "No package manager set"

curl -V || show_err_and_exit "curl is somehow not installed"


case $(uname) in
	(Linux*) 
		if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
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

if perl -e "exit 1 if index('$PATH','${app_root}/${bin_dir}') != -1"; then
	echo "Please add '${app_root}/${bin_dir}' to path"
	export PATH="$PATH":"$app_root"/"$bin_dir"
fi


if ! mc-python -V 2>/dev/null || ! is_python_sufficient_version; then
	pythonToLink='python3'
	case $(uname) in
		(Linux*) 
			if ! python3 -V 2>/dev/null; then
				install_package python3
			fi
			#unbuntu only installs up to 3.8.10 which has a mysterious bug
			if ! is_python_sufficient_version; then
				sh ./compiled_dependencies/build_separate_python.sh &&
				pythonToLink='python3.9'
			fi
			;;
		(Darwin*)
			if ! brew_is_installed python3; then
				install_package python3
			fi
			;;
		(*) ;;
	esac &&
	ln -sf $(get_bin_path "$pythonToLink") "$app_root"/"$bin_dir"/mc-python
fi || show_err_and_exit "python install failed"


if ! mc-python -m pip -V 2>/dev/null; then
	curl https://bootstrap.pypa.io/pip/get-pip.py | mc-python /dev/stdin
fi

mc-python -m pip install --upgrade pip

if ! mc-python -m  virtualenv --version 2>/dev/null; then
	mc-python -m pip install --user virtualenv
fi

if ! nvm --version 2>/dev/null; then
	case $(uname) in
		(Linux*)
			rc_script="$HOME"/.bashrc
			;;
		(Darwin*)
			rc_script="$HOME"/.zshrc
			;;
		(*) ;;
	esac
	touch "$rc_script" #create if doesn't exist
	[ -f "$rc_script" ] || 
	show_err_and_exit "Error: .bashrc is not a regular file"
	curl -o- \
		https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
	export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
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

if ! aclocal --version 2>/dev/null; then
	install_package automake
fi


case $(uname) in
	(Darwin*)
		if ! brew_is_installed libtool; then
			install_package libtool 
		fi
		if ! brew_is_installed pkg-config; then
			install_package pkg-config
		fi
		if ! brew_is_installed libshout; then
			install_package libshout 
		fi
		;;
	(Linux*) 
		if [ "$pkgMgrChoice" = "$APT_CONST" ] \
		&& ! libtool --version 2>/dev/null; then
			install_package libtool-bin
		fi
		;;
	(*) ;;
esac

#leave this here incase the python check above did update the python version
set_python_version_const

if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
	if ! dpkg -s libxml2-dev >/dev/null 2>&1; then
		install_package libxml2-dev
	fi &&
	if ! dpkg -s libogg-dev >/dev/null 2>&1; then
		install_package libogg-dev
	fi &&
	if ! dpkg -s libvorbis-dev >/dev/null 2>&1; then
		install_package libvorbis-dev
	fi &&
	if ! dpkg -s libshout3-dev >/dev/null 2>&1; then
		install_package libshout3-dev
	fi &&
	if ! dpkg -s libmp3lame-dev >/dev/null 2>&1; then
		install_package libmp3lame-dev
	fi &&
	if ! dpkg -s libflac-dev >/dev/null 2>&1; then
		install_package libflac-dev
	fi &&
	if ! dpkg -s libfaad-dev >/dev/null 2>&1; then
		install_package libfaad-dev
	fi &&
	if ! dpkg -s libperl-dev >/dev/null 2>&1; then
		install_package libperl-dev
	fi &&
	if ! dpkg -s python3-distutils >/dev/null 2>&1; then
		install_package python3-distutils
	fi
	if ! dpkg -s python"$pyMajor"."$pyMinor"-dev >/dev/null 2>&1; then
		install_package python"$pyMajor"."$pyMinor"-dev
	fi #continue even if python3.x-dev is not found bc if we compiled python,
	#it may not actually exist
fi


if [ ! -e "$app_trunk" ]; then
	mkdir -pv "$app_trunk"
fi

case $(uname) in
	(Linux*)
		if [ "$pkgMgrChoice" = "$PACMAN_CONST" ]; then
			if ! icecast -v 2>/dev/null; then
				yes 'no' | install_package icecast
			fi
		elif [ "$pkgMgrChoice" = "$APT_CONST" ]; then
			if ! icecast2 -v 2>/dev/null; then
				install_package icecast2
			fi
		fi
		;;
	(*) ;;
esac



if ! mc-ices -V 2>/dev/null; then
	sh ./compiled_dependencies/build_ices.sh
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
echo "Checking for $confDir/$app_name.conf"
if [ ! -e "$confDir/$app_name.conf" ]; then
	setup_nginx_confs &&
	sudo -p 'copy nginx config' \
		cp "$templates_src"/nginx_evil.conf "$confDir"/nginx_evil.conf
fi
