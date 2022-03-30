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



[ -n "$pkgMgr" ] ||
	error_list="$error_list\nNo package manager set"

perl -v >/dev/null 2>&1 ||
	error_list="$error_list\nPerl is not installed"

[ -e "$bin_dir" ] || 
	error_list="$error_list\n$bin_dir does not exist"

case $(uname) in
	Darwin*)
		brew --version >/dev/null 2>&1 ||
			error_list="$error_list\nHomebrew is not installed"
		;;
	*) ;;
esac

mc-python -V >/dev/null  2>&1 ||
	error_list="$error_list\nmc-python is not installed"

mc-python -m pip -V >/dev/null  2>&1||
	error_list="$error_list\npip is not installed"

mc-python -m  virtualenv --version >/dev/null 2>&1 ||
	error_list="$error_list\nvirtualenv is not installed"

case $(uname) in
	Linux*)
		s3fs --version >/dev/null 2>&1 ||
			error_list="$error_list\\ns3fs is not installed"
		;;
esac

git --version >/dev/null 2>&1 ||
	error_list="$error_list\ngit is not installed"

aclocal --version >/dev/null 2>&1 ||
	error_list="$error_list\naclocal is not installed"

case $(uname) in
	Darwin*)
		brew_is_installed libtool >/dev/null 2>&1 ||
			error_list="$error_list\nlibtool is not installed"
		brew_is_installed pkg-config >/dev/null 2>&1 ||
			error_list="$error_list\npkg-config is not installed"
		brew_is_installed libshout >/dev/null 2>&1 ||
			error_list="$error_list\nlibshout is not installed"
		;;
	Linux*) 
		if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
			libtool --version >/dev/null 2>&1>/dev/null 2>&1 ||
				error_list="$error_list\nlibtool is not installed"
		fi
		;;
	*) ;;
esac

set_python_version_const >/dev/null 2>&1

[ -n "$pyVersion" ]||
	error_list="$error_list\npyVersion is not set"
[ -n "$pyMajor" ]||
	error_list="$error_list\npyMajor is not set"
[ -n "$pyMinor" ]||
	error_list="$error_list\npyMinor is not set"

if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
	dpkg -s libxml2-dev >/dev/null 2>&1 ||
		error_list="$error_list\nlibxml2-dev is not installed"
	dpkg -s libogg-dev >/dev/null 2>&1 ||
		error_list="$error_list\nlibogg-dev is not installed"
	dpkg -s libvorbis-dev >/dev/null 2>&1 ||
		error_list="$error_list\nlibvorbis-dev is not installed"
	dpkg -s libshout3-dev >/dev/null 2>&1 ||
		error_list="$error_list\nlibshout3-dev is not installed"
	dpkg -s libmp3lame-dev >/dev/null 2>&1 ||
		error_list="$error_list\nlibmp3lame-dev is not installed"
	dpkg -s libflac-dev >/dev/null 2>&1 ||
		error_list="$error_list\nlibflac-dev is not installed"
	dpkg -s libfaad-dev >/dev/null 2>&1 ||
		error_list="$error_list\nlibfaad-dev is not installed"
	dpkg -s python"$pyMajor"."$pyMinor"-dev >/dev/null 2>&1 ||
		error_list="$error_list\npython"$pyMajor"."$pyMinor"-dev is not installed"
	dpkg -s libperl-dev >/dev/null 2>&1 ||
		error_list="$error_list\nlibperl-dev is not installed"
	dpkg -s python3-distutils >/dev/null 2>&1 ||
		error_list="$error_list\npython3-distutils is not installed"
fi

[ -e "$build_home" ] ||
	error_list="$error_list\n$build_home does not exist"

[ -e "$radio_home" ] ||
	error_list="$error_list\n$radio_home does not exist"

case $(uname) in
	Linux*)
		if [ "$pkgMgrChoice" = "$PACMAN_CONST" ]; then
			icecast -v >/dev/null 2>&1 ||
				error_list="$error_list\n$icecast is not installed"
		elif [ "$pkgMgrChoice" = "$APT_CONST" ]; then
			icecast2 -v >/dev/null 2>&1 ||
				error_list="$error_list\n$icecast2 is not installed"
		fi
		;;
	*) ;;
esac

mc-ices -V >/dev/null 2>&1 ||
	error_list="$error_list\nmc-ices is not installed"

[ -e "$sqlite_file" ] ||
	error_list="$error_list\n$sqlite_file does not exist"

[ -e "$radio_home"/radio_common.sh ] ||
	error_list="$error_list\nradio_common.sh is not in place"
[ -e "$radio_home"/icecast_check.sh ] ||
	error_list="$error_list\nicecast_check.sh is not in place"
[ -e "$radio_home"/requirements.txt ] ||
	error_list="$error_list\nrequirements.txt is not in place"

[ -e "$maintenance_dir_cl" ] ||
	error_list="$error_list\n$maintenance_dir_cl is not in place"


compare_dirs() (
	local src_dir="$1"
	local cpy_dir="$2"

	if [ ! -e "$cpy_dir" ]; then
		echo "$cpy_dir/ is not in place" 
		return 1
	fi
	mkfifo src_fifo cpy_fifo cmp_fifo

	src_res=$(find "$src_dir" | \
		sed "s@${src_dir%/}/\{0,1\}@@" | sort) 
	cpy_res=$(find "$cpy_dir" -not -path "$cpy_dir/$py_env/*" \
		-and -not -path "$cpy_dir/$py_env" | \
		sed "s@${cpy_dir%/}/\{0,1\}@@" | sort)

	get_file_list() {
		local supress="$1"
		echo "$src_res" > src_fifo &
		echo "$cpy_res" > cpy_fifo &
		[ -n "$supress" ] && comm "-$supress" src_fifo cpy_fifo ||
			comm src_fifo cpy_fifo
	}

	in_both=$(get_file_list 12)
	in_src=$(get_file_list 23)
	in_cpy=$(get_file_list 13)
	[ -n "$in_cpy" ] && echo "There are items that only exist in copy"
	[ -n "$in_src" ] && echo "There are items missing from the copy"

	if [ -n "$in_both" ]; then
		echo "$in_both" > cmp_fifo &
		while read file_name; do
			[ "${src_dir%/}/$file_name" -nt "${cpy_dir%/}/$file_name" ] &&
				echo "$file_name is outdated"
		done <cmp_fifo
	fi
	rm -f src_fifo cpy_fifo cmp_fifo
)

error_list="$error_list\n$(compare_dirs './maintenance' "$maintenance_dir_cl")"

[ -e "$maintenance_dir_cl/$py_env" ] ||
	error_list="$error_list\n$maintenance_dir_cl/$py_env is not in place"

error_list="$error_list\n$(compare_dirs './templates' "$templates_dir_cl")"
error_list="$error_list\n$(compare_dirs './start_up' "$start_up_dir_cl")"
error_list="$error_list\n$(compare_dirs "$api_src" "$app_path_cl")"
[ -e "$app_path_cl/$py_env" ] ||
	error_list="$error_list\n$app_path_cl/$py_env is not in place"
error_list="$error_list\n$(compare_dirs "$client_src"/build \
 "$app_path_client_cl")"

echo "done"