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

if [ -z "$pkgMgr" ]; then
	echo "No package manager set"
	exit 1
fi

if ! perl -v 2>/dev/null; then
	eval "$pkgMrg" perl
fi

[ ! -e "$bin_dir" ] && mkdir -pv "$bin_dir"

if perl -e "exit 1 if index('$PATH','$bin_dir') != -1"; then
	echo "Please add '$bin_dir' to path"
	export PATH="$PATH":"$bin_dir"
fi

case $(uname) in
	Darwin*)
		if ! brew --version 2>/dev/null; then
			/bin/bash -c "$(curl -fsSL \
				https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
		fi
		;;
	*) ;;
esac

if ! mc-python -V 2>/dev/null; then
	case $(uname) in
		Linux*) 
			if ! python3 -V 2>/dev/null; then
				eval "$pkgMgr" python3
			fi
			;;
		Darwin*)
			if ! brew_is_installed python3; then
				eval "$pkgMgr" python3
			fi
			;;
		*) ;;
	esac
	ln -sf $(get_bin_path python3) "$bin_dir"/mc-python
fi


if ! mc-python -m pip -V 2>/dev/null; then
	curl https://bootstrap.pypa.io/pip/get-pip.py | mc-python /dev/stdin
fi


if ! mc-python -m  virtualenv --version 2>/dev/null; then
	mc-python -m pip install --user virtualenv
fi

if ! npm version 2>/dev/null; then
	eval "$pkgMgr" npm
fi


case $(uname) in
	Linux*)
		if ! s3fs --version 2>/dev/null; then
			eval "$pkgMgr" s3fs
		fi
		;;
esac

if ! sqlite3 -version 2>/dev/null; then
	eval "$pkgMgr" sqlite3
fi

if ! git --version 2>/dev/null; then
	eval "$pkgMgr" git
fi

if ! aclocal --version 2>/dev/null; then
	eval "$pkgMgr" automake
fi


case $(uname) in
	Darwin*)
		if ! brew_is_installed libtool; then
			eval "$pkgMgr" libtool 
		fi
		if ! brew_is_installed pkg-config; then
			eval "$pkgMgr" pkg-config
		fi
		if ! brew_is_installed libshout; then
			eval "$pkgMgr" libshout 
		fi
		;;
	Linux*) 
		if [ "$pkgMgrChoice" = "$APT_CONST" ] \
		&& ! libtool --version 2>/dev/null; then
			eval "$pkgMgr" libtool-bin
		fi
		;;
	*) ;;
esac

set_python_version_const

if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
	if ! dpkg -s libxml2-dev >/dev/null 2>&1; then
		eval "$pkgMgr" libxml2-dev
	fi
	if ! dpkg -s libogg-dev >/dev/null 2>&1; then
		eval "$pkgMgr" libogg-dev
	fi
	if ! dpkg -s libvorbis-dev >/dev/null 2>&1; then
		eval "$pkgMgr" libvorbis-dev
	fi
	if ! dpkg -s libshout3-dev >/dev/null 2>&1; then
		eval "$pkgMgr" libshout3-dev
	fi
	if ! dpkg -s libmp3lame-dev >/dev/null 2>&1; then
		eval "$pkgMgr" libmp3lame-dev
	fi
	if ! dpkg -s libflac-dev >/dev/null 2>&1; then
		eval "$pkgMgr" libflac-dev
	fi
	if ! dpkg -s libfaad-dev >/dev/null 2>&1; then
		eval "$pkgMgr" libfaad-dev
	fi
	if ! dpkg -s python"$pyMajor"."$pyMinor"-dev >/dev/null 2>&1; then
		eval "$pkgMgr" python"$pyMajor"."$pyMinor"-dev
	fi
	if ! dpkg -s libperl-dev >/dev/null 2>&1; then
		eval "$pkgMgr" libperl-dev
	fi
	if ! dpkg -s python3-distutils >/dev/null 2>&1; then
		eval "$pkgMgr" python3-distutils
	fi
fi


if ! [ -e "$radio_home" ]; then
	mkdir -pv "$radio_home"
fi

case $(uname) in
	Linux*)
		if [ "$pkgMgrChoice" = "$PACMAN_CONST" ]; then
			if ! icecast -v 2>/dev/null; then
				eval "$pkgMgr" icecast
			fi
		elif [ "$pkgMgrChoice" = "$APT_CONST" ]; then
			if ! icecast2 -v 2>/dev/null; then
				eval "$pkgMgr" icecast2
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
			eval "$pkgMgr" nginx 
			;;
		Linux*) 
			if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
				eval "$pkgMgr" nginx-full
			fi
			;;
		*) ;;
	esac
	update_nginx_conf
fi

