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


set_pkg_mgr

[ -n "$pkgMgrChoice " ] || show_err_and_exit "No package manager set"

curl -V || show_err_and_exit "curl is somehow not installed"


case $(uname) in
	Linux*) 
		if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
			sudo apt-get update
		fi
		;;
	Darwin*)
		if ! brew --version 2>/dev/null; then
			#-f = -fail - fails quietly, i.e. no error page ...I think?
			#-s = -silent - don't show any sort of loading bar or such
			#-S = -show-error - idk
			#-L = -location - if page gets redirect, try again at new location
			/bin/bash -c "$(curl -fsSL \
				https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
		fi
		;;
	*) ;;
esac

if ! perl -v 2>/dev/null; then
	install_package perl
fi

[ ! -e "$bin_dir" ] && mkdir -pv "$bin_dir"

if perl -e "exit 1 if index('$PATH','$bin_dir') != -1"; then
	echo "Please add '$bin_dir' to path"
	export PATH="$PATH":"$bin_dir"
fi


if ! mc-python -V 2>/dev/null || ! is_python_sufficient_version; then
	pythonToLink='python3'
	case $(uname) in
		Linux*) 
			if ! python3 -V 2>/dev/null; then
				install_package python3
			fi
			#unbuntu only installs up to 3.8.10 which has a mysterious bug
			if ! is_python_sufficient_version; then
				if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
					if ! dpkg -s build-essential >/dev/null 2>&1; then
						install_package build-essential
					fi &&
					if ! dpkg -s zlib1g-dev >/dev/null 2>&1; then
						install_package zlib1g-dev
					fi &&
					if ! dpkg -s libncurses5-dev >/dev/null 2>&1; then
						install_package libncurses5-dev
					fi &&
					if ! dpkg -s libgdbm-dev >/dev/null 2>&1; then
						install_package libgdbm-dev
					fi &&
					if ! dpkg -s libnss3-dev >/dev/null 2>&1; then
						install_package libnss3-dev
					fi &&
					if ! dpkg -s libssl-dev >/dev/null 2>&1; then
						install_package libssl-dev
					fi &&
					if ! dpkg -s libreadline-dev >/dev/null 2>&1; then
						install_package libreadline-dev
					fi &&
					if ! dpkg -s libffi-dev >/dev/null 2>&1; then
						install_package libffi-dev
					fi &&
					if ! dpkg -s libsqlite3-dev >/dev/null 2>&1; then
						install_package libsqlite3-dev
					fi &&
					if ! dpkg -s wget >/dev/null 2>&1; then
						#not sure if this is actually needed or just the guide I
						#was reading was using it to download the tar file
						install_package wget
					fi &&
					if ! dpkg -s libbz2-dev >/dev/null 2>&1; then
						install_package libbz2-dev
					fi &&
					(
						python_build_dir="$build_home"/python
						empty_dir_contents "$python_build_dir"
						cd "$python_build_dir"
						verNum='3.9.1'
						curl -o Python-"$verNum".tgz \
							https://www.python.org/ftp/python/"$verNum"/Python-"$verNum".tgz
						tar -xf Python-"$verNum".tgz &&
						cd Python-"$verNum" &&
						./configure --enable-optimizations &&
						make &&
						sudo -p "install python3.9" make altinstall
					)
				fi &&
				pythonToLink='python3.9'
			fi
			;;
		Darwin*)
			if ! brew_is_installed python3; then
				install_package python3
			fi
			;;
		*) ;;
	esac &&
	ln -sf $(get_bin_path "$pythonToLink") "$bin_dir"/mc-python
fi || show_err_and_exit "python install failed"


if ! mc-python -m pip -V 2>/dev/null; then
	curl https://bootstrap.pypa.io/pip/get-pip.py | mc-python /dev/stdin
fi


if ! mc-python -m  virtualenv --version 2>/dev/null; then
	mc-python -m pip install --user virtualenv
fi

if ! npm version 2>/dev/null; then
	install_package npm
fi


case $(uname) in
	Linux*)
		if ! s3fs --version 2>/dev/null; then
			install_package s3fs
		fi
		;;
esac

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
	Darwin*)
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
	Linux*) 
		if [ "$pkgMgrChoice" = "$APT_CONST" ] \
		&& ! libtool --version 2>/dev/null; then
			install_package libtool-bin
		fi
		;;
	*) ;;
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
	if ! dpkg -s python"$pyMajor"."$pyMinor"-dev >/dev/null 2>&1; then
		install_package python"$pyMajor"."$pyMinor"-dev
	fi &&
	if ! dpkg -s libperl-dev >/dev/null 2>&1; then
		install_package libperl-dev
	fi &&
	if ! dpkg -s python3-distutils >/dev/null 2>&1; then
		install_package python3-distutils
	fi
fi


if ! [ -e "$radio_home" ]; then
	mkdir -pv "$radio_home"
fi

case $(uname) in
	Linux*)
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
	*) ;;
esac



if ! mc-ices -V 2>/dev/null; then
	sh ./build_ices.sh
fi


if ! nginx -v 2>/dev/null; then
	case $(uname) in
		Darwin*)
			install_package nginx 
			;;
		Linux*) 
			if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
				install_package nginx-full
			fi
			;;
		*) ;;
	esac &&
	setup_nginx_confs &&
	confDir=$(get_nginx_conf_dir_abs_path) &&
	sudo -p 'copy nginx config' \
		cp "$templates_src"/nginx_evil.conf "$confDir"/nginx_evil.com
fi

