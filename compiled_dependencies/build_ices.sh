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

#we have this as a seperate script so I can easily run it without being tangled
#with the rest



process_global_vars "$@"
set_env_path_var
#leave this here incase the python check in the global install script
#did update the python version
set_python_version_const

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
		if [ "$pkgMgrChoice" = "$MC_APT_CONST" ] \
		&& ! libtool --version 2>/dev/null; then
			install_package libtool-bin ||
			show_err_and_exit "Couldn't install libtool"
		fi &&
		if ! dpkg -s build-essential >/dev/null 2>&1; then
			install_package build-essential
		fi &&
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
		;;
	(*) ;;
esac

case $(uname) in
	Darwin*)
		PATH="/opt/homebrew/opt/libtool/libexec/gnubin:$PATH"
		;;
	*) ;;
esac
icesBuildDir="$MC_APP_ROOT"/"$MC_BUILD_DIR"/ices
(
	namePrefix='mc-'
	sudo_rm_dir "$icesBuildDir"
	cd "$MC_APP_ROOT"/"$MC_BUILD_DIR"
	git clone https://github.com/joelliusczar/ices0.git ices
	cd ices
	if [ -n "$__ICES_BRANCH__" ]; then
		echo "Using branch ${__ICES_BRANCH__}"
		git checkout -t origin/"$__ICES_BRANCH__" || exit 1
	fi
	aclocal &&
	autoreconf -fi &&
	automake --add-missing &&
	./configure --prefix="$MC_APP_ROOT"/.local \
		--with-python=$(which mc-python) \
		--with-moddir="$MC_APP_ROOT"/"$pyModules_dir" \
		--program-prefix="$namePrefix" &&
	make &&
	make install &&
	cd "$MC_APP_ROOT"/"$MC_BUILD_DIR" &&
	if [ "$skip_option" != clean ]; then
		sudo_rm_dir "$icesBuildDir"
	fi
)