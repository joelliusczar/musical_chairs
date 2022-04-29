#!/bin/sh

if [ -e ./radio_common.sh ]; then
	. ./radio_common.sh
elif [ -e ../radio_common.sh ]; then
	. ../radio_common.sh
elif [ -e "$HOME"/radio/radio_common.sh ]; then
	. "$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

pkgMgrChoice=$(get_pkg_mgr)

[ -n "$pkgMgrChoice" ] ||
echo "No package manager set"

perl -v >/dev/null 2>&1 ||
echo "Perl is not installed"

[ -e "$app_root"/"$bin_dir" ] || 
echo "${app_root}/${bin_dir} does not exist"

case $(uname) in
	Darwin*)
		brew --version >/dev/null 2>&1 ||
		echo "Homebrew is not installed"
		;;
	*) ;;
esac

mc-python -V >/dev/null  2>&1 ||
echo "mc-python is not installed"

mc-python -m pip -V >/dev/null  2>&1||
echo "pip is not installed"

mc-python -m  virtualenv --version >/dev/null 2>&1 ||
echo "virtualenv is not installed"

if [ -z "$NVM_DIR" ]; then
  export NVM_DIR="$HOME"/.nvm
  [ -s "$NVM_DIR"/nvm.sh ] && \. "$NVM_DIR"/nvm.sh  >/dev/null 2>&1
fi

nvm --version >/dev/null 2>&1 ||
echo "nvm not available"

nvm run node --version >/dev/null 2>&1 ||
echo "no version of node present"

case $(uname) in
	Linux*)
		s3fs --version >/dev/null 2>&1 ||
		echo "ns3fs is not installed"
		;;
esac

git --version >/dev/null 2>&1 ||
echo "git is not installed"

aclocal --version >/dev/null 2>&1 ||
echo "aclocal is not installed"

case $(uname) in
	Darwin*)
		brew_is_installed libtool >/dev/null 2>&1 ||
		echo "libtool is not installed"
		brew_is_installed pkg-config >/dev/null 2>&1 ||
		echo "pkg-config is not installed"
		brew_is_installed libshout >/dev/null 2>&1 ||
		echo "libshout is not installed"
		;;
	Linux*) 
		if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
			libtool --version >/dev/null >/dev/null 2>&1 ||
			echo "libtool is not installed"
		fi
		;;
	*) ;;
esac

set_python_version_const >/dev/null 2>&1

[ -n "$pyVersion" ]||
echo "pyVersion is not set"
[ -n "$pyMajor" ] ||
echo "pyMajor is not set"
[ -n "$pyMinor" ] ||
echo "pyMinor is not set"

if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
	dpkg -s libxml2-dev >/dev/null 2>&1 ||
	echo "libxml2-dev is not installed"
	dpkg -s libogg-dev >/dev/null 2>&1 ||
	echo "libogg-dev is not installed"
	dpkg -s libvorbis-dev >/dev/null 2>&1 ||
	echo "libvorbis-dev is not installed"
	dpkg -s libshout3-dev >/dev/null 2>&1 ||
	echo "libshout3-dev is not installed"
	dpkg -s libmp3lame-dev >/dev/null 2>&1 ||
	echo "libmp3lame-dev is not installed"
	dpkg -s libflac-dev >/dev/null 2>&1 ||
	echo "libflac-dev is not installed"
	dpkg -s libfaad-dev >/dev/null 2>&1 ||
	echo "libfaad-dev is not installed"
	dpkg -s python"$pyMajor"."$pyMinor"-dev >/dev/null 2>&1 ||
	echo "python"$pyMajor"."$pyMinor"-dev is not installed"
	dpkg -s libperl-dev >/dev/null 2>&1 ||
	echo "libperl-dev is not installed"
	dpkg -s python3-distutils >/dev/null 2>&1 ||
	echo "python3-distutils is not installed"
fi

[ -e "$app_root"/"$build_home" ] ||
echo "${app_root}/${build_home} does not exist"

[ -e "$app_trunk" ] ||
echo "${app_trunk} does not exist"

case $(uname) in
	Linux*)
		if [ "$pkgMgrChoice" = "$PACMAN_CONST" ]; then
			icecast -v >/dev/null 2>&1 ||
			echo "$icecast is not installed"
		elif [ "$pkgMgrChoice" = "$APT_CONST" ]; then
			icecast2 -v >/dev/null 2>&1 ||
			echo "$icecast2 is not installed"
		fi
		;;
	*) ;;
esac

mc-ices -V >/dev/null 2>&1 ||
echo "mc-ices is not installed"

[ -e "$app_root"/"$sqlite_file" ] ||
echo "${app_root}/${sqlite_file} does not exist"

[ -e "$app_trunk"/radio_common.sh ] ||
echo "radio_common.sh is not in place"
[ -e "$app_trunk"/icecast_check.sh ] ||
echo "icecast_check.sh is not in place"
[ -e "$app_trunk"/requirements.txt ] ||
echo "requirements.txt is not in place"

[ -e "$app_root"/"$maintenance_dir_cl" ] ||
echo "${app_root}/${maintenance_dir_cl} is not in place"


compare_dirs "$maintenance_src" "$app_root"/"$maintenance_dir_cl"

[ -e "$app_root"/"$maintenance_dir_cl/$py_env" ] ||
echo "${app_root}/${maintenance_dir_cl}/${py_env} is not in place"

compare_dirs "$templates_src" "$app_root"/"$templates_dir_cl"
compare_dirs "$start_up_src" "$app_root"/"$start_up_dir_cl"
compare_dirs "$api_src" "$web_root"/"$app_api_path_cl"

[ -e "$web_root"/"$app_api_path_cl/$py_env" ] ||
echo "${web_root}/${app_api_path_cl}/${py_env} is not in place"
compare_dirs "$client_src"/build \
 "$web_root"/"$app_client_path_cl"


[ -e "$app_root"/"$sqlite_file" ] || 
echo "${app_root}/${sqlite_file} is not in place"

nginx -v 2>/dev/null || 
echo "nginx is not installed"

confDir=$(get_nginx_conf_dir_abs_path)

[ -e "$confDir"/"$app_name".conf ] || 
echo "ngnix config not found"

[ -e "$confDir"/nginx_evil/.conf" ] || 
echo "ngnix evil config not found"
echo "done"