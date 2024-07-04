#!/bin/sh

if [ -e ./mc_dev_ops.sh ]; then
. ./mc_dev_ops.sh
elif [ -e ../mc_dev_ops.sh ]; then
. ../mc_dev_ops.sh
elif [ -e "$HOME"/radio/mc_dev_ops.sh ]; then
. "$HOME"/radio/mc_dev_ops.sh
else
  echo "mc_dev_ops.sh not found"
  exit 1
fi

#we have this as a seperate script so I can easily run it without being tangled
#with the rest



set_env_vars "$@"
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
icesBuildDir="$(__get_app_root__)"/"$MC_BUILD_DIR"/ices
(
	namePrefix='mc-'
	sudo_rm_dir "$icesBuildDir"
	cd "$(__get_app_root__)"/"$MC_BUILD_DIR"
	git clone https://github.com/joelliusczar/ices0.git ices
	cd ices
	if [ -n "$__ICES_BRANCH__" ]; then
		echo "Using branch ${__ICES_BRANCH__}"
		git checkout -t origin/"$__ICES_BRANCH__" || exit 1
	fi
	aclocal &&
	autoreconf -fi &&
	automake --add-missing &&
	./configure --prefix="$(__get_app_root__)"/.local \
		--with-python=$(which mc-python) \
		--with-moddir="$(__get_app_root__)"/"$MC_PY_MODULE_DIR" \
		--program-prefix="$namePrefix" &&
	make &&
	make install &&
	cd "$(__get_app_root__)"/"$MC_BUILD_DIR" &&
	if ! str_contains "$__SKIP__" 'clean'; then
		sudo_rm_dir "$icesBuildDir"
	fi
)